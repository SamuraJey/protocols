import socket
import struct
import time

NTP_SERVER = 'ntp0.ntp-servers.net'
NTP_PORT = 123


def get_ntp_time():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5)
    try:
        client_socket.connect((NTP_SERVER, NTP_PORT))

        packet = bytearray(48)
        packet[0] = 0x1B

        client_socket.sendall(packet)
        

        response_packet = client_socket.recv(48)
        HEADER_FORMAT = '> B B B B I I I Q Q Q Q'
        first_octet, Stratum, Poll, Precision, Root_delay, Root_dispersion, Reference_ID, Reference_timestamp, Originate_timestamp, Receive_timestamp, Transmit_timestamp = struct.unpack(
            HEADER_FORMAT, response_packet)
        Leap_indicator = first_octet >> 6
        Version_number = (first_octet >> 3) & 0b111
        Mode = first_octet & 0b111
        Reference_timestamp = Reference_timestamp / 2 ** 32 - 2208988800
        Receive_timestamp = Receive_timestamp / 2 ** 32 - 2208988800
        Transmit_timestamp = Transmit_timestamp / 2 ** 32 - 2208988800
        print(f'Leap indicator: {Leap_indicator}')
        print(f'Version number: {Version_number}')
        print(f'Mode: {Mode}')
        print(f'Stratum: {Stratum}')
        print(f'Poll: {Poll}')
        print(f'Precision: {Precision}')
        print(f'Root delay: {Root_delay}')
        print(f'Root dispersion: {Root_dispersion}')
        print(f'Reference ID: {Reference_ID}')
        print(f'Reference timestamp: {Reference_timestamp}')
        print(f'Originate timestamp: {Originate_timestamp}')
        print(f'Receive timestamp: {Receive_timestamp}')
        print(f'Transmit timestamp: {Transmit_timestamp}')

        ntp_time = Transmit_timestamp
        human_readable_time = time.ctime(ntp_time)

        print(f"NTP time: {human_readable_time}")

    except socket.timeout:
        print("Timeout: Unable to receive NTP response")

    finally:
        client_socket.close()

if __name__ == '__main__':
    get_ntp_time()
