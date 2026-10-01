#!/bin/bash
# LifePulse - Quick Launch Script

echo "=========================================================="
echo "🩸 LifePulse - Blood Donor Finder Application"
echo "=========================================================="

cd "$(dirname "$0")"

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# Ensure database is initialized
if [ ! -f "blood_donor.db" ]; then
    echo "Initializing database with sample donors & urgent requests..."
    ./venv/bin/python database.py
fi

echo ""
echo "Starting Flask Server (http://127.0.0.1:5000 or http://127.0.0.1:5001) ..."
echo "Press Ctrl+C to stop the server."
echo ""

./venv/bin/python app.py
