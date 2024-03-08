import socket
import ssl
import time

from config import Config
from encoder import Base64
from attacment import Attachment
from message import Message
import os


def request(message: str) -> bytes:
    return (message + '\r\n').encode()


class SMTP:
    def __init__(self, client: socket.socket):
        self._client = client

    def hello(self) -> 'SMTP':
        self.__send('EHLO server\r\n')
        return self

    def authorisation(self, login: str, password: str) -> 'SMTP':
        self.__send('AUTH LOGIN')
        self.__send(Base64.base64_from_string(login))
        self.__send(Base64.base64_from_string(password))
        return self

    def build_header(self, sender: str, recipients: list) -> 'SMTP':
        self.__send(f'MAIL FROM:<{sender}>\r\n')
        for recipient in recipients:
            time.sleep(0.5)
            self.__send(f'RCPT TO:<{recipient}>\r\n')
        return self

    def send_data(self, data: str) -> 'SMTP':
        time.sleep(0.5)
        self.__send('DATA')
        time.sleep(0.5)
        self.__send(data)
        time.sleep(0.5)
        self.__send("\r\n.\r\n")
        return self

    def __send(self, message: str):
        self._client.send(request(message))
        self.__receive()

    def __receive(self):
        print('Server:', self._client.recv(65535)
              .decode().removesuffix('\n'))

    def quit(self):
        self.__send('QUIT')


def create_message(config: Config) -> str:
    # subject = config.subject
    message = Message(config)
    if not config.attachments:
        attachments = get_attachments(os.getcwd())
    else:
        attachments = get_attachments(config.attachments[0])

    for attachment in attachments:
        message.append(attachment)
    message.end()

    return f'{message.content}\r\n.\n'

def get_attachments(path: str) -> list:
    attachments = []
    print(f"path: {path}")
    print(f"listdir: {os.listdir(str(path))}")
    for filename in os.listdir(str(path)):
        if filename.lower().endswith(('.jpg','.jpeg', '.gif')):
            attachments.append(Attachment(os.path.abspath(path + filename)).content)
    return attachments


def main():
    config = Config('smtp/config_go.json')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((config.mail_server, config.port))
        client = ssl.SSLContext().wrap_socket(sock=client)

    smtp = SMTP(client)
    smtp.hello()\
        .authorisation(config.name, config.password)\
        .build_header(config.mail, config.recipients)\
        .send_data(create_message(config))\
        .quit()


if __name__ == '__main__':
    main()
