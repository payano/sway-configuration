#!/bin/sh
export XDG_CURRENT_DESKTOP=sway
export XDG_SESSION_TYPE=wayland
export GDK_BACKEND=wayland
exec python3 /home/jsv/.config/waybar/scripts/panel-supervisor.py "$@"
