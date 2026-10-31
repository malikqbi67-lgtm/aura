import json
import urllib.request

MODEL = "qwen3:8b"
ALLOWED = ["TURN ON AC", "TURN OFF AC", "TURN ON LIGHT", "TURN OFF LIGHT"]

def ask_ai(user_text, sensors, devices):
    prompt = (
        "You control a smart room that has ONLY an AC and a light. "
        "Reply with JSON only, no extra text.\n"
        'Format: {"actions": [...], "reason": "short explanation in Arabic"}\n'
        "Allowed actions: " + json.dumps(ALLOWED) + "\n"
        "Sensors: " + json.dumps(sensors) + "\n"
        "Devices: " + json.dumps(devices) + "\n"
        "User says: " + user_text
    )
    body = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "format": "json"
    }).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=body,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        answer = json.loads(resp.read())["response"]
    result = json.loads(answer)
    # safety: keep only allowed actions
    result["actions"] = [a for a in result.get("actions", []) if a in ALLOWED]
    return result

if __name__ == "__main__":
    sensors = {"temperature": 33, "humidity": 60, "light": 400, "motion": True}
    devices = {"ac": False, "light": False}
    print(ask_ai("الجو حار وأريد أن أنام", sensors, devices))
