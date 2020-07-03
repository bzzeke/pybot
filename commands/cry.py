import requests
import os
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

from utils import serialize, unserialize

class Cry:
    CRY_CALLBACK_ID = "cry"
    MQTT_TOPIC = "/devices/util/controls/Cry Alarm/on"
    mqtt = None

    def __init__(self, dispatcher, mqtt):
        self.mqtt = mqtt
        dispatcher.add_handler(CommandHandler("cry", self.ask))
        dispatcher.add_handler(CallbackQueryHandler(self.enable, pattern="^{}\:.*$".format(self.CRY_CALLBACK_ID)))

    def ask(self, update, context):

        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data=serialize(self.CRY_CALLBACK_ID, "1")),
                InlineKeyboardButton("No", callback_data=serialize(self.CRY_CALLBACK_ID, "0")),
            ]
        ]

        update.message.reply_text(
            'Enable?',
            reply_markup=InlineKeyboardMarkup(keyboard))

    def enable(self, update, context):
        query = update.callback_query
        query.answer()
        id, payload = unserialize(query.data)

        self.mqtt.publish(self.MQTT_TOPIC, payload)

        text = "Ok, alarm is *{}*".format("enabled" if payload == "1" else "disabled")
        query.bot.send_message(chat_id=query.message.chat.id, text = text, parse_mode="MarkdownV2")
