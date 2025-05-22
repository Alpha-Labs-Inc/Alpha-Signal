#!/bin/bash
set -e

# Start API service in background
python alphasignal/app.py &
PID_APP=$!

# Start order processor in background
python alphasignal/processor.py &
PID_PROCESSOR=$!

# Start ngrok in unbuffered mode in background so its output appears in logs
python -u alphasignal/ngrok_run.py &
PID_NGROK=$!

# Wait for all background processes to finish
# Wait for all background processes to finish
wait $PID_APP $PID_PROCESSOR $PID_NGROK

# Then print the last few lines of the ngrok log
echo "=== ngrok logs (last 20 lines) ==="
tail -n 1 ngrok.log
