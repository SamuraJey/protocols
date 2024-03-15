import json


class Config:
    def __init__(self, filename: str):
        with open(filename, encoding='utf8') as config:
            conf = json.load(config)
            self.mail_server = conf['mail_server'].split(':')[0]
            self.port = int(conf['mail_server'].split(':')[-1])
            self.mail = conf['mail']
            self.fake_name = conf['name']
            self.name = conf['name']
            self.password = conf['password']
            self.recipients = conf['recipients']
            self.message_file = conf['message_file']
            self.subject = conf['subject']
            self.attachments = conf['attachments']
            self.verbose = self.to_bool(conf['verbose'])
            # print(conf['verbose'])
            
    def to_bool(self, string):
        if string == 'True':
            return True
        else:
            return False
