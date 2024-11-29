#!/bin/bash

if [[ "$PLAYER_EVENT" != "playing" ]]; then
  exit 0
fi

curl -X POST http://10.0.0.171:8080/spotify --data '{"track_id": "$TRACK_ID"}'
