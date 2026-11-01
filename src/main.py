import random
import time
import sqlite3
from ai import ask_ai
import paho.mqtt.client as mqtt
import json
from datetime import datetime

COOLDOWN = 15
MANUAL_TIME = 300
manual_until = {"ac": 0, "light": 0}
last_change = {"ac": 0, "light": 0}

def read_sensors():
    return {
        "temperature": random.randint(18, 40),
        "humidity": random.randint(30, 90),
        "light": random.randint(0, 800),
        "motion": random.choice([True, False])
    }

def decide(room):
    sensors = room["sensors"]
    devices = room["devices"]
    decisions = []

    if sensors["temperature"] > 28 and sensors["motion"] and not devices["ac"]:
        decisions.append("TURN ON AC")
    if not sensors["motion"] and devices["ac"]:
        decisions.append("TURN OFF AC")
    if sensors["light"] < 100 and sensors["motion"] and not devices["light"]:
        decisions.append("TURN ON LIGHT")
    if not sensors["motion"] and devices["light"]:
        decisions.append("TURN OFF LIGHT")

    if sensors["temperature"] < 24 and devices["ac"] and "TURN OFF AC" not in decisions:
        decisions.append("TURN OFF AC")
    if sensors["light"] > 300 and devices["light"] and "TURN OFF LIGHT" not in decisions:
        decisions.append("TURN OFF LIGHT")

    return decisions

DB = "data/aura.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT, temperature INTEGER, humidity INTEGER,
        light INTEGER, motion INTEGER, ac INTEGER, light_on INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT, decision TEXT, result TEXT)""")
    conn.commit()
    conn.close()

def save_reading(room):
    s = room["sensors"]
    d = room["devices"]
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO readings (time, temperature, humidity, light, motion, ac, light_on) VALUES (?,?,?,?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s["temperature"], s["humidity"],
         s["light"], int(s["motion"]), int(d["ac"]), int(d["light"])))
    conn.commit()
    conn.close()

def save_event(decision, result):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO events (time, decision, result) VALUES (?,?,?)",
                 (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), decision, result))
    conn.commit()
    conn.close()

def log_event(decision, result, sensors):
    event = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "decision": decision,
        "result": result,
        "sensors": sensors
    }
    with open("data/log.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")

def execute(room, decisions):
    for d in decisions:
        device = "ac" if "AC" in d else "light"
        if time.time() - last_change[device] < COOLDOWN:
            print("BLOCKED (cooldown):", d)
            log_event(d, "BLOCKED", room["sensors"])
            continue
        last_change[device] = time.time()

        state = "TURN ON" in d
        client.publish("aura/room1/commands", json.dumps({"device": device, "state": state}))
        print("SENT COMMAND:", d)
        log_event(d, "SENT", room["sensors"])

room = {
    "name": "Living Room",
    "sensors": {},
    "devices": {"ac": False, "light": False}
}

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    if msg.topic == "aura/room1/user":
        text = data["text"]
        print("USER SAYS:", text)
        result = ask_ai(text, room["sensors"], room["devices"])
        print("AI SUGGESTS:", result["actions"], "|", result.get("reason", ""))
        for a in result["actions"]:
            dev = "ac" if "AC" in a else "light"
            manual_until[dev] = time.time() + MANUAL_TIME
            print("MANUAL MODE for", dev, "for", MANUAL_TIME, "seconds")
        execute(room, result["actions"])
        return
    if msg.topic == "aura/room1/status":
        room["devices"][data["device"]] = data["state"]
        print("CONFIRMED by device:", data)
    else:
        room["sensors"] = data

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("aura/room1/sensors")
client.subscribe("aura/room1/user")
client.subscribe("aura/room1/status")
client.loop_start()
print("AURA listening on aura/room1/sensors ...")

init_db()
last_seen = None

while True:
    if not room["sensors"] or room["sensors"] == last_seen:
        time.sleep(1)
        continue
    last_seen = dict(room["sensors"])
    save_reading(room)

    print("==============================")
    print("Sensors:", room["sensors"])
    print("Devices:", room["devices"])

    decisions = [d for d in decide(room)
                 if time.time() > manual_until["ac" if "AC" in d else "light"]]
    if len(decisions) == 0:
        print("No action needed")
    execute(room, decisions)

    time.sleep(3)
