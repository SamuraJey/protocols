import json


class Config:
    def __init__(self, filename=''):
        if filename:
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
                self.verbose = bool(conf['verbose'])
                
        else:
            self.mail_server = ''
            self.port = 0
            self.mail = ''
            self.fake_name = ''
            self.name = ''
            self.password = ''
            self.recipients = []
            self.message_file = ''
            self.subject = ''
            self.attachments = []
            self.verbose = False
