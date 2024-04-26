import socket
import struct

def scan_udp_port(host, port, timeout=3):
    """
    Сканирует UDP-порт на заданном хосте.
    
    Args:
        host (str): IP-адрес или доменное имя хоста.
        port (int): Номер UDP-порта для сканирования.
        timeout (float, optional): Время ожидания ответа в секундах. По умолчанию 1.0 секунда.
    
    Returns:
        bool: True, если порт открыт, False, если порт недоступен.
    """
    try:
        # Создание сырого сокета для обработки ICMP-ответов
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        raw_socket.settimeout(timeout)
        
        # Создание UDP-сокета для отправки пустого UDP-пакета
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.settimeout(timeout)
        
        # Отправка пустого UDP-пакета
        raw_socket.sendto(b'31231223131', (host, port))

        # Попытка получения ICMP-ответа
        try:
            data, addr = raw_socket.recvfrom(1024)
            icmp_header = data[20:28]
            type, code, checksum, id, seq = struct.unpack('bbHHh', icmp_header)
            print(data)
            # Если получен ICMP-ответ "Port Unreachable", значит порт недоступен
            if type == 3 and code == 3:
                print(f"Порт {port} недоступен")
                return False
        except socket.timeout:
            # Если ICMP-ответ не получен в течение таймаута, значит порт открыт
            print(f"Порт {port} открыт")
            return True
    except Exception as e:
        print(f"Ошибка при сканировании порта {port}: {e}")
    finally:
        udp_socket.close()
        raw_socket.close()

scan_udp_port("45.33.32.156", 1123)  # Сканирование UDP-порта 53 на example.com