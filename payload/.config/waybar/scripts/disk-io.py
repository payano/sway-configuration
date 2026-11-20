#!/usr/bin/env python3
"""Report physical system-disk activity from kernel counters every two seconds."""
import json
from pathlib import Path
import time

STAT = Path('/sys/block/nvme0n1/stat')

def sample():
    fields = [int(value) for value in STAT.read_text().split()]
    return time.monotonic(), fields[2], fields[6], fields[9]

def rate(value):
    for unit in ('B/s', 'KiB/s', 'MiB/s', 'GiB/s'):
        if value < 1024 or unit == 'GiB/s':
            return f'{value:.1f} {unit}'
        value /= 1024

try:
    previous = sample()
    while True:
        time.sleep(2)
        current = sample()
        elapsed = current[0] - previous[0]
        read = max(0, current[1] - previous[1]) * 512 / elapsed
        write = max(0, current[2] - previous[2]) * 512 / elapsed
        busy = min(100, max(0, current[3] - previous[3]) / (elapsed * 10))
        print(json.dumps({
            'text': f'I/O {busy:3.0f}%',
            'tooltip': f'Systemdisk: nvme0n1\nAktiv tid: {busy:.0f}%\nLäsning: {rate(read)}\nSkrivning: {rate(write)}\nAktiv tid är inte procent av diskens maximala kapacitet.'
        }, ensure_ascii=False), flush=True)
        previous = current
except (BrokenPipeError, KeyboardInterrupt):
    pass
