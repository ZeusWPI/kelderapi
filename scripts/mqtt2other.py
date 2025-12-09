import json
import paho.mqtt.client as mqtt
import requests
import subprocess

broker_host = "localhost"
broker_port = 1883
topics = [
    "kelderapi/leddy",
    "zigbee2mqtt/all",
    "zigbee2mqtt/devices",
    "zigbee2mqtt/group_switch_devices",
]


def screen_on():
    print("running \"screen.sh on\"")
    subprocess.Popen(["/opt/kelderapi/screen.sh", "on"])

def screen_off():
    print("running \"screen.sh off\"")
    subprocess.Popen(["/opt/kelderapi/screen.sh", "off"])

def on_message(client, userdata, msg):
    print(f'Received message on topic "{msg.topic}"')
    try:
        payload_dict = json.loads(msg.payload)
    except json.JSONDecodeError:
        print(f"Failed to decode message as json: {msg}")
        return
    match msg.topic:
        case "kelderapi/leddy":
            username = payload_dict.get("username")
            data = f"ScrollingText Welkom {username}!"
            print(f"sending {data} to leddy")
            requests.post("http://leddy.kelder.local/", data)
        case "zigbee2mqtt/all" | "zigbee2mqtt/devices" | "zigbee2mqtt/group_switch_devices":
            action = payload_dict.get("action")
            state = payload_dict.get("state")
            if action == "on" or state == "ON":
                print("running \"screen.sh on\"")
                subprocess.Popen(["/opt/kelderapi/screen.sh", "on"])
            elif action == "off" or state == "OFF":
                print("running \"screen.sh off\"")
                subprocess.Popen(["/opt/kelderapi/screen.sh", "off"])
            else:
                return


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message

print(f"Connecting to {broker_host} {broker_port}")
client.connect(broker_host, broker_port, 1)

for topic in topics:
    print(f"Subscribing to {topic}")
    client.subscribe(topic)

client.loop_forever()
