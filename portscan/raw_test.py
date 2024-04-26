import socket
import struct
import sys

def scan_udp_port(host, port):
    # Создаем raw сокет
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    # Устанавливаем таймаут для получения ответа
    raw_socket.settimeout(3)
    try:
        # Отправляем UDP пакет на указанный хост и порт
        raw_socket.sendto(b'', (host, port))

        # Получаем ответ
        data, addr = raw_socket.recvfrom(1024)
        print("data: ", data)
        # Парсим ICMP заголовок
        icmp_header = data[20:28]
        print(icmp_header)
        icmp_type, code, checksum, packet_id, sequence = struct.unpack("!BBHHH", icmp_header)
        
        # Проверяем тип ICMP пакета
        if icmp_type == 3 and code == 3:
            print(f"Порт {port} недоступен")
        else:
            print(f"Порт {port} открыт")
    except socket.timeout:
        print(data)
        print(f"Порт {port} открыт")
    
    # Закрываем сокет
    raw_socket.close()

# scan_udp_port("127.0.0.1", 1234)
# sys.exit(0)
# Пример использования
for i in range (1, 65535):
    scan_udp_port("scanme.nmap.org", i)