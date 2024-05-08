import logging
import socket
import ssl
import json

import email
from email.header import decode_header
from base64 import b64decode
import re
import sys
from time import sleep
import prettytable

DEBUG = True


class IMAPClient:
    def __init__(self, config_file):
        try:
            with open(config_file) as f:
                config = json.load(f)
        except FileNotFoundError as e:
            logging.error(f"File not found: {config_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logging.error(f"Error while reading json file: {e}")
            sys.exit(1)
        except PermissionError as e:
            logging.error(f"Permission denied: {e}")
            sys.exit(1)

        self.current_command = "A000"
        self.ssl_enabled = config.get('ssl')
        self.server = config.get('server').split(':')
        self.host = self.server[0]
        self.port = int(self.server[1]) if len(self.server) == 2 else 143
        self.n1 = config.get('start_id', '1')
        self.n2 = config.get('end_id', '*')
        self.user = config.get('user')
        self.password = config.get('password')

        self.socket = None
        self.connected = False

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(3)
        if self.ssl_enabled:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_default_certs()
            self.socket = context.wrap_socket(self.socket, server_hostname=self.host)
            # self.socket = ssl.wrap_socket(self.socket)
        self.socket.connect((self.host, self.port))
        self.read_response()  # Читаем приветственное сообщение сервера

        self.send_command(f'LOGIN {self.user} {self.password}')
        self.connected = True

    def read_response(self, to_print=True):
        response = b''
        
        while True:
            data = self.socket.recv(65535)
            response += data
            if data.endswith(b'\r\n'):
                break
        if to_print:
            print(response.decode())
        return response.decode().strip()

    def send_command(self, command, to_print=True):
        self.socket.sendall(f'{self.current_command} {command}\r\n'.encode())
        self.current_command = self.current_command[0] + \
            str(int(self.current_command[1:]) + 1).zfill(3)
        print(f'Sent: {command}')
        sleep(3) # Для того, чтобы сервер успел обработать запрос. На меньших значениях может выдавать бред.
        return self.read_response(to_print=to_print)

    def get_headers(self):
        self.send_command('SELECT INBOX')
        kek = self.send_command(f'FETCH {self.n1}:{self.n2} RFC822', to_print=False)
        headers = kek.split('\r\n)\r\n')
        # print(headers)
        emails = []

        for header in headers:
            if header.startswith('* '):
                header_data = header.split('\r\n', 1)[1]
                email_msg = email.message_from_bytes(header_data.encode())
                try:
                    if email_msg['From'] is not None:
                        from_header = decode_header(email_msg['From'])
                    else:
                        from_header = "No_from_header"

                    if email_msg['Subject'] is not None:
                        subject_header = decode_header(email_msg['Subject'])
                    else:
                        subject_header = "No_subject_header"
                except TypeError as e:
                    logging.error(f"Error TypeError {e}")
                    continue
                from_who_answer = ""

                for part in from_header:
                    if type(part[0]) is str:
                        from_who_answer += part[0]
                    elif type(part[0]) is bytes:
                        try:
                            if part[-1] is not None:
                                from_who_answer += part[0].decode(part[-1])
                            else:
                                try:
                                    from_who_answer += part[0].decode()
                                except UnicodeDecodeError as e:
                                    from_who_answer += "Decode_Error"
                                    print(e)
                        except LookupError as exp:
                            from_who_answer += "Unknown_encoding"
                            logging.error(
                                f"Wrong encoding is encounterd in From field: {part[-1]}\n{exp}")
                            logging.error(f"Error in header: {from_header}")

                try:
                    if type(subject_header[0][0]) is str:
                        subject = subject_header[0][0]
                    elif type(subject_header[0][0]) is bytes:
                        if subject_header[0][-1] is not None:
                            our_encoding = subject_header[0][-1]
                        subject = subject_header[0][0].decode(our_encoding)
                except LookupError:
                    logging.error(
                        f"Wrong encoding is encounterd in subject field, encoding is: {our_encoding}")
                    logging.error(
                        f"Subject header with error: {subject_header}")
                    subject = "Encoding_error"

                emails.append({
                    'From': from_who_answer,
                    'To': email_msg['To'],
                    'Subject': subject,
                    'Date': email_msg['Date'],
                    'Size': str(len(header_data.encode())), 
                    "Message-Id": email_msg["Message-Id"]
                })
        self.send_command('CLOSE')
        return emails

    def get_attachments(self, email_list=None):
        self.send_command('SELECT INBOX')
        kek = self.send_command(
            f'FETCH {self.n1}:{self.n2} (BODY.PEEK[])', to_print=False)
        attachments_raw = kek.split('\r\n)\r\n')
        # response = self.read_response(to_print=False)
        # print(attachments_raw)
        attachments = []
        for response in attachments_raw:
            if response.startswith('* '):
                message_data = response.split('\r\n', 1)[1]
                email_msg = email.message_from_bytes(message_data.encode())

                for part in email_msg.walk():
                    # print(part)
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'size': len(part.get_payload(decode=True)),
                            'Message-Id': email_msg['Message-Id']
                        })

        return attachments

    def close(self):
        self.send_command('LOGOUT')
        self.socket.close()
        self.connected = False


