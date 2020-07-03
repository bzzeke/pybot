import paho.mqtt.client as mqtt
import os

from util import log

class Mqtt:
    SUBSCRIBE_TOPIC = "/devices/+/controls/+"
    TIMEOUT = 10
    client = None
    state = {}

    def __init__(self):
        self.client = mqtt.Client("bot")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(os.environ["MQTT_HOST"], int(os.environ["MQTT_PORT"]), self.TIMEOUT)
            self.client.loop_start()
        except Exception as e:
            log("[mqtt] Failed to connect: {}".format(e))


    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            return

        log("[mqtt] subscribed to topic {}".format(self.SUBSCRIBE_TOPIC))
        client.subscribe(self.SUBSCRIBE_TOPIC)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        self.state[msg.topic] = payload

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def get_value(self, topic):
        return self.state[topic] if topic in self.state else ""
