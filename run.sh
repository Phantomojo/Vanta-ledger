#!/bin/bash
# Activate virtual environment
source /home/mikey/vanta-ledger/env/bin/activate

# Set PYTHONPATH to the src directory
export PYTHONPATH=$PYTHONPATH:/home/mikey/vanta-ledger/src

# Run the app
python /home/mikey/vanta-ledger/src/vanta_ledger/main.py
