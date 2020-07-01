import requests
import os
import traceback

from renderers.markdown import Markdown

class Temp:
    mqtt = None

    def __init__(self, mqtt):
        self.mqtt = mqtt

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
            print("JSON decode error: {}".format(e))
            traceback.print_exc()
