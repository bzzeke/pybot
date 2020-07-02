import requests
import os
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from utils import serialize, unserialize

class Cry:
    MQTT_TOPIC = "/devices/util/controls/Cry Alarm/on"
    mqtt = None

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def ask(self, update, context):

        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data=self.generate_callback("1")),
                InlineKeyboardButton("No", callback_data=self.generate_callback("0")),
            ]
        ]

        update.message.reply_text(
            'Enable?',
            reply_markup=InlineKeyboardMarkup(keyboard))

    def enable(self, update, context):
        query = update.callback_query
        query.answer()
        payload = self.get_command(query.data)

        self.mqtt.publish(self.MQTT_TOPIC, payload)

        text = "Ok, alarm is *{}*".format("enabled" if payload == "1" else "disabled")
        query.bot.send_message(chat_id=query.message.chat.id, text = text, parse_mode="MarkdownV2")

    def generate_callback(self, payload):

        return serialize(
            "cry",
            "enable",
            payload
        )

    def get_command(self, payload):
        command, state, data = unserialize(payload)
        return data
