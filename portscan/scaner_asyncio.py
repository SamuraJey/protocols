import sys
import socket
import asyncio
import time

async def tcp_scanner(port: int, host: str) -> None:
    writer = None
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1)
        writer.write(b'kek\r\n\r\n')
        await writer.drain()
        data = await reader.read(1024)
        if data:
            print(f'data: {data}')
        print(f'TCP Open {port} {define_protocol(data)}')
    finally:
        if writer is not None:
            writer.close()
            await writer.wait_closed()

async def udp_scanner(port: int, host: str) -> None:
    try:
        reader, writer = await asyncio.open_connection(host, port, proto=asyncio.DatagramProtocol)
        writer.write(b'kek')
        await writer.drain()
        data, _ = await reader.read(1024)
        if data:
            print(f'data: {data}')
        print(f'UDP Open {port} {define_protocol(data)}')
    finally:
        writer.close()
        await writer.wait_closed()

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

async def main():
    if len(sys.argv) == 5:
        start_port = int(sys.argv[1])
        finish_port = int(sys.argv[2])
        if start_port < 0 or start_port > 65535 or finish_port < 0 or finish_port > 65535:
            print('Неверный номер порта')
            sys.exit(-1)
        protocol = sys.argv[3]
        host = sys.argv[4]
        
        tasks = []
        if protocol == 'TCP':
            for port in range(start_port, finish_port + 1):
                tasks.append(tcp_scanner(port, host))
        elif protocol == 'UDP':
            for port in range(start_port, finish_port + 1):
                tasks.append(udp_scanner(port, host))
        else:
            print('Неправильный протокол')
            sys.exit(-1)
        
        await asyncio.gather(*tasks)
    else:
        print('Неправильный ввод аргументов')
        sys.exit(-1)

if __name__ == '__main__':
    start_time = time.time()
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    print(f'Execution time: {time.time() - start_time:.2f} seconds')