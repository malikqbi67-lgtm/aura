import json
import random
import time
import paho.mqtt.client as mqtt

SENSORS = "aura/room1/sensors"
COMMANDS = "aura/room1/commands"
STATUS = "aura/room1/status"

devices = {"ac": False, "light": False}

def on_message(client, userdata, msg):
    cmd = json.loads(msg.payload.decode())
    devices[cmd["device"]] = cmd["state"]
    print("Command received:", cmd)
    client.publish(STATUS, json.dumps({"device": cmd["device"], "state": devices[cmd["device"]]}))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe(COMMANDS)
client.loop_start()

print("ESP32 simulator started")

while True:
    reading = {
        "temperature": random.randint(18, 40),
        "humidity": random.randint(30, 90),
        "light": random.randint(0, 800),
        "motion": random.choice([True, False])
    }
    client.publish(SENSORS, json.dumps(reading))
    print("Sent:", reading, "| Devices:", devices)
    time.sleep(3)
