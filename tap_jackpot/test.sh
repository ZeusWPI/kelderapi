#!/bin/sh
set -euo pipefail
cd "$(dirname ${0})"

JACKPOTMSG="JACKPOT! JE VOLGENDE DRANKJE IS GRATIS, YIPPIE!"
LOSTMSG="Jammer, geen gratis drank deze keer"

# MQTT broker configuration
BROKER="localhost"     # change to your broker's hostname or IP
PORT="1883"            # default MQTT port
TOPIC="frigo/ordered"     # topic to subscribe to

TRIGGER_LOG_DIR="./trigger_log"
mkdir -p "${TRIGGER_LOG_DIR}"

export DISPLAY=:0

# Commands to run on each message
function jackpot
{
    echo "Triggered jackpot"
    local message="${1}"

    echo "${message}" > "${TRIGGER_LOG_DIR}/$(date --iso-8601=seconds)"

    if [ -n "${AUDIO}" ]; then
       (mpv --terminal=no --volume=100 jackpot.mp3 || true) &
    fi

    i3-msg "workspace 1;fullscreen toggle";
    sleep .5
    alacritty -o font.size=24 -e sh -c "dialog --timeout 12 --msgbox \"$JACKPOTMSG\" 12 30"
    sleep .5
    i3-msg "workspace 1;fullscreen toggle";
}

function lost
{
    echo "Triggered lost"
    local message="${1}"

    echo "${message}" > "${TRIGGER_LOG_DIR}/$(date --iso-8601=seconds)"

    i3-msg "workspace 1;fullscreen toggle";
    sleep .5
    alacritty -o font.size=24 -e sh -c "dialog --timeout 12 --msgbox \"$LOSTMSG\" 12 30"
    sleep .5
    i3-msg "workspace 1;fullscreen toggle";
}

function startup
{
    echo "Triggered lost"
    local message="${1}"

    echo "${message}" > "${TRIGGER_LOG_DIR}/$(date --iso-8601=seconds)"

    i3-msg "workspace 1;fullscreen toggle";
    sleep .5
    alacritty -o font.size=24 -e sh -c "dialog --timeout 12 --msgbox \"JACKPOT STARTUP\" 12 30"
    sleep .5
    i3-msg "workspace 1;fullscreen toggle";
}

echo "Tap jackpot started"
#AUDIO="" startup '["started"]'

AUDIO=y jackpot "test"

message=""
CHANCE=$((RANDOM % 100))
        if ((CHANCE < 1)); then
            mosquitto_pub -t tap_jackpot/roulette -m "win"
            sleep 30
            AUDIO=y jackpot "${message}"
        else
            mosquitto_pub -t tap_jackpot/roulette -m "lost"
            sleep 30
            lost "${message}"
        fi

# Subscribe and process messages 
last_message=""
mosquitto_sub -h "$BROKER" -p "$PORT" -t "$TOPIC" | jq -c --sort-keys --unbuffered '.' | while read -r message; do
    #if [ -z "${last_message}" ]; then
    #    echo "Skipping first message, might be a duplicate"
    #elif [ "${message}" = "${last_message}" ]; then
    #    echo "Skipping duplicate message"
    #else
        echo "Sale"
        CHANCE=$((RANDOM % 100))
        if ((CHANCE < 1)); then
            mosquitto_pub -t tap_jackpot/roulette -m "win"
            sleep 30
            AUDIO=y jackpot "${message}"
        else
            mosquitto_pub -t tap_jackpot/roulette -m "lost"
            sleep 30
            lost "${message}"
        fi
    #fi
    last_message="${message}"
done
