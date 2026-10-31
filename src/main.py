import random
import time
import json
from datetime import datetime

COOLDOWN = 15
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
    devices = room["devices"]
    for d in decisions:
        device = "ac" if "AC" in d else "light"
        if time.time() - last_change[device] < COOLDOWN:
            print("BLOCKED (cooldown):", d)
            log_event(d, "BLOCKED", room["sensors"])
            continue
        last_change[device] = time.time()

        if d == "TURN ON AC":
            devices["ac"] = True
        elif d == "TURN OFF AC":
            devices["ac"] = False
        elif d == "TURN ON LIGHT":
            devices["light"] = True
        elif d == "TURN OFF LIGHT":
            devices["light"] = False

        ok = (
            (d == "TURN ON AC" and devices["ac"])
            or (d == "TURN OFF AC" and not devices["ac"])
            or (d == "TURN ON LIGHT" and devices["light"])
            or (d == "TURN OFF LIGHT" and not devices["light"])
        )
        print("OK:" if ok else "FAILED:", d)
        log_event(d, "OK" if ok else "FAILED", room["sensors"])

room = {
    "name": "Living Room",
    "sensors": {},
    "devices": {"ac": False, "light": False}
}

while True:
    room["sensors"] = read_sensors()

    print("==============================")
    print("Sensors:", room["sensors"])
    print("Devices:", room["devices"])

    decisions = decide(room)
    if len(decisions) == 0:
        print("No action needed")
    execute(room, decisions)

    time.sleep(3)
