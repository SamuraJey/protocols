import json
import argparse
import logging
import socket
import struct
import sys
import asyncio
import time
from asyncio import Queue

MAX_CONNECTIONS = 1500
closed_ports = []
open_ports = []


def get_args():
    parser = argparse.ArgumentParser(description='Сканер портов TCP и UDP')
    parser.add_argument('host', type=str, help='IP адрес хоста')
    parser.add_argument('-t', '--tcp', action='store_true',
                        help='Сканировать TCP порты')
    parser.add_argument('-u', '--udp', action='store_true',
                        help='Сканировать UDP порты')
    parser.add_argument('-p', '--ports', nargs=2, type=int,
                        metavar=('N1', 'N2'), help='Диапазон портов для сканирования')

    return parser.parse_args()


def check_is_admin():
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.close()
        return True
    except PermissionError:
        return False


def check_icmp_code_is_3(data: bytes) -> bool:
    icmp_header = data[20:28]
    # Проверяем, является ли полученный пакет ICMP пакетом 'Port Unreachable'
    icmp_type, code, checksum, id, seq = struct.unpack(
        '!bbHHh', icmp_header)
    if icmp_type == 3 or code == 3:
        return True
    else:
        return False


async def tcp_scanner(port: int, host: str, well_known_ports: dict) -> None:
    try:

        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1)
        writer.write(b'kek\r\n\r\n')
        await writer.drain()
        data = await reader.read(1024)
        # if data:
        #     print(f'data: {data.decode()}')

        guessed_protocol = define_protocol(data)
        if guessed_protocol == 'Unknown':
            try:
                guessed_protocol = well_known_ports.get(str(port))
            except KeyError:
                guessed_protocol = 'Unknown'
        if not guessed_protocol:
            guessed_protocol = 'Unknown'
        print(f'TCP Open {port} protocol is {guessed_protocol}')
        open_ports.append(port)
        writer.close()
        await writer.wait_closed()
    except TimeoutError as expt:
        pass
        # print(
        #     f'Timeout Error while scanning port {port}. Port probably closed.')
        # closed_ports.append(port)
        pass
    except ConnectionRefusedError:
        # print(f'Connection refused while scanning port {port}.\
        #         Port probably closed.')
        closed_ports.append(port)
    except OSError as e:
        # Оно почему-то выкидывет какой-то OSError, но я не могу понять какой конкретно, пока так, потом мб пофиксим
        pass
        # print(f'Connection refused while scanning port {port}. Port probably closed.')
    except Exception as e:
        logging.error(f'Error while scanning port {port}.\
                       Exception description: {e} Exception type: {type(e)}')


async def udp_scanner(port: int, host: str, well_known_ports: dict) -> None:
    try:
        # Создаем raw socket для получения ICMP пакетов
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.bind(("", 0))
        sock.settimeout(1.5)
        

        # Создаем UDP-сокет для отправки пустых пакетов
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(1.5)

        # Отправляем UDP-пакет
        try:
            await asyncio.get_event_loop().sock_sendto(udp_sock, b'wdkomwokweokdwdewd', (host, port))
            print("udp send done")
        except Exception:
            print("error while sending udp packet")
        try:
            # Пытаемся получить ответ от сервера
            data, addr = await asyncio.get_event_loop().sock_recvfrom(sock, 1024)
            if check_icmp_code_is_3(data):
                pass
                # print(f'Port {port} is closed')
        except socket.timeout:
            # Если нет ответа, то отправляем еще один UDP-запрос
            try:
                await asyncio.get_event_loop().sock_sendto(udp_sock, b'wdkomwokweokdwdewd', (host, port))
                data, addr = await asyncio.get_event_loop().sock_recvfrom(sock, 1024)
                if check_icmp_code_is_3(data):
                    return
                    # print(f'Port {port} is closed')
            except socket.timeout:
                try:
                    print(
                        f'UDP Port {port} is probably open and probably belongs to {well_known_ports.get(str(port))}')
                except KeyError:
                    print(
                        f'UDP Port {port} is probably open, but application protocol is Unknown')
    except Exception as e:
        print(f'UDP Error scanning port {port}: {e}')


def define_protocol(data: bytes) -> str:
    protocol = 'Unknown'
    if b'SMTP' in data:
        protocol = 'SMTP'
    elif b'POP3' in data or b'+OK' in data or b'-ERR' in data or b'USER' in data\
            or b'PASS' in data or b'STAT' in data or b'LIST' in data \
            or b'RETR' in data or b'TOP' in data or b'QUIT' in data:
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


async def worker(queue: Queue, host: str, mode: str, well_known_ports: dict) -> None:
    while True:

        port = await queue.get()
        if mode.lower() == 'tcp':
            await tcp_scanner(int(port), host, well_known_ports)
        elif mode.lower() == 'udp':
            await udp_scanner(int(port), host, well_known_ports)

        queue.task_done()


async def main():
    with open('well_known_ports.json', 'r') as file:
        well_known_ports = json.load(file)

    args = get_args()
    start_port = args.ports[0]
    finish_port = args.ports[1]

    if start_port < 0 or start_port > 65535 or finish_port < 0 or finish_port > 65535:
        print('Неверный номер порта')
        sys.exit(1)

    if args.tcp:
        protocol = 'tcp'
    else:
        if not check_is_admin():
            print(f'We need root privelegies to scan UDP sockets')
            sys.exit(1)
        protocol = 'udp'

    host = args.host
    queue = Queue()
    for port in range(start_port, finish_port + 1):
        await queue.put(port)

    tasks = []
    for _ in range(MAX_CONNECTIONS):
        tasks.append(asyncio.create_task(
            worker(queue, host, protocol, well_known_ports)))

    await queue.join()  # Ожидание завершения всех задач в очереди

    for task in tasks:
        task.cancel()

    # Ожидание завершения всех задач
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    start_time = time.time()
    print('Starting')
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(
            f'Error while running main. Exception description: |{e}| Exception type: {type(e)}')
    end_time = time.time()

    print(f'Execution time: {(end_time - start_time):.2f} seconds')