import requests
import os

from telegram.ext import CommandHandler

from renderers.markdown import Markdown
from utils import log

class Temp:
    mqtt = None

    def __init__(self, telegram, mqtt):
        self.mqtt = mqtt
        telegram.dispatcher.add_handler(CommandHandler("temp", self.run))

    def run(self, update, context):

        r = requests.get(os.environ["MQTT_DASH"])
        topic_values = {}
        try:
            widgets = r.json()
            for widget in widgets["results"]:
                for control in widget["controls"]:
                    topic_values[control["statusTopic"]] = self.mqtt.get_value(control["statusTopic"])

            renderer = Markdown(topic_values, widgets["results"])
            update.message.reply_markdown(renderer.render())
        except Exception as e:
            log("[temp] JSON decode error: {}".format(e))
