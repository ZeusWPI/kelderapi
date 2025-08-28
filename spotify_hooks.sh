#!/usr/bin/env bash

# --------------------------------------------------
# hooks for spotify song change
#
# environment variables available:
# PLAYER_EVENT -- type of event ( track_changed | ...? idk )
# TRACK_ID -- spotify id of track
#
# variables from .env are also available (they get exported here as well)
# 
# use absolute paths !!!
# --------------------------------------------------  

mosquitto_pub -t music/librespot_debug -m "$(env | grep -vF -ePULSE_ -e{/usr,/sys,/run,/home,LC_,LANG=,JOURNAL,SYSTEM,RUST,LC_,JOURNAL,SYSTEMD,SHLVL=,USER=,PID=,MEMORY_,LOGNAME=,EDITOR=} | sort)"

IFS='\t\n'

source /opt/kelderapi/.env
export SPOTIFY_CLIENT_ID
export SPOTIFY_CLIENT_SECRET


### hook functions ###

lights_screen() {
    /opt/kelderapi/env/bin/python /opt/kelderapi/scripts/spotify_change_song_hook.py
}


led_strip() {
    /opt/kelderapi/get_song_duration "$TRACK_ID" \
        | xargs -I {} curl \
            -s \
            -X PUT \
            -H 'Content-Type: application/json' \
            --data '{"topic": "spotify_progress", "message": "{}"}' \
            'http://ledstrip/api/mailbox.json'
}


mqtt_publish() {
    case "${PLAYER_EVENT}" in
        "volume_changed")
            payload="{\"volume\":$(bc <<<"${VOLUME}*100/65535")}"
            ;;
        "shuffle_changed")
            payload="{\"shuffle\":${SHUFFLE}}"
            ;;
        "repeat_changed")
            payload="{\"repeat\":${REPEAT}}"
            ;;
        "auto_play_changed")
            payload="{\"autoPlay\":${AUTO_PLAY}}"
            ;;
        "track_changed")
            payload="{\"itemType\":\"${ITEM_TYPE}\",\"trackId\":\"${TRACK_ID}\"}"
            ;;
        "playing"|"paused"|"seeked"|"position_correction")
            payload="{\"trackId\":\"${TRACK_ID}\",\"positionMs\":${POSITION_MS}}"
            ;;
        "unavailable"|"end_of_track"|"preload_next"|"loading"|"stopped")
            payload="{\"trackId\":\"${TRACK_ID}\"}"
            ;;
        *)
            payload=""
            ;;
    esac
    if [[ -n "${payload}" ]]; then
        mosquitto_pub -t "music/events/${PLAYER_EVENT}" -m "${payload}"
    fi
}

### call functions here ###
{
    set -euo pipefail
    #set -x
    echo "===================="
    echo "Got event ${PLAYER_EVENT}"

    echo "Running lights_screen"
    lights_screen

    if [[ $PLAYER_EVENT = 'track_changed' ]]; then
        echo "Running led_strip"
        led_strip
    fi

    echo "Running mqtt_publish"
    mqtt_publish

    echo "===================="
} &>>/tmp/spotify_hook.log
