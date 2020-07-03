import requests
import os
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, Filters

from utils import serialize, unserialize

class Set:

    mqtt = None
    TOPIC_CALLBACK_ID = "settopic"
    VALUE_CALLBACK_ID = "setvalue"

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


    def __init__(self, dispatcher, mqtt):
        self.mqtt = mqtt
        dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler('set', self.select_topic)],

            states={
                "publish": [MessageHandler(Filters.all, self.publish)],
            },
            fallbacks = []
        ))
        dispatcher.add_handler(CallbackQueryHandler(self.set_value, pattern="^{}\:.*$".format(self.TOPIC_CALLBACK_ID)))
        dispatcher.add_handler(CallbackQueryHandler(self.publish, pattern="^{}\:.*$".format(self.VALUE_CALLBACK_ID)))

    def select_topic(self, update, context):

        keyboard = [
            [
                InlineKeyboardButton(self.TOPICS["Floor_1"]["text"], callback_data=serialize(self.TOPIC_CALLBACK_ID, "Floor_1")),
                InlineKeyboardButton(self.TOPICS["Floor_2"]["text"], callback_data=serialize(self.TOPIC_CALLBACK_ID, "Floor_2")),
                InlineKeyboardButton(self.TOPICS["Basement"]["text"], callback_data=serialize(self.TOPIC_CALLBACK_ID, "Basement"))
            ],
            [
                InlineKeyboardButton(self.TOPICS["Enabled"]["text"], callback_data=serialize(self.TOPIC_CALLBACK_ID, "Enabled")),
                InlineKeyboardButton(self.TOPICS["Simple"]["text"], callback_data=serialize(self.TOPIC_CALLBACK_ID, "Simple"))
            ]
        ]

        update.message.reply_text(
            "Select option:",
            reply_markup=InlineKeyboardMarkup(keyboard))

        return "publish"

    def set_value(self, update, context):
        query = update.callback_query
        query.answer()
        id, topic = unserialize(query.data)
        context.user_data['topic'] = topic

        if self.TOPICS[topic]["type"] == "switch":
            keyboard = [
                [
                    InlineKeyboardButton(self.TOPICS[topic]["vars"][1], callback_data=serialize(self.VALUE_CALLBACK_ID, "1")),
                    InlineKeyboardButton(self.TOPICS[topic]["vars"][0], callback_data=serialize(self.VALUE_CALLBACK_ID, "0"))
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
            id, payload = unserialize(query.data)
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
