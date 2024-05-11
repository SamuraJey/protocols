import logging
import socket
import ssl
import time

from config import Config
from encoder import Base64
from attacment import Attachment
from message import Message
import os

# Функция для удобной отправки сообщения


def request(message: str) -> bytes:
    return (message + '\r\n').encode()


class SMTP:
    def __init__(self, client: socket.socket, conf: Config):
        # Передавать конфиг немного криво, но не придумал как реализовать verbose иначе
        self._client = client
        self._config = conf

    def hello(self) -> 'SMTP':
        self.__send('EHLO server')
        return self

    def authorisation(self, login: str, password: str) -> 'SMTP':
        self.__send('AUTH LOGIN')
        time.sleep(0.1)
        self.__send(Base64.base64_from_string(login))
        time.sleep(0.1)
        self.__send(Base64.base64_from_string(password))
        return self

    def build_header(self, sender: str, recipients: list, size: int) -> 'SMTP':
        self.__send(f'MAIL FROM:<{sender}> SIZE={size}')
        for recipient in recipients:
            time.sleep(0.3)
            self.__send(f'RCPT TO:<{recipient}>')
        return self

    def send_data(self, data: str) -> 'SMTP':
        time.sleep(0.1)
        self.__send('DATA')
        time.sleep(0.1)
        self.__send(data, to_print=False)
        time.sleep(0.3)
        # self.__send("\r\n.\r\n")
        return self

    def __send(self, message: str):
        self._client.send(request(message))
        self.__receive()

    def __receive(self, to_print=True):
        BUFFER_SIZE = 4096*4
        response = bytearray()
        self._client.settimeout(2.0)  # Set a timeout of 2 seconds
        while True:
            try:
                data = self._client.recv(BUFFER_SIZE)
                if not data:
                    break
                response.extend(data)
            except socket.timeout:
                break
        self._client.settimeout(None)  # Remove the timeout
        if to_print:
            try:
                print('Received: ')
                print(response.decode())
            except UnicodeDecodeError as e:
                logging.error(f"Error while decoding: {e}")
                print("Error while decoding")
        try:
            return response.decode().strip()
        except UnicodeDecodeError as e:
            logging.error(f"Error while decoding: {e}")
            return response.decode(errors='ignore').strip()

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

    return f'{message.content}'


def get_attachments(path: str) -> list:
    attachments = []
    # print(f"path: {path}")
    # print(f"listdir: {os.listdir(str(path))}")
    for filename in os.listdir(str(path)):
        # Выбираем только файлы с расширением .jpg, .jpeg, .gif
        if filename.lower().endswith(('.jpg', '.jpeg', '.gif')):
            attachments.append(Attachment(
                os.path.abspath(path + filename)).content)
    return attachments


def main():
    # Указываем путь до файла конфигурации
    import argparse
    # Плохая справка, но она есть.
    parser = argparse.ArgumentParser(
        description='SMTP Client\nThis is how your config.json should look like:\n\
        {\n"mail_server": "smtp.gmail.com",\n"port": 465,\n"name": "NAME",\n"mail": "EMAIL@DOMAIN.COM",\n\
        "password": "YOUR_PASSWORD",\n"subject": "SUBJECT",\n"recipients": [\n"EMAIL@DOMAIN.COM"\n],\n\
        "message_file": "smtp/letter/text.txt",\n"attachments": [\n"smtp/letter/"\n],\n"verbose":"True"\n}\n\
        Where: mail_server - smtp server address\nport - smtp server port\nname - your name\nmail - your email\n\
        password - your password\nsubject - letter subject\nrecipients - list of recipients\n\
        message_file - path to the message file\nattachments - path to the directory with attachments\n\
        verbose - print server response if True or dont if False\n')

    # TODO Принимать путь до файла конфигурации
    args = parser.parse_args()
    config = Config('smtp/config_ya.json')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        socket.setdefaulttimeout(5)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_default_certs()
        client = context.wrap_socket(
            client, server_hostname=config.mail_server)
        client.connect((config.mail_server, config.port))

    smtp = SMTP(client, config)
    message = create_message(config)
    message_size = len(message[:-2].encode('utf-8'))

    smtp.hello()\
        .authorisation(config.name, config.password)\
        .build_header(config.mail, config.recipients, message_size)\
        .send_data(message)\
        .quit()


if __name__ == '__main__':
    main()
