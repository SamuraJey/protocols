import socket
import time

from ntplib import NTPStats

stats = NTPStats()

sock = socket.socket()
sock.connect(('192.168.1.40', 12333))
time.sleep(1)

data = '\x1b' + 47 * '\0'
sock.send(data.encode('utf-8'))

data = sock.recv(1024)

sock.close()

print(f'Полученные данные: {data}')
stats.from_data(data)
print(f'Время полученное пользователем: {time.ctime(stats.tx_time)}')
