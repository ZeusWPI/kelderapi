#!/bin/bash
export DISPLAY=${DISPLAY:-:$(ls -v /tmp/.X11-unix/ | head -n 1 | cut -dX -f2)}
if [ x"$1" = x"on" ]; then
	xset dpms force on
	xset s off
	xset s noblank
	xset -dpms
elif [ x"$1" = x"off" ]; then
	xset dpms force off
fi
