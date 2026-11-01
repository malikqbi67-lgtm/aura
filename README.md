# AURA: Autonomous Smart Environment

AURA is a simulated smart room that senses its surroundings, understands the situation, makes decisions, and controls devices automatically. It combines IoT, AI, and automation, and runs entirely on a laptop without physical devices.

## Features

- Simulated sensors: temperature, humidity, light, motion
- Rule-based decision engine with safety rules (cooldown between device changes)
- ESP32 simulator communicating over MQTT
- Local AI (Ollama, qwen3:8b) that understands natural-language commands in Arabic
- Device commands with confirmation from the device
- Manual override: user commands pause automation for 5 minutes
- History stored in SQLite, served by a FastAPI backend
- Real-time Next.js dashboard with charts, decision log, manual buttons, and a chat box

## Architecture

```text
ESP32 simulator --MQTT--> AURA (decisions + safety) --MQTT commands--> ESP32 simulator
                              |
                           SQLite --> FastAPI --> Next.js dashboard
                              ^
                        Ollama (local LLM)
```

The AI only suggests actions. Safety rules and filters decide what is actually executed.

## Project Structure

```text
aura/
├── src/
│   ├── main.py        # decision engine, MQTT, storage
│   ├── ai.py          # local LLM integration
│   ├── esp32_sim.py   # simulated ESP32 device
│   └── api.py         # FastAPI backend
├── dashboard/         # Next.js dashboard
├── data/              # database and logs
├── run.sh             # start everything
└── stop.sh            # stop everything
```

## Requirements

- Python 3.10+
- Node.js
- Mosquitto (`brew install mosquitto`)
- Ollama with the `qwen3:8b` model

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install paho-mqtt fastapi uvicorn
cd dashboard && npm install && cd ..
ollama pull qwen3:8b
```

## Run

```bash
./run.sh
```

Then open http://localhost:3000. To stop everything:

```bash
./stop.sh
```

## API Endpoints

| Endpoint | Description |
|---|---|
| GET /state | Latest reading and device states |
| GET /readings | Historical readings |
| GET /events | AURA decisions log |
| POST /user | Send a natural-language message to AURA |
| POST /command | Manual device control |

## Roadmap

- Adaptive learning from history
- Multi-room support
- PostgreSQL and n8n workflows
- Real ESP32 and sensors

## Author

Malek
