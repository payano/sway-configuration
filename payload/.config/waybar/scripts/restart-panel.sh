#!/bin/sh
# Restart the supervised panel without Waybar's internal SIGUSR2 reload.
set -eu
kill -USR2 "$(cat "$XDG_RUNTIME_DIR/waybar-supervisor.pid")"
