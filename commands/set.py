import requests
import os
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler

from utils import serialize, unserialize

class Set:

    mqtt = None
    TOPIC_TEMPLATE = "/devices/thermostat/controls/{}/on"
    TOPICS = {
        "Floor_1": {
            "text": "1st floor t˚C",
            "type": "temperature"
        },
        "Floor_2": {
            "text": "2nd floor t˚C",
            "type": "temperature"
        },
        "Basement": {
            "text": "Basement t˚C",
            "type": "temperature"
        },
        "Enabled": {
            "text": "Boiler state",
            "type": "switch",
            "vars": ["Off", "On"]
        },
        "Simple": {
            "text": "Heating mode",
            "type": "switch",
            "vars": ["Extended", "Simple"]
        }
    }


    def __init__(self, mqtt):
        self.mqtt = mqtt

    def select_topic(self, update, context):

        keyboard = [
            [
                InlineKeyboardButton(self.TOPICS["Floor_1"]["text"], callback_data=self.generate_callback("topic", "Floor_1")),
                InlineKeyboardButton(self.TOPICS["Floor_2"]["text"], callback_data=self.generate_callback("topic", "Floor_2")),
                InlineKeyboardButton(self.TOPICS["Basement"]["text"], callback_data=self.generate_callback("topic", "Basement"))
            ],
            [
                InlineKeyboardButton(self.TOPICS["Enabled"]["text"], callback_data=self.generate_callback("topic", "Enabled")),
                InlineKeyboardButton(self.TOPICS["Simple"]["text"], callback_data=self.generate_callback("topic", "Simple"))
            ]
        ]

        update.message.reply_text(
            "Select option:",
            reply_markup=InlineKeyboardMarkup(keyboard))

        return "publish"

    def set_value(self, update, context):
        query = update.callback_query
        query.answer()
        topic = self.get_command(query.data)
        context.user_data['topic'] = topic

        if self.TOPICS[topic]["type"] == "switch":
            keyboard = [
                [
                    InlineKeyboardButton(self.TOPICS[topic]["vars"][1], callback_data=self.generate_callback("value", "1")),
                    InlineKeyboardButton(self.TOPICS[topic]["vars"][0], callback_data=self.generate_callback("value", "0"))
                ]
            ]

            query.bot.send_message(chat_id=query.message.chat.id, text="Set {}:".format(self.TOPICS[topic]["text"]), parse_mode="MarkdownV2", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            query.bot.send_message(chat_id=query.message.chat.id, text="Set temperature for {}".format(self.TOPICS[topic]["text"]), parse_mode="MarkdownV2")

        return "publish"

    def publish(self, update, context):

        if "topic" not in context.user_data:
            return

        topic = context.user_data["topic"]
        query = update.callback_query
        if query != None:
            query.answer()
            payload = self.get_command(query.data)
        else:
            payload = update.message.text

        if self.TOPICS[topic]["type"] == "switch":
            text = "Ok, {} set to *{}*".format(self.TOPICS[topic]["text"], self.TOPICS[topic]["vars"][int(payload)])
        elif self.TOPICS[topic]["type"] == "temperature":
            text = "Ok, {} temperature set to *{}*".format(self.TOPICS[topic]["text"], payload)

        self.mqtt.publish(self.TOPIC_TEMPLATE.format(topic), payload)

        if query != None:
            query.bot.send_message(chat_id=query.message.chat.id, text = text, parse_mode="MarkdownV2")
        else:
            update.message.reply_markdown(text)

        return ConversationHandler.END

    def generate_callback(self, type, payload):

        return serialize(
            "set",
            type,
            payload
        )

    def get_command(self, payload):
        command, state, data = unserialize(payload)
        return data
