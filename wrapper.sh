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

export DISPLAY="${DISPLAY:-:0}"

for i in $(seq 1 30); do
    xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break
    sleep 1
done

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
