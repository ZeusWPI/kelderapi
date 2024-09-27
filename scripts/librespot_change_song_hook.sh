#!/bin/bash

PLAYER_EVENT="changed"
TRACK_ID="6rPO02ozF3bM7NnOV4h6s2"

if [[ "$PLAYER_EVENT" != "changed" ]]; then
  exit 0
fi

curl -X POST http://10.0.0.171:8080/spotify --data '{"track_id": "$TRACK_ID"}'
