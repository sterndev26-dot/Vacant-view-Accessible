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

# Kill any existing instance to release GPIO
pkill -f "${SCRIPT_DIR}/run.py" 2>/dev/null || true
sleep 1

export DISPLAY="${DISPLAY:-:0}"

for i in $(seq 1 30); do
    xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break
    sleep 1
done

if ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
    echo "Display $DISPLAY not available after 30s, aborting."
    exit 1
fi

# Disable screen sleep
xset s off 2>/dev/null || true
xset -dpms 2>/dev/null || true
xset s noblank 2>/dev/null || true

cd "${SCRIPT_DIR}"

x-terminal-emulator -e bash -c "
    echo 'Activating virtual environment...';
    source ${SCRIPT_DIR}/venv/bin/activate;
    echo 'Running run.py...';
    python ${SCRIPT_DIR}/run.py;
    echo '';
    echo 'Done. Staying in virtual environment.';
    exec bash
"
