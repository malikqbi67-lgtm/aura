import json
import random
import time
import paho.mqtt.client as mqtt

TOPIC = "aura/room1/sensors"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883)
client.loop_start()

print("ESP32 simulator started. Publishing to", TOPIC)

while True:
    reading = {
        "temperature": random.randint(18, 40),
        "humidity": random.randint(30, 90),
        "light": random.randint(0, 800),
        "motion": random.choice([True, False])
    }
    client.publish(TOPIC, json.dumps(reading))
    print("Sent:", reading)
    time.sleep(3)
