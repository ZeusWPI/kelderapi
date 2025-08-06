import json
import paho.mqtt.client as mqtt
import subprocess
import requests

broker_host = "localhost"
broker_port = 1883
sources = ["zigbee2mqtt/group_switch_devices", "zigbee2mqtt/devices", "zigbee2mqtt/all", "kelderapi/leddy"]

def on_message(client, userdata, msg):
    print("message received")
    try:
        payload_dict = json.loads(msg.payload)
        match msg.topic:
            case "zigbee2mqtt/group_switch_devices" | "zigbee2mqtt/devices" | "zigbee2mqtt/all":
                action = payload_dict.get("action")
                state = payload_dict.get("state")

                if action == "on" or state == "ON":
                    subprocess.Popen(["/opt/kelderapi/screen.sh", "on"])
                elif action == "off" or state == "OFF":
                    subprocess.Popen(["/opt/kelderapi/screen.sh", "off"])
                else:
                    return
            case "kelderapi/leddy":
                username = payload_dict.get("username")
                requests.post("http://leddy.kelder.local/", data=f"Option autoResetMs {5 * 1000}")
                requests.post("http://leddy.kelder.local/", data=f"ScrollingText Welkom {username}!")
                

    except json.JSONDecodeError:
        print(f"Failed to decode message as json: {msg}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(broker_host, broker_port, 60)

for source in sources:
    client.subscribe(f"{source}")

client.loop_forever()
