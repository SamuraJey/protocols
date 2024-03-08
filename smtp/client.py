import argparse
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
    def __init__(self, client: socket.socket, config: Config):
        self._client = client
        self._config = config

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
        if self._config.verbose:
            print('Server:', self._client.recv(65535)
                  .decode().removesuffix('\n'))

    def quit(self):
        self.__send('QUIT')


def create_message(smpt: SMTP) -> str:
    # subject = config.subject
    message = Message(smpt._config)
    if not smpt._config.attachments:
        attachments = get_attachments(os.getcwd())
    else:
        attachments = get_attachments(smpt._config.attachments[0])

    for attachment in attachments:
        message.append(attachment)
    message.end()

    return f'{message.content}\r\n.\n'


def get_attachments(path: str) -> list:
    attachments = []
    print(f"path: {path}")
    print(f"listdir: {os.listdir(str(path))}")
    for filename in os.listdir(str(path)):
        if filename.lower().endswith(('.jpg', '.jpeg', '.gif')):
            attachments.append(Attachment(
                os.path.abspath(path + filename)).content)
    return attachments


def main():
    parser = argparse.ArgumentParser(
        description='Send an email with attachments.')
    parser.add_argument('--config', type=str, default='',
                        help='load configuration from JSON file')
    parser.add_argument('-s', '--server', type=str,
                        help='SMTP server address or domain name')
    parser.add_argument('-t', '--to', type=str,
                        help='email address of the recipient')
    parser.add_argument('-f', '--from_email', type=str,
                        default='<>', help='email address of the sender')
    parser.add_argument('--subject', type=str,
                        default='Happy Pictures', help='subject of the email')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='display protocol communication')
    parser.add_argument('-d', '--directory', type=str, default=os.getcwd(),
                        help='directory containing images to be attached')

    args = parser.parse_args()

    if args.config:
        # config = Config(args.config)
        config = Config("config.json")
    else:
        config = Config(mail_server=args.server,  mail=args.from_email, fake_name=args.fake_name, name=args.name, password=args.password, recipients=[
                        args.to], message_file=args.message_file, subject=args.subject, attachments=[args.directory], verbose=bool(args.verbose))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((config.mail_server, config.port))
        client = ssl.SSLContext().wrap_socket(sock=client)

    smtp = SMTP(client, config)
    smtp.hello()\
        .authorisation(config.name, config.password)\
        .build_header(config.mail, config.recipients)\
        .send_data(create_message(smtp))\
        .quit()
    client.close()


if __name__ == '__main__':
    main()
