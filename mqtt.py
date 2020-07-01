import paho.mqtt.client as mqtt
import os

class Mqtt:
    SUBSCRIBE_TOPIC = "/devices/+/controls/+"
    client = None
    state = {}

    def __init__(self):
        self.client = mqtt.Client("bot")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(os.environ["MQTT_HOST"], int(os.environ["MQTT_PORT"]), 10)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            return

        print("MQTT subscribed")
        client.subscribe(self.SUBSCRIBE_TOPIC)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        self.state[msg.topic] = payload
        # print("Got message: {} -> {}".format(msg.topic, payload))

    def get_value(self, topic):
        return self.state[topic] if topic in self.state else ""
