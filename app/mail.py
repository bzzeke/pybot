import os
import requests
import email
import base64
import time
import asyncore
import re

from smtpd import SMTPServer
from threading import Thread

from util import log

class EMailServer(SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):

        if not self.is_valid_recipient(rcpttos[0]):
            return

        message = email.message_from_bytes(data)
        notification = {
            "text": "",
            "attachments": []
        }

        body = []
        for part in message.walk():

            if part.get_content_type() == 'text/plain':
                body.append(part.get_payload(decode=True).decode())
                continue

            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            notification["attachments"].append(base64.b64encode(part.get_payload(decode=True)).decode())

        notification["text"] = "".join(body)

        requests.post("http://{}:{}/notify/general".format(os.environ["API_SERVER_HOST"], os.environ["API_SERVER_PORT"]), json=notification)

    def is_valid_recipient(self, recipient):
        return re.match(os.environ["SMTP_VALID_EMAIL"], recipient) != None


class MailServer(Thread):
    smtp = None

    def run(self):
        log("[mail_server] Starting service")

        self.smtp = EMailServer((os.environ["API_SERVER_HOST"], int(os.environ["MAIL_PORT"])), None)

        asyncore.loop()

    def stop(self):
        self.smtp.close()
