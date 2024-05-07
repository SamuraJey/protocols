import socket
import ssl
import json
import base64
import email
from email.header import decode_header

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
        socket.setdefaulttimeout(10)
        if self.ssl_enabled:
            self.socket = ssl.wrap_socket(self.socket)
        self.socket.connect((self.host, self.port))
        self.read_response()  # Читаем приветственное сообщение сервера

        self.send_command(f'LOGIN {self.user} {self.password}')
        self.connected = True

    def read_response(self):
        response = b''
        while True:
            data = self.socket.recv(1024)
            response += data
            if data.endswith(b'\r\n'):
                break
        print(response.decode())
        return response.decode().strip()

    def send_command(self, command):
        self.socket.sendall(f'{self.current_command} {command}\r\n'.encode())
        self.current_command = self.current_command[0] + str(int(self.current_command[1:]) + 1).zfill(3)
        print(f'Sent: {command}')
        return self.read_response()

    def get_headers(self):
        self.send_command('SELECT INBOX')
        kek = self.send_command(f'FETCH {self.n1}:{self.n2} BODY[HEADER]')
        headers = kek.split('\r\n\r\n)\r\n')
        # while True:
        #     response = self.read_response()
        #     if response.startswith('OK'):
        #         break
        #     headers.append(response)

        emails = []
        for header in headers:
            if header.startswith('* '):
                # header_data = header.split(') ')[-1]
                header_data = header.split('\r\n', 1)[1]
                email_msg = email.message_from_bytes(header_data.encode())
                # print()
                # print(email_msg)
                # print()
                try:
                    from_header = decode_header(email_msg['From'])
                
                # print(f"\n\nfrom_header: {from_header}\n\n")

                    subject_header = decode_header(email_msg['Subject'])
                except TypeError:
                    print("Sluchilsa pipets")
                    continue
                from_who_answer = ""
                try:
                    # from_header parser
                    if type(from_header[0][0]) is str:
                        from_who = from_header[0][0]
                        # print("if headear" + from_who)
                    elif type(from_header[0][0]) is bytes: #or type(from_header[0][0]) is bytearray:
                        if from_header[0][-1] is not None:
                            our_encoding = from_header[0][-1]
                        from_who = from_header[0][0].decode(our_encoding)
                        # print("elif header" + from_who)
                except LookupError:
                    print("Wrong encoding is encounterd in From field: " + our_encoding)
                    print("Kekero123 " + from_header)
                    from_who = "Encoding_error"
                
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
                    print("Wrong encoding is encounterd in subject field: " + our_encoding)
                    print(f"Kekero123 {subject_header}")
                    subject = "Encoding_error"
                # print(subject_header)
                emails.append({
                    'From': from_who,
                    'To': email_msg['To'],
                    'Subject': subject,
                    'Date': email_msg['Date'],
                    'Size': email_msg['Content-Length']
                })

        return emails


    def get_attachments(self):
        self.send_command(f'FETCH {self.n1}:{self.n2} (BODY.PEEK[])')
        attachments = []
        while True:
            response = self.read_response()
            if response.startswith('OK'):
                break
            if response.startswith('* '):
                message_data = response.split(') ')[-1]
                email_msg = email.message_from_bytes(message_data.encode())
                for part in email_msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'size': len(part.get_payload(decode=True))
                        })

        return attachments

    def close(self):
        self.send_command('LOGOUT')
        self.socket.close()
        self.connected = False

# Пример использования
client = IMAPClient('imap/cfg.json')
client.connect()

# Получение заголовков писем
headers = client.get_headers()
for header in headers:
    # Работет вроде, кроме сайз
    print(f"From: {header['From']}, To: {header['To']}, Subject: {header['Subject']}, Date: {header['Date']}, Size: {header['Size']}")

# Получение информации о вложениях
# attachments = client.get_attachments()
# for attachment in attachments:
#     print(f"Filename: {attachment['filename']}, Size: {attachment['size']}")

client.close()