#!/bin/bash

TARGET="localhost"

echo "Pinging $TARGET. Press Esc to stop."

while true; do
    curl -sS -o /dev/null -w "%{http_code}\n" http://localhost &
    curl_pid=$!
    sleep 1
    read -s -t 0.1 -n 1 key
    # Проверяем на Esc
    if [[ $key == $'\e' ]]; then
        kill $curl_pid
        break
    fi
    wait $curl_pid

done

echo "Ping stopped"
