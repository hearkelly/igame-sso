#!/bin/sh

source venv/bin/activate

while true; do
    flask deploy
    if mycmd; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

exec waitress-serve --host 0.0.0.0 --port 8000 igame:app
