import socket
import struct
import sys

def scan_udp_port(host, port):
    # Создаем raw сокет
    dest_addr = socket.gethostbyname(host)
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 50
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
    send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    recv_socket.bind(("", port))
    send_socket.sendto(b"", (host, port))
    # Устанавливаем таймаут для получения ответа
    
    try:
        # Отправляем UDP пакет на указанный хост и порт
        data, curr_addr = recv_socket.recvfrom(1024)

        # Получаем ответ
        print("data: ", data)
        # Парсим ICMP заголовок
        icmp_header = data[20:28]
        
        icmp_type, code, checksum, packet_id, sequence = struct.unpack("!BBHHH", icmp_header)
        print(icmp_type)
        # Проверяем тип ICMP пакета
        if icmp_type == 3 and code == 3:
            print(f"Порт {port} недоступен")
        else:
            print(f"Порт {port} открыт")
    except socket.timeout:
        print(data)
        print(f"Порт {port} открыт")
    
    
    # Закрываем сокет
    send_socket.close()
    recv_socket.close()

# scan_udp_port("127.0.0.1", 1234)
# sys.exit(0)
# Пример использования
for i in range (1, 65535):
    scan_udp_port("scanme.nmap.org", i)