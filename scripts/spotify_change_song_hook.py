import os
import requests

if "PLAYER_EVENT" not in os.environ or os.environ["PLAYER_EVENT"] != "track_changed":
    exit(0)

try:
    requests.post('http://koin:9510/api/song', json={"spotify_id": str(os.environ['TRACK_ID'])})  # cammie scherm
except Exception:
    pass


import time

import paho.mqtt.client as mqtt


def on_publish(client, userdata, mid, reason_code, properties):
    try:
        userdata.remove(mid)
    except KeyError:
        print("Jammer")


unacked_publish = set()
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_publish = on_publish

mqttc.user_data_set(unacked_publish)
mqttc.connect("koin", 1883, 60)

mqttc.loop_start()

msg_info = mqttc.publish("zigbee2mqtt/bulb_1_2/set", '{"effect": "blink"}', qos=1)
unacked_publish.add(msg_info.mid)

while len(unacked_publish):
    time.sleep(0.1)

msg_info.wait_for_publish()

mqttc.disconnect()
mqttc.loop_stop()
