#!/bin/bash
pkill -f esp32_sim.py
pkill -f "src/main.py"
pkill -f uvicorn
pkill -f "next dev"
pkill mosquitto
echo "AURA stopped"
