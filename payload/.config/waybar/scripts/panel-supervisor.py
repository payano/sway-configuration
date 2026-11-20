#!/usr/bin/env python3
"""Keep one panel instance; SIGUSR2 performs a clean restart, not a Waybar reload."""
import fcntl
import os
from pathlib import Path
import signal
import subprocess
import sys

runtime = Path(os.environ['XDG_RUNTIME_DIR'])
lock = (runtime / 'waybar-supervisor.lock').open('w')
try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    sys.exit(0)
pidfile = runtime / 'waybar-supervisor.pid'
pidfile.write_text(str(os.getpid()))
child = None
restart = False
stopping = False

def handle(signum, frame):
    global restart, stopping
    if signum == signal.SIGUSR1:
        if child is not None and child.poll() is None:
            child.send_signal(signum)
        return
    if signum == signal.SIGUSR2:
        restart = True
    else:
        stopping = True
    if child is not None and child.poll() is None:
        child.send_signal(signal.SIGINT)

for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGUSR1, signal.SIGUSR2):
    signal.signal(sig, handle)

try:
    while not stopping:
        restart = False
        child = subprocess.Popen(['/usr/bin/waybar', *sys.argv[1:]], start_new_session=True)
        child.wait()
        # Also stop custom-module descendants if the panel left any behind.
        try:
            os.killpg(child.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        if not restart:
            break
finally:
    pidfile.unlink(missing_ok=True)
