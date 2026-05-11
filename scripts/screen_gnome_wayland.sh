#!/bin/bash
# zie https://gitlab.gnome.org/GNOME/mutter/-/blob/main/data/dbus-interfaces/org.gnome.Mutter.DisplayConfig.xml#L287
if [ x"$1" = x"on" ]; then
    /usr/sbin/rfkill unblock bluetooth
    gdbus call --session \
        --dest org.gnome.Mutter.DisplayConfig \
        --object-path /org/gnome/Mutter/DisplayConfig \
        --method org.freedesktop.DBus.Properties.Set \
        org.gnome.Mutter.DisplayConfig PowerSaveMode '<@i 0>'
    pactl set-sink-volume @DEFAULT_SINK@ 20%
elif [ x"$1" = x"off" ]; then
    /usr/sbin/rfkill block bluetooth
    gdbus call --session \
        --dest org.gnome.Mutter.DisplayConfig \
        --object-path /org/gnome/Mutter/DisplayConfig \
        --method org.freedesktop.DBus.Properties.Set \
        org.gnome.Mutter.DisplayConfig PowerSaveMode '<@i 3>'
else
    echo "Usage: $0 { on | off }" >&2
    exit 1
fi
