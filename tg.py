import time
import os

from telegram.ext import Updater
from threading import Thread

class Telegram(Thread):

    stop = False
    updater = None
    dispatcher = None
    bot = None

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        super(Telegram,self).__init__(group=group, target=target, name=name)
        self.updater = Updater(os.environ["BOT_TOKEN"], use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.bot = self.updater.bot

    def run(self):

        self.updater.start_polling()

        while not self.stop:
            time.sleep(1)
