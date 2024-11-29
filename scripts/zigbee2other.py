import json
import paho.mqtt.client as mqtt
import subprocess

broker_host = "localhost"
broker_port = 1883
topic_base = "zigbee2mqtt"
sources = ["group_switch_devices", "devices", "all"]

def on_message(client, userdata, msg):
    print("message received")
    try:
        payload_dict = json.loads(msg.payload)
        action = payload_dict.get("action")
        state = payload_dict.get("state")

        if action == "on" or state == "ON":
            subprocess.Popen(["/opt/kelderapi/screen.sh", "on"])
        elif action == "off" or state == "OFF":
            subprocess.Popen(["/opt/kelderapi/screen.sh", "off"])
        else:
            return

    except json.JSONDecodeError:
        print(f"Failed to decode message as json: {msg}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(broker_host, broker_port, 60)

for source in sources:
    client.subscribe(f"{topic_base}/{source}")

client.loop_forever()
