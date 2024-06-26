from encoder import Base64
from config import Config


class Message:
    def __init__(self, config: Config):
        targets_address = ','.join(f'"{x}" <{x}>' for x in config.recipients)
        self._boundary = f'sIMpLe_BoUnDaRy_1234567890'
        subject = Base64.base64_from_string(config.subject or "No subject")
        header = [
            f'From: "{config.fake_name}" <{config.mail}>',
            f'To:{targets_address}',
            f'Subject: =?UTF-8?B?{subject}?=',
            f'Content-type: multipart/mixed; boundary={self._boundary}',
            f'\n--{self._boundary}'
        ]
        self._header = '\n'.join(header)
        # print(f"self._header: {self._header}")
        self._text = self.get_text(config.message_file)
        self._text = self._text.replace('\n.', '\n..')

    def append(self, message: str):
        self._text += f'\n--{self._boundary}\n{message}\n'

    def end(self):
        self._text += f'\n--{self._boundary}--\n.'

    @property
    def content(self) -> str:
        return f'{self._header}\n{self._text}'

    @property
    def text(self) -> str:
        return self._text

    @staticmethod
    def get_text(filename: str) -> str:
        with open(filename, 'r', encoding='utf8') as file:
            message = "".join(file.readlines())
        return f'Content-Type: text/plain; charset=utf-8\n' \
               f'Content-Transfer-Encoding: 8bit\n' \
               f'\n{message}'
