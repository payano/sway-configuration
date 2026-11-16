#!/usr/bin/env python3
"""Choose a PulseAudio/PipeWire output from the currently available sinks."""

import json
import subprocess


def pactl(*args):
    return subprocess.check_output(("pactl", *args), text=True).strip()


def main():
    sinks = json.loads(pactl("--format=json", "list", "sinks"))
    if not sinks:
        subprocess.run(("zenity", "--info", "--text=Inga ljudutgångar hittades."))
        return

    current = pactl("get-default-sink")
    command = [
        "zenity", "--list", "--radiolist", "--title=Välj ljudutgång",
        "--text=Välj var ljudet ska spelas upp:",
        "--column=Aktiv", "--column=Ljudutgång", "--column=Enhet",
        "--hide-column=3", "--print-column=3", "--width=450", "--height=260",
        "--ok-label=Välj", "--cancel-label=Avbryt", "--",
    ]
    names = set()
    for sink in sinks:
        name = sink["name"]
        names.add(name)
        command.extend(("TRUE" if name == current else "FALSE", sink["description"], name))

    choice = subprocess.run(command, text=True, capture_output=True)
    selected = choice.stdout.strip()
    if choice.returncode != 0 or selected not in names or selected == current:
        return

    subprocess.run(("pactl", "set-default-sink", selected), check=True)
    for line in pactl("list", "short", "sink-inputs").splitlines():
        input_id = line.split("\t", 1)[0]
        subprocess.run(("pactl", "move-sink-input", input_id, selected), check=True)


if __name__ == "__main__":
    main()
