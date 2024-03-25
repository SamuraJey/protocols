import struct
import sys
import socket
import re


def whois(ip_or_dns, server):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server, 43))
    sock.sendall((bytes(ip_or_dns, 'utf-8')) + b'\r\n')

    response = ''
    while True:
        data = str((sock.recv(1024)), encoding='utf-8')
        if not data:
            break
        response += data
    sock.close()
    return response

# NETNAME, AS, COUNTRY
def parse(ip, server: str = "whois.iana.org", main = True):
    netname = ''
    as_number = ''
    country = ''

    servs = ("whois.arin.net", "whois.lacnic.net", "whois.ripe.net", "whois.afrinic.net", "whois.apnic.net")

    res = whois(ip, server)

    for line in res.splitlines():
        if line.startswith("whois"):
            return parse(ip, line.split(':')[1].strip(), False)
        if re.match(re.compile(r"^[Nn]et[Nn]ame"), line) is not None:
            netname = line.split(':')[1].strip()
        if line.startswith("origin") or line.startswith("OriginAS"):
            as_number = line.split(':')[1].strip()
        if re.match(re.compile(r"^[Cc]ountry"), line) is not None:
            country = line.split(':')[1].strip()

    if main and netname == "" and country == "" and as_number == "":
        for s in servs:
            n_name, n_country, n_number = parse(ip, s, False)
            netname = netname if n_name == "" else n_name
            country = country if n_country == "" else n_country
            as_number = as_number if n_number == "" else n_number

    return netname, country, as_number

def local(ip):
    ip_app = [int(i) for i in ip.split('.')]

    # 10.0.0.0 — 10.255.255.255
    if ip_app[0] == 10:
        return True
    # 100.64.0.0 — 100.127.255.255
    if ip_app[0] == 100 and (ip_app[1] >= 64 or ip_app[1] <= 127):
        return True
    # 172.16.0.0 — 172.31.255.255
    if ip_app[0] == 172 and (ip_app[1] >= 16 or ip_app[1] <= 31):
        return True
    # 192.168.0.0 — 192.168.255.255
    if ip_app[0] == 192 and ip_app[1] == 168:
        return True
    return False

def get_checksum(header):
    checksum = 0
    overflow = 0
    for i in range(0, len(header), 2):
        word = header[i] + (header[i + 1] << 8)
        checksum = checksum + word
        overflow = checksum >> 16
        while overflow > 0:
            checksum = checksum & 0xFFFF
            checksum = checksum + overflow
            overflow = checksum >> 16
    overflow = checksum >> 16
    while overflow > 0:
        checksum = checksum & 0xFFFF
        checksum = checksum + overflow
        overflow = checksum >> 16
    checksum = ~checksum
    checksum = checksum & 0xFFFF
    return checksum

def icmp_proto(ttl, ip):
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    header = struct.pack(
        "bbHHh", 8, 0, 0, 0, 0)
    checksum = get_checksum(header)
    header = struct.pack("bbHHh", 8,
                         0, checksum, 0, 0)
    icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    icmp_socket.settimeout(1)
    icmp_socket.sendto(header, (ip, 1))

    try:
        data, addres = icmp_socket.recvfrom(1024)
        return addres[0]
    except socket.timeout:
        return None

def trace(final_ip):
    for ttl in range(1, 31):
        ip = icmp_proto(ttl, final_ip)

        if ip:
            print(f"{ttl}. {ip}\r\n")
            netmask, countr, num = parse(ip)
            if local(ip):
                print("locale\r\n")
            else:
                print(f"{netmask}, {countr}, {num}\r\n")

            if ip == final_ip:
                return
        else:
            print(f"{ttl}. *\r\n")

        print("\r\n")


def main():
    ip_or_dns = sys.argv[1]
    ip = socket.gethostbyname(ip_or_dns)
    trace(ip)



if __name__ == "__main__":
    main()