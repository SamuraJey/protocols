import mimetypes
import os

from encoder import Base64


class Attachment:
    def __init__(self, filename: str):
        file_extension = os.path.splitext(filename)[1]
        content_type = mimetypes.types_map[file_extension]
        name = filename.split('\\')[-1]
        # base64_filename = f'"{Base64.base64_from_string(name)}"'
        base64_attachment = Base64.base64_from_file(filename)
        content = [
            f'Content-Type: {content_type}; name={name}',
            f'Content-Disposition: attachment; filename={name}',
            f'Content-Transfer-Encoding: base64',
            '',
            f'{base64_attachment}'
        ]
        self.content = '\n'.join(content)
