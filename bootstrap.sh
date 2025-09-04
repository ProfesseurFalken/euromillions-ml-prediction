#!/usr/bin/env bash
set -e
PY=${PY:-python3}; REQ=${REQ:-requirements.txt}
echo ">>> Checking Python..."; $PY -V >/dev/null 2>&1 || { echo "Install Python 3.11"; exit 1; }
echo ">>> Creating venv..."; $PY -m venv .venv
echo ">>> Activating + upgrading pip..."; source .venv/bin/activate; python -m pip install --upgrade pip
echo ">>> Installing requirements..."; [ -f "$REQ" ] || { echo "requirements.txt missing"; exit 1; }; pip install -r "$REQ"
echo ">>> Ensuring .env and folders..."; [ -f ".env" ] || { [ -f ".env.example" ] && cp .env.example .env || true; }; mkdir -p data data/raw data/processed models/euromillions
echo ">>> Bootstrap done. Launching UI..."; streamlit run ui/streamlit_app.py
