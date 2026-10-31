room = {
    "name": "Living Room",
    "sensors": {
        "temperature": 31,
        "humidity": 55,
        "light": 200,
        "motion": True
    },
    "devices": {
        "ac": False,
        "light": False
    }
}

print("Room:", room["name"])
print("Temperature:", room["sensors"]["temperature"])
print("Motion:", room["sensors"]["motion"])
print("AC on?", room["devices"]["ac"])