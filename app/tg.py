import time
import os

from telegram.ext import Updater, Dispatcher, JobQueue
from telegram import Bot
from queue import Queue
from threading import Thread

class Telegram(Thread):

    stop = False
    updater = None
    dispatcher = None
    bot = None

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        super(Telegram,self).__init__(group=group, target=target, name=name)

        if "DEBUG_BOT" in os.environ:
            self.updater = Updater(os.environ["BOT_TOKEN"], use_context=True)
            self.dispatcher = self.updater.dispatcher
            self.bot = self.updater.bot
        else:
            self.bot = Bot(os.environ["BOT_TOKEN"])
            self.dispatcher = Dispatcher(self.bot, None, use_context=True)
            self.bot.set_webhook(os.environ["BOT_HOOK_URL"])

    def run(self):

        if self.updater != None:
            self.updater.start_polling()

            while not self.stop:
                time.sleep(1)
