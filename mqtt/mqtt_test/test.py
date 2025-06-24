import numpy as np
import json, random
from paho.mqtt.client import Client
import time, base64
from multiprocessing import Event

connect_event = Event()


def on_connect(client, userdata, flags, rc):

    print("Connected with result code %s." % str(rc))
    connect_event.set()


if __name__ == "__main__":

    client = Client()

    ip = "140.112.45.232"
    # ip = "0.0.0.0"
    port = 1883

    client.on_connect = on_connect
    client.connect(ip, port, 60)

    client.loop_start()
    connect_event.wait()
    while True:
        client.publish("radar", json.dumps({
            'id': [f"testffasfasas"], 
            'azm': [random.randint(0,180)],
            'elv': [45.0],
            'color':['#ffff00']
        }), qos=0)
        print('Push radar')

        # with open(f'./mqtt/mqtt_test/test{random.randint(1,2)}.png', 'rb') as image_file: 
        #     base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        # client.publish("target", json.dumps({
        #     'fig': base64_image
        # }), qos=0)
        # client.publish("ant", json.dumps({
        #     'fig': base64_image
        # }), qos=0)
        # client.publish("pf", json.dumps({
        #     'fig': base64_image
        # }), qos=0)
        # # print('Push spec')

        # client.publish("message", json.dumps({
        #     'level': 'DEBUG',
        #     'text': 'This is text\nsperate'
        # }), qos=0)
        # client.publish("ant", json.dumps({
        #     "powers": [-20.1, -14.1, 10.5, None, None, None, None, None, -12.0, -4.5, None, None, None, None, None, None],
        #     "received": [None, None, 0, 4.3, 3.5, None, None, None, None, None, None, None, None, None, None],
        #     "selected": [0, 1, 8, 9],
        # }), qos=0)

        # time.sleep(1)

        # client.publish("ant", json.dumps({
        #     "powers": [None, None, None, -20.1, -14.1, '123\n1', None, None, None, None, -12.0, -4.5, None, None, None, None],
        #     "received": [None,None, None, None, None, 0, 4.3, 3.5, None, None, None, None, None, None, None],
        #     "selected": [2,4,6,8],
        # }), qos=0)

        time.sleep(1)