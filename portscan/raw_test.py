import socket
import struct
import time

def scan_udp_port(host, port, timeout=3.0):
    """
    Сканирует UDP-порт на указанном хосте.
    
    Аргументы:
    host (str) -- IP-адрес или имя хоста
    port (int) -- номер порта
    timeout (float) -- таймаут ожидания ответа в секундах
    
    Возвращает:
    bool -- True, если порт открыт, False, если порт закрыт или недоступен
    """
    try:
        # Создаем raw-сокет для работы с ICMP-пакетами
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.settimeout(timeout)
        
        # Создаем UDP-сокет для отправки запросов
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(timeout)
        
        # Отправляем пустой UDP-пакет на указанный порт
        udp_sock.sendto(b'', (host, port))
        
        try:
            # Ожидаем ответа ICMP
            data, addr = sock.recvfrom(1024)
            print(addr)
            print(data)
            
            # Проверяем, является ли ответ ICMP 'Port Unreachable'
            icmp_header = data[20:28]
            type, code, checksum, id, seq = struct.unpack('!bbHHh', icmp_header)
            
            if type == 3 and code == 3:
                print(f'Port {port} is closed or unreachable')
                return False
        except socket.timeout:
            # Если не получили ответ ICMP в течение таймаута, значит порт открыт
            print(f'Port {port} is open')
            return True
    except:
        # Если возникла ошибка, считаем порт недоступным
        return False
    finally:
        # Закрываем сокеты
        sock.close()
        udp_sock.close()

scan_udp_port('scanme.nmap.org', 124)  # Сканируем UDP-порт 53 (DNS) на example.com