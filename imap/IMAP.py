#!/usr/bin/python

# Made by: Sergey Zaremba MO-201
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
import os
# Using local copy of library because i can
import lib.prettytable_init as prettytable

DEBUG = False


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
        socket.setdefaulttimeout(10)
        if self.ssl_enabled:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            context.load_default_certs()
            self.socket = context.wrap_socket(
                self.socket, server_hostname=self.host)
            # self.socket = ssl.wrap_socket(self.socket)
        self.socket.connect((self.host, self.port))
        self.read_response()  # Читаем приветственное сообщение сервера

        self.send_command(f'LOGIN {self.user} {self.password}')
        self.connected = True

    def read_response(self, to_print=True):
        BUFFER_SIZE = 4096*4
        response = bytearray()
        self.socket.settimeout(2.0)  # Set a timeout of 2 seconds
        while True:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    break
                response.extend(data)
            except socket.timeout:
                break
        self.socket.settimeout(None)  # Remove the timeout
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

    def send_command(self, command, to_print=True):
        self.socket.sendall(f'{self.current_command} {command}\r\n'.encode())
        self.current_command = self.current_command[0] + \
            str(int(self.current_command[1:]) + 1).zfill(3)
        print(f'Sent: {command}')
        sleep(0.2)
        return self.read_response(to_print=to_print)

    def get_emails(self):
        self.send_command('SELECT INBOX')

        email_list = []
        for msg_id in range(int(self.n1), int(self.n2) + 1):
            response = self.send_command(
                f'FETCH {msg_id} BODY.PEEK[]', to_print=False)
            email_list.append(response)

        # print(headers)
        emails = []

        for one_email in email_list:
            if one_email.startswith('* '):
                header_data = one_email.split('\r\n', 1)[1]
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
        attachemnt_data = self.get_attachments(email_list)
        return emails, attachemnt_data

    def get_attachments(self, email_list=None):
        if not email_list:
            return None
        attachments = []
        for response in email_list:
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


def merge_emails_with_attachments(emails, attachments):
    for email in emails:
        for attachment in attachments:
            if email["Message-Id"] == attachment["Message-Id"]:
                email.setdefault("Attachment", []).append(attachment)
    return emails


def main():
    client = IMAPClient('imap/config_mail_ru.json')
    client.connect()

    messages, attachments = client.get_emails()
    messages = mime_encoding_decode(messages)

    if DEBUG:
        with open('messages_before.json', 'w') as f:
            json.dump(messages, f, indent=4)

    # Собираем все в один словарь
    list_of_dictionaries = merge_emails_with_attachments(messages, attachments)

    table = prettytable.PrettyTable()
    table.field_names = ['№', 'From', 'To', 'Subject',
                         'Date', 'Size(in bytes)', 'Attachments']
    counter = 1
    for item in list_of_dictionaries:
        attachments = item.get('Attachment', [])
        attachment_data = ', '.join(
            [f"{att['filename']} ({att['size']/1024:.1f} kB)" for att in attachments]) if attachments else None
        size_in_kb = int(item.get("Size"))/1024 if item.get("Size") else None
        table.add_row([counter, item.get("From"), item.get("To"), item.get("Subject"),
                       item.get("Date"), f"{size_in_kb:.1f} kB", attachment_data])
        counter += 1

    if DEBUG:
        with open('messages_after.json', 'w') as f:
            json.dump(messages, f, indent=4)
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(str(table))

    print(table)

    # Таблица получается большой, лучше бы её записать в файл - читать удобнее,
    # но в задаче написано выводить на экран, но я все равно записал в файл =)

    if os.path.isfile('output.txt'):
        print("output.txt already exists. Skipping writing file.")
    else:
        with open('output.txt', 'w', encoding='utf-8') as f:
            f.write(str(table))

    client.close()
    sys.exit(0)


if __name__ == '__main__':
    main()

'''
если захотим сохранить данные в json
with open('data.json', 'w') as f:
        json.dump(msg_dict, f, indent=4)
with open('messages.json', 'w') as f:
        json.dump(messages, f, indent=4)
'''
