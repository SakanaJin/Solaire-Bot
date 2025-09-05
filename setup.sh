#!/bin/bash

if [ ! -d ".venv" ]: then
    python3 -m venv .venv
fi

source .venv/bin/activate

if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found. Skipping package installation"
    exit 1
fi

pip install -r requirements.txt

deactivate


