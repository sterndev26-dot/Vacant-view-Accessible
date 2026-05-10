#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "${SCRIPT_DIR}/venv/bin/activate" ]; then
    echo "Virtual environment not found at ${SCRIPT_DIR}/venv/bin/activate"
    exit 1
fi

if [ ! -f "${SCRIPT_DIR}/run.py" ]; then
    echo "run.py not found in ${SCRIPT_DIR}"
    exit 1
fi

cd "${SCRIPT_DIR}"

x-terminal-emulator -e bash -c '
    echo "Activating virtual environment...";
    source venv/bin/activate;
    echo "Running run.py...";
    python run.py;
    echo "";
    echo "Done. Staying in virtual environment.";
    exec bash
    '
