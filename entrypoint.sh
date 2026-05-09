#!/bin/bash
# If no args provided, use defaults
if [ $# -eq 0 ]; then
    set -- --browser chromium --port 5075 --headless --threads 2
fi

echo "=========================================="
echo "Starting Turnstile Solver"
echo "Args: $@"
echo "=========================================="
exec python main.py "$@"
