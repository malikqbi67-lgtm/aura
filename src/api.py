import json
import sqlite3
import paho.mqtt.client as mqtt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "data/aura.db"

mq = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mq.connect("localhost", 1883)
mq.loop_start()

def query(sql, args=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/state")
def state():
    rows = query("SELECT * FROM readings ORDER BY id DESC LIMIT 1")
    return rows[0] if rows else {}

@app.get("/readings")
def readings(limit: int = 60):
    return query("SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,))

@app.get("/events")
def events(limit: int = 20):
    return query("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))

class UserMessage(BaseModel):
    text: str

@app.post("/user")
def user(msg: UserMessage):
    mq.publish("aura/room1/user", json.dumps({"text": msg.text}))
    return {"sent": msg.text}
