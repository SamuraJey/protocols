import argparse
import socket
import struct
import time

UNIX_TIME_SHIFT = 2208988800
BYTE_OFFSET = 2 ** 32


def time_with_delta(time_delta: float) -> int:
    current_time = get_ntp_time()
    fake_time = current_time + time_delta
    return int(fake_time * BYTE_OFFSET)


def get_unix_time() -> int:
    return int(time.time())


def get_ntp_time() -> int:
    return get_unix_time() + UNIX_TIME_SHIFT


class SNTP:
    """
    RFC 4330
    https://www.rfc-editor.org/rfc/inline-errata/rfc4330.html
    """
    _HEADER_FORMAT = '> B B B B I I 4s Q Q Q Q'
    _LEAP_INDICATOR = 0  # no warning
    _VERSION_NUMBER = 4  # NTP/SNTP version number
    _MODE = 4  # server
    _STRATUM = 1  # synchronized
    _FIRST_OCTET = _LEAP_INDICATOR << 6 | _VERSION_NUMBER << 3 | _MODE
    # CLIENT_REQUEST_TEMPLATE = '\x1b' + 47 * '\0'

    def __init__(self, time_delta: float = 0):
        self._received_time = time_with_delta(0)
        self._time_delta = time_delta
        self._transmit_time = 0

    def do_magic(self, received_packet: bytes) -> bytes:
        self._transmit_time = struct.unpack(self._HEADER_FORMAT,
                                            received_packet)[10]

        return self.build_server_packet()

    def build_server_packet(self) -> bytes:
        return struct.pack(self._HEADER_FORMAT,
                           self._FIRST_OCTET,
                           self._STRATUM,
                           0,
                           0,
                           0,
                           0,
                           b'',
                           0,
                           self._transmit_time,
                           self._received_time,
                           time_with_delta(self._time_delta))


import threading

class Server:
    _IP = '127.0.0.1'
    _PORT = 123

    def __init__(self, ip_addr: str, port: int, time_delta: float):
        self.time_delta = time_delta
        self._IP = ip_addr
        self._PORT = port
        print(f'Server start on {self._IP}:{self._PORT}')
        print(f'Установленное время сдвига: {time_delta//2} сек.')

    def handle_client(self, data, address):
        received_packet = data[0]
        print(f'New client: {address[0]}:{address[1]}')
        sntp = SNTP(self.time_delta)
        packet = sntp.do_magic(received_packet)
        self.sock.sendto(packet, address)

    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self._IP, self._PORT))
        except OSError:
            print("OSError, server can't start")
            self.sock.close()
            return

        while True:
            try:
                data = self.sock.recvfrom(1024)
            except KeyboardInterrupt:
                self.sock.close()
                print('Keyboard interrupt, server stopped')
                break
            threading.Thread(target=self.handle_client, args=(data, data[1])).start()


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delay', type=int,
                        default=300, help='Time delay in seconds')
    parser.add_argument('-p', '--port', type=int,
                        default=12333, help='Port number')
    args = parser.parse_args()

    Server("192.168.1.40", args.port, args.delay*2).run()


if __name__ == '__main__':
    start()
