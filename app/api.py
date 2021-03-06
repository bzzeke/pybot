import sys
import socket
import time
import json
import os
import copy
import urllib
import shutil
import re
import datetime as dt
import requests
import tempfile
import base64

from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from util import log, serialize

class ApiHTTPServer(ThreadingMixIn, HTTPServer):
    telegram = None

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, telegram=None):
        super(ApiHTTPServer, self).__init__(server_address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.telegram = telegram

class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.respond()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        request_body = self.rfile.read(content_length)
        self.respond(request_body.decode("utf-8"))

    def respond(self, request_body=None):
        path = urllib.parse.unquote(self.path).strip("/")
        path = path.split("/")
        method = path[0]
        del path[0]

        if hasattr(self, method):
            if request_body == None:
                response = getattr(self, method)(path)
            else:
                response = getattr(self, method)(path, request_body)

            if response != None:
                try:
                    if type(response) == str:
                        response = response.encode("utf-8")
                    self.wfile.write(response)
                except:
                    pass
        else:
            self.send_response(404)
            self.end_headers()

class ApiHandler(HTTPHandler):


    def cd(self, args, body):
        url = os.environ["CD_REMOTE_SERVER"] if args[0] == "remote" else os.environ["CD_LOCAL_SERVER"]

        response = {
            "status": "failed",
            "error": "Empty request"
        }

        try:
            payload = json.loads(body)
            r = requests.post(url, json=payload)

            response["status"] = "ok" if r.status_code == 200 else "failed"
            response["error"] = "" if r.status_code == 200 else r.status_code

        except Exception as e:
            response["error"] = str(e)

        self.send_response(200 if response["status"] == "ok" else 503)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        return json.dumps(response)


    def hook(self, args, body):

        if args[0] == "process":
            self.server.telegram.dispatcher.process_update(Update.de_json(json.loads(body), self.server.telegram.bot))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            return json.dumps(["ok"])

    def notify(self, args, body):
        MAX_MESSAGE_LENGTH = 4096
        response = {
            "status": "ok",
            "error": ""
        }

        if args[0] == "general":

            '''
            data structure:
            {
                text: 'message',
                parse_mode: 'Markdown',
                attachments: [
                    file1_base64,
                    file2_base64
                ],
                meta: {
                    surveillance: [
                        [camera1, timestamp1],
                        [camera2, timestamp2],
                    ]
                }
            }
            '''
            try:
                payload = json.loads(body)
                chat_ids = os.environ["CHAT_IDS"].split(",")
                file = None

                if len(payload['text']) > MAX_MESSAGE_LENGTH:
                    file = tempfile.TemporaryFile()
                    file.write(payload["text"].encode())
                    file.seek(0)

                for chat_id in chat_ids:
                    if file == None:
                        self.server.telegram.bot.send_message(chat_id=chat_id, text=payload["text"], parse_mode=payload["parse_mode"] if "parse_mode" in payload else "")
                    else:
                        self.server.telegram.bot.send_document(chat_id=chat_id, document=file, filename="message.txt", parse_mode=payload["parse_mode"] if "parse_mode" in payload else "")

                    if "attachments" in payload:
                        for index, attachment in enumerate(payload["attachments"]):
                            file = tempfile.TemporaryFile()
                            file.write(base64.decodebytes(attachment.encode()))
                            file.seek(0)

                            reply_markup = None
                            if "meta" in payload and "surveillance" in payload["meta"]:
                                camera, timestamp = tuple(payload["meta"]["surveillance"][index])
                                reply_markup = InlineKeyboardMarkup([
                                    [InlineKeyboardButton("Get video", callback_data=serialize("video", "{}_{}".format(camera, timestamp)))]
                                ])

                            self.server.telegram.bot.send_photo(chat_id=chat_id, photo = file, reply_markup=reply_markup)

                response["status"] = "ok"

            except Exception as e:
                response["error"] = str(e)
                response["status"] = "failed"

        self.send_response(200 if response["status"] == "ok" else 503)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        return json.dumps(response)


class ApiServer(Thread):
    httpd = None
    telegram = None

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, telegram=None):
        super(ApiServer,self).__init__(group=group, target=target, name=name)
        self.telegram = telegram

    def run(self):
        log("[api] Starting service")
        self.httpd = ApiHTTPServer((os.environ["API_SERVER_HOST"], int(os.environ["API_SERVER_PORT"])), ApiHandler, telegram=self.telegram)
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass

        self.httpd.server_close()

    def stop(self):
        self.httpd.shutdown()