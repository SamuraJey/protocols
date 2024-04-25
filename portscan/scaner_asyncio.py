import logging
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


async def udp_scanner(port: int, host: str) -> None:
    try:
        # print(f"host: {host}, type of host: {type(host)}")
        # print(f"port: {port}, type of port: {type(port)}")
        remote = await asudp.open_remote_endpoint(host=host, port=port)
        remote.send(b'kek\r\n\r\n')
        data = await remote.receive()
        # try:
        #     reader, writer = await asyncio.open_connection(str(host), int(port), proto=asyncio.DatagramProtocol)
        # except Exception as e:
        #     logging.error(f'FIRSTrror while scanning port {port}. Exception description: {e} Exception type: {type(e)}')

        # writer.write(b'kek\r\n\r\n')
        # # await writer.drain()
        # data, _ = await reader.read(1024)
        if data:
            print(f'data: {data}')
        print(f'UDP Open {port} {define_protocol(data)}')
        remote.close()
    except Exception as e:
        logging.error(f'YDPError while scanning port {port}. Exception description: {e} Exception type: {type(e)}')

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

async def worker(queue: Queue, host: str) -> None:
    while True:
        port = await queue.get()

        # print(f"Starting scanning on host: {host} port: {port} ")
        
        # await tcp_scanner(int(port), host)
        await udp_scanner(int(port), host)
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
            tasks.append(asyncio.create_task(worker(queue, host)))
        
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