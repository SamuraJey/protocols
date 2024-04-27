import logging
import socket
import struct
import sys
import asyncio
import time
from asyncio import Queue
import asyncio_udp as asudp

MAX_CONNECTIONS = 1500 
closed_ports = []
open_ports = []
async def tcp_scanner(port: int, host: str) -> None:
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=0.5)
        writer.write(b'kek\r\n\r\n')
        # await writer.drain()
        data = await reader.read(1024)
        if data:
            print(f'data: {data.decode()}')
        print(f'TCP Open {port} {define_protocol(data)}')
        # open_ports.append(port)
        writer.close()
        await writer.wait_closed()
    except TimeoutError as expt:
        # logging.error(f'Timeout Error while scanning port {port}. Port probably closed.')
        # closed_ports.append(port)
        pass
    except Exception as e:
        logging.error(f'Error while scanning port {port}. Exception description: {e} Exception type: {type(e)}')


async def udp_scanner(port, host):
    try:
        # Создаем raw socket для получения ICMP пакетов
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.settimeout(2)

        # Создаем UDP-сокет для отправки пустых пакетов
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(2)

        # Отправляем пустой UDP-пакет
        await asyncio.get_event_loop().sock_sendto(udp_sock, b'wdkomwokweokdwdewd', (host, port))

        try:
            # Пытаемся получить ответ от сервера
            data, addr = await asyncio.get_event_loop().sock_recvfrom(sock, 1024)
            icmp_header = data[20:28]
            # Проверяем, является ли полученный пакет ICMP пакетом "Port Unreachable"
            icmp_type, code, checksum, id, seq = struct.unpack('!bbHHh', icmp_header)
            if icmp_type == 3 or code == 3:
                print(f"Port {port} is closed")
            else:
                print(f"Port {port} is open")
        except socket.timeout:
            # Если нет ответа, то порт открыт
            print(f"Port {port} is open")
    except Exception as e:
        print(f"Error scanning port123 {port}: {e}")

def define_protocol(data: bytes) -> str:
    protocol = 'Unknown'
    if b'SMTP' in data:
        protocol = 'SMTP'
    elif b'POP3' in data or b'+OK' in data or b'-ERR' in data or b'USER' in data or b'PASS' in data or b'STAT' in data or b'LIST' in data or b'RETR' in data or b'TOP' in data or b'DELE' in data or b'QUIT' in data:
        protocol = 'POP3'
    elif b'IMAP' in data or b'* OK' in data:
        protocol = 'IMAP'
    elif b'HTTP' in data or b'GET' in data:
        protocol = 'HTTP'
    elif b'NTP' in data:
        protocol = 'NTP'
    elif b'DNS' in data:
        protocol = 'DNS'
    elif b'SSH' in data:
        protocol = 'SSH'
    return protocol

async def worker(queue: Queue, host: str, mode: str) -> None:
    while True:
        port = await queue.get()
        # print(f"Starting scanning on host: {host} port: {port} ")
        if mode.lower() == 'tcp':
            await tcp_scanner(int(port), host)
        elif mode.lower() == 'udp':
            await udp_scanner(int(port), host)
        # await udp_scanner(int(port), host)
        queue.task_done()
        # print(f"Finished scanning on host: {host} port: {port} ")

async def main():
    if len(sys.argv) == 5:
        start_port = int(sys.argv[1])
        finish_port = int(sys.argv[2])
        if start_port < 0 or start_port > 65535 or finish_port < 0 or finish_port > 65535:
            print('Неверный номер порта')
            sys.exit(-1)
        protocol = sys.argv[3]
        host = sys.argv[4]
        
        queue = Queue()
        for port in range(start_port, finish_port + 1):
            await queue.put(port)
        
        tasks = []
        for _ in range(MAX_CONNECTIONS):
            tasks.append(asyncio.create_task(worker(queue, host, "udp")))
        
        await queue.join()  # Ожидание завершения всех задач в очереди
        
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)  # Ожидание завершения всех задач
    else:
        print('Неправильный ввод аргументов')
        sys.exit(-1)

if __name__ == '__main__':
    start_time = time.time()
    print('Starting')
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f'Error while running main. Exception description: |{e}| Exception type: {type(e)}')
    end_time = time.time()

    print(f'Execution time: {(end_time - start_time):.2f} seconds')