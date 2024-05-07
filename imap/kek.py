import socket
import ssl
import json
# import base64
import email
from email.header import decode_header
from base64 import b64decode
import re
import sys
from time import sleep
from prettytable import PrettyTable

class IMAPClient:
    def __init__(self, config_file):
        with open(config_file) as f:
            config = json.load(f)

        self.current_command = "A000"
        self.ssl_enabled = config.get('ssl')
        self.server = config.get('server').split(':')
        self.host = self.server[0]
        self.port = int(self.server[1]) if len(self.server) > 1 else 143
        self.n1 = config.get('n', '1')
        self.n2 = config.get('n2', '*')
        self.user = config.get('user')
        self.password = config.get('password')

        self.socket = None
        self.connected = False

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(3)
        if self.ssl_enabled:
            self.socket = ssl.wrap_socket(self.socket)
        self.socket.connect((self.host, self.port))
        self.read_response()  # Читаем приветственное сообщение сервера

        self.send_command(f'LOGIN {self.user} {self.password}')
        self.connected = True

    def read_response(self, to_print=True):
        response = b''
        while True:
            data = self.socket.recv(65000)
            response += data
            if data.endswith(b'\r\n'):
                print("srabotal break")
                break
        if to_print:
            print(response.decode())
        return response.decode().strip()

    def send_command(self, command, to_print=True):
        self.socket.sendall(f'{self.current_command} {command}\r\n'.encode())
        self.current_command = self.current_command[0] + str(int(self.current_command[1:]) + 1).zfill(3)
        print(f'Sent: {command}')
        return self.read_response(to_print=to_print)

    def get_headers(self):
        self.send_command('SELECT INBOX')
        kek = self.send_command(f'FETCH {self.n1}:{self.n2} BODY[HEADER]', to_print=False)
        headers = kek.split('\r\n\r\n)\r\n')
        # while True:
        #     response = self.read_response()
        #     if response.startswith('OK'):
        #         break
        #     headers.append(response)

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
                
                # print(f"\n\nfrom_header: {from_header}\n\n")
                    if email_msg['Subject'] is not None:
                        subject_header = decode_header(email_msg['Subject'])
                    else:
                        subject_header = "No_subject_header"
                except TypeError as e:
                    print(f"Error TypeError {e}")
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
                            print(f"Wrong encoding is encounterd in From field: {part[-1]}\n{exp}")
                            # print("Wrong encoding is encounterd in From field: " + part[-1] + "\n" + exp)
                            print(f"Error in header: {from_header}")
                            # print("Error in header: " + from_header)



                # try:
                #     # from_header parser
                #     if type(from_header[0][0]) is str:
                #         from_who = from_header[0][0]
                #         # print("if headear" + from_who)
                #     elif type(from_header[0][0]) is bytes: #or type(from_header[0][0]) is bytearray:
                #         if from_header[0][-1] is not None:
                #             our_encoding = from_header[0][-1]
                #         from_who = from_header[0][0].decode(our_encoding)
                #         # print("elif header" + from_who)
                # except LookupError:
                #     print("Wrong encoding is encounterd in From field: " + our_encoding)
                #     print("Kekero123 " + from_header)
                #     from_who = "Encoding_error"
                
                try:
                    if type(subject_header[0][0]) is str:
                        subject = subject_header[0][0]
                        # print("if subcjet" + subject)
                    elif type(subject_header[0][0]) is bytes:
                        if subject_header[0][-1] is not None:
                            our_encoding = subject_header[0][-1]
                        subject = subject_header[0][0].decode(our_encoding)
                        # print("elif subcjet" + subject)
                except LookupError:
                    print(f"Wrong encoding is encounterd in subject field: {our_encoding}")
                    print(f"answerrr Kekero123 {subject_header}")
                    subject = "Encoding_error"
                # print(subject_header)
                # trying to get attachments
                
                emails.append({
                    'From': from_who_answer,
                    'To': email_msg['To'],
                    'Subject': subject,
                    'Date': email_msg['Date'],
                    'Size': email_msg['Content-Length'],
                    "Message-Id": email_msg["Message-Id"]
                })
        # try:
        #     attachments = self.get_attachments()
        # except Exception as e:
        #     print(f"Error in getting attachments: {e}")
        #     attachments = []
        return emails


    def get_attachments(self):
        self.send_command('SELECT INBOX')
        kek = self.send_command(f'FETCH {self.n1}:{self.n2} (BODY.PEEK[])', to_print=False)
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
            if value is None:
                continue
            match_encoding = re.search(pattern_for_encoding, value)
            match_text = re.search(pattern_for_text, value)
            if match_encoding:
                encoding = match_encoding.group(1)
            if match_text:
                key_to_change = list(item.keys())[list(item.values()).index(value)]
                part_1 = b64decode(match_text.group(1)).decode(encoding)
                part_2 = value.split(match_text.group(1))[1].lstrip("?= ")
                item[key_to_change] = part_1 + " " + part_2
    return given_headers

client = IMAPClient('imap/cfg.json')
client.connect()

# Получение заголовков писем
headers = client.get_headers()
headers = mime_encoding_decode(headers)

# Вывод заголовков в виде таблицы
table = PrettyTable()
table.field_names = ['From', 'To', 'Subject', 'Date', 'Size', 'Message-Id']



# Получение информации о вложениях
attachments = client.get_attachments()
# # print(attachments)
for attachment in attachments:
    # print(f"Filename: {attachment['filename']}")
    print(f"Filename: {attachment['filename']}, Size: {attachment['size']/1024:.2f} KB, Message-Id: {attachment['Message-Id']}")

for header in headers:
    table.add_row([header['From'], header['To'], header['Subject'], header['Date'], header['Size'], header["Message-Id"]])
print(table)
# print(headers)
client.close()
sys.exit(0)