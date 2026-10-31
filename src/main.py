import random

def read_sensors():
    sensors = {
        "temperature": random.randint(18, 40),
        "humidity": random.randint(30, 90),
        "light": random.randint(0, 800),
        "motion": random.choice([True, False])
    }
    return sensors

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

    return decisions

room = {
    "name": "Living Room",
    "sensors": read_sensors(),
    "devices": {
        "ac": False,
        "light": False
    }
}

print("Room:", room["name"])
print("Sensors:", room["sensors"])
print("Devices:", room["devices"])

decisions = decide(room)

print("--- AURA Decisions ---")
if len(decisions) == 0:
    print("No action needed")
for d in decisions:
    print(d)
