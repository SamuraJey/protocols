import socket
import ssl

ADDR = "smtp.mail.ru"
PORT = 465


def request(message: str) -> bytes:
    return (message + '\r\n').encode()


def __receive(client):
    print('Server:', client.recv(2048).decode().removesuffix('\n'))


def __send(client, message: str):
    client.send(request(message))
    __receive(client)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((ADDR, PORT))
    client = ssl.SSLContext().wrap_socket(sock=client)
    __send(client, 'EHLO SamuraJ')
    __send(client, 'AUTH LOGIN')
    __send(client, 'YWFhLXRlc3RlcjIwMjRAbWFpbC5ydQ==')
    __send(client, 'Tkg4S3JYVlJiZEJqY3FRWkNaNEc=')
    __send(client, 'MAIL FROM: aaa-tester2024@mail.ru')
    __send(client, 'RCPT TO: aaa-tester2024@mail.ru')
    __send(client, 'DATA')
    client.send(request('From: aaa-tester2024@mail.ru'))
    client.send(request('To: aaa-tester2024@mail.ru'))
    client.send(request('Subject: SERGEY ZAREMBA MO_201 Subject'))
    client.send(request('\r\n'))
    client.send(request('SERGEY ZAREMBA MO_201 TEXT'))
    client.send(request('SERGEY ZAREMBA MO_201 TEXT'))
    __send(client, '\r\n')
    __send(client, '.')
    __send(client, 'QUIT')
