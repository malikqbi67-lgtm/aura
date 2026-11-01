#!/bin/bash
cd ~/Documents/aura
source venv/bin/activate
mkdir -p logs

# Ollama (إن لم يكن يعمل)
curl -s http://localhost:11434 > /dev/null || (ollama serve > logs/ollama.log 2>&1 &)

/opt/homebrew/opt/mosquitto/sbin/mosquitto > logs/mosquitto.log 2>&1 &
sleep 2
python3 src/esp32_sim.py > logs/sim.log 2>&1 &
python3 src/main.py > logs/aura.log 2>&1 &
uvicorn src.api:app > logs/api.log 2>&1 &
(cd dashboard && npm run dev > ../logs/dashboard.log 2>&1 &)

echo "AURA is running. Open http://localhost:3000"
echo "Logs: tail -f logs/aura.log"
