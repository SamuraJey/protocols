import socket
import struct
import time

NTP_SERVER = "localhost"
TIME1970 = 2208988800


def sntp_client():
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
    sock.connect(('localhost', 12332))
    data = '\x1b' + 47 * '\0'
    time.sleep(1)
    print('Sending request to', NTP_SERVER)
    sock.sendto(data.encode('utf-8'), (NTP_SERVER, 12332))
    while True:

        data, address = sock.recvfrom(1024)
        if not data:
            break
        if data:
            print(f'Response received from: {address}')
        t = struct.unpack('!12I', data)[10]
        t -= TIME1970
        print('\tTime=%s' % time.ctime(t))


if __name__ == '__main__':
    sntp_client()
