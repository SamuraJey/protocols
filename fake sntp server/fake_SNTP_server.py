#!/usr/bin/python

# Made by: Sergey Zaremba MO-201
import argparse
import threading
import time
import socket
import struct


class SNTP:
    """
    RFC 4330
    https://www.rfc-editor.org/rfc/inline-errata/rfc4330.html
    """

    """ 
    > - Означает что данные в формате big-endian
    B - 1 байт (unsigned char 8 bit)
    I - 4 байта (unsigned int 32 bit)
    Q - 8 байт (unsigned long long 64 bit)
    """
    UNIX_TIME_SHIFT = 2208988800
    BYTE_OFFSET = 2 ** 32
    _HEADER_FORMAT = '> B B B B I I I Q Q Q Q'
    _LEAP_INDICATOR = 0  # Нет предупреждений
    _VERSION_NUMBER = 4  # номер версии NTP/SNTP
    _MODE = 4  # 3 - клиент, 4 - сервер
    # насколько точное время у сервера 1 - самый точный (атомные часы) 15 - не точное
    _STRATUM = 1
    # Первые 8 бит - первый октет
    _FIRST_OCTET = _LEAP_INDICATOR << 6 | _VERSION_NUMBER << 3 | _MODE
    # CLIENT_REQUEST_TEMPLATE = '\x1b' + 47 * '\0'

    def __init__(self, time_delta: float = 0):
        self._received_time = self._time_with_delta(0)
        self._time_delta = time_delta
        self._transmit_time = 0

    def _time_with_delta(self, time_delta: float) -> int:
        """
        Нам нужен 64 битный unsigned int, где первые 32 бита - секунды, 
        а вторые 32 бита - доли секунды
        Поэтому мы умножаем на 2^32, что бы получить фейковые доли секунды
        """
        current_time = self._get_ntp_time()
        fake_time = current_time + time_delta
        return int(fake_time * self.BYTE_OFFSET)

    def _get_unix_time(self) -> int:
        return int(time.time())

    def _get_ntp_time(self) -> int:
        return self._get_unix_time() + self.UNIX_TIME_SHIFT

    def do_magic(self, received_packet: bytes) -> bytes:
        self._transmit_time = struct.unpack(self._HEADER_FORMAT,
                                            received_packet)[10]

        return self._build_server_packet()

    def _build_server_packet(self) -> bytes:
        return struct.pack(self._HEADER_FORMAT,
                           self._FIRST_OCTET,
                           self._STRATUM,
                           0,
                           0,
                           0,
                           0,
                           0,
                           0,
                           self._transmit_time,
                           self._received_time,
                           self._time_with_delta(self._time_delta))


class Server:
    _IP = '127.0.0.1'
    _PORT = 123

    def __init__(self, ip_addr: str, port: int, time_delta: float):
        self.time_delta = time_delta
        self._IP = ip_addr
        self._PORT = port
        print(f'Сервер запущен на {self._IP}:{self._PORT}')
        print(f'Установленное время сдвига: {time_delta//2} сек.')

    def handle_client(self, data, address):
        received_packet = data[0]
        print(f'Новый клиент: {address[0]}:{address[1]}')
        sntp = SNTP(self.time_delta)
        packet = sntp.do_magic(received_packet)
        self.sock.sendto(packet, address)

    def run(self):
        try:
            print("Server started")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self._IP, self._PORT))
        except OSError:
            print("OSError, сервер не может запуститься")
            self.sock.close()
            return

        while True:
            try:
                data = self.sock.recvfrom(1024)
            except KeyboardInterrupt:
                self.sock.close()
                print('Прерывание с клавиатуры, сервер остановлен')
                break
            threading.Thread(target=self.handle_client,
                             args=(data, data[1])).start()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delay', type=int,
                        default=0, help='Сдвиг времени в секундах')
    parser.add_argument('-p', '--port', type=int,
                        default=1233, help='Номер порта сервера')
    args = parser.parse_args()
    # Почему то время в 2 раза меньше чем мы передаем... Поэтому умножаем на 2 =)
    Server("localhost", args.port, args.delay*2).run()


if __name__ == '__main__':
    main()
