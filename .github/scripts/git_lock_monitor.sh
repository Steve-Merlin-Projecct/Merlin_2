#!/bin/bash
# Git Lock Monitor - Continuously monitors and removes git locks

echo "Starting git lock monitor (runs every 5 seconds)..."
echo "Press Ctrl+C to stop"

while true; do
    if [ -f .git/index.lock ] || [ -f .git/config.lock ]; then
        echo "$(date): Lock files detected, removing..."
        rm -f .git/index.lock .git/config.lock 2>/dev/null
        echo "$(date): Lock files cleaned"
    fi
    sleep 5
done