pattern_for_encoding = r"\?([^?]+)\?"
pattern_for_text = r'=\?\S*\?B\?(.*?)\?=\S*'


def mime_encoding_decode(given_headers: list) -> list:
    for item in given_headers:
        for value in item.values():
            if value is None and (type(value) is not str or type(value) is not bytes):
                continue
            match_encoding = re.search(pattern_for_encoding, value)
            match_text = re.search(pattern_for_text, value)
            if match_encoding:
                encoding = match_encoding.group(1)
            if match_text:
                key_to_change = list(item.keys())[
                    list(item.values()).index(value)]
                part_1 = b64decode(match_text.group(1)).decode(encoding)
                part_2 = value.split(match_text.group(1))[1].lstrip("?= ")
                item[key_to_change] = part_1 + " " + part_2
    return given_headers

def main():
    client = IMAPClient('imap/config_mail_ru.json')
    client.connect()

    # Получение заголовков писем
    messages = client.get_headers()
    messages = mime_encoding_decode(messages)
    attachments = client.get_attachments()

    if DEBUG:
        with open('messages_before.json', 'w') as f:
            json.dump(messages, f, indent=4)

    # Собираем все в один словарь
    msg_dict = {}
    for message in messages:
        msg_dict[message["Message-Id"]] = message

    for att in attachments:
        msg_dict[att["Message-Id"]].setdefault("Attachment", []).append(att)

    table = prettytable.PrettyTable()
    table.field_names = ['From', 'To', 'Subject', 'Date', 'Size(in bytes)', 'Attachments']

    for msg_id, msg_data in msg_dict.items():
        attachments = msg_data.get('Attachment', [])
        attachment_data = ', '.join(
            [f"{att['filename']} ({att['size']/1024:.1f}kB)" for att in attachments])
        table.add_row([
            msg_data['From'],
            msg_data['To'],
            msg_data['Subject'],
            msg_data['Date'],
            msg_data['Size'],
            # msg_data['Message-Id'],
            attachment_data
        ])

    if DEBUG:
        with open('messages_after.json', 'w') as f:
            json.dump(messages, f, indent=4)
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(str(table))

    print(table)

    # Таблица получается большой, лучше бы её записать в файл - читать удобнее, но в задаче написано выводить на экран

    # with open('output.txt', 'w', encoding='utf-8') as f:
    #     f.write(str(table))

    client.close()
    sys.exit(0)

if __name__ == '__main__':
    main()

'''
если захотим сохранить данные в json
with open('attachments.json', 'w') as f:
        json.dump(attachments, f, indent=4)
with open('messages.json', 'w') as f:
        json.dump(messages, f, indent=4)
'''
