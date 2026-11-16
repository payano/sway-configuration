#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
dry=0; config_only=0; distro=''
usage() {
  echo 'Usage: ./install.sh [--dry-run] [--distro debian|arch] [--config-only]'
  echo '--distro is only allowed with --dry-run. Run as your normal user, not sudo.'
}
while (($#)); do
  case "$1" in
    --dry-run) dry=1 ;;
    --config-only) config_only=1 ;;
    --distro) shift; distro=${1:?Missing distro} ;;
    -h|--help) usage; exit 0 ;;
    *) usage; exit 2 ;;
  esac
  shift
done
if [[ -n "$distro" && "$dry" = 0 ]]; then echo '--distro requires --dry-run' >&2; exit 2; fi
if [[ -z "$distro" ]]; then
  . /etc/os-release
  distro=$ID
  if [[ "$ID" = debian && "${VERSION_ID%%.*}" != 13 ]]; then
    echo 'This installer supports Debian 13 and Arch Linux.' >&2; exit 1
  fi
fi
case "$distro" in debian|arch) ;; *) echo "Unsupported distribution: $distro" >&2; exit 1 ;; esac
mapfile -t packages < "packages.$distro"
printf 'Distribution: %s\nPackages: %s\n' "$distro" "${packages[*]}"
echo 'Configuration: Sway, Waybar, Dunst, Foot, Kanshi and helper scripts.'
echo 'Existing files will be backed up under ~/.local/state/sway-portable/backups/.'
if ((dry)); then
  if [[ "$distro" = arch ]]; then echo 'Command: sudo pacman -Syu --needed <packages> (full system upgrade)';
  else echo 'Commands: sudo apt-get update; sudo apt-get install <packages>'; fi
  echo 'Enable NetworkManager and Bluetooth for next boot. Enable PipeWire user sockets.'
  exit 0
fi
if ((EUID == 0)); then echo 'Run without sudo; the script invokes sudo for system changes.' >&2; exit 1; fi
if [[ "${XDG_CONFIG_HOME:-$HOME/.config}" != "$HOME/.config" ]]; then
  echo 'Custom XDG_CONFIG_HOME is not supported.' >&2; exit 1
fi
# Paths are substituted into shell and Sway commands; refuse unsafe characters.
if [[ ! "$HOME" =~ ^/[a-zA-Z0-9_./-]+$ ]]; then echo 'HOME contains unsupported characters.' >&2; exit 1; fi
if ((!config_only)); then
  command -v sudo >/dev/null || { echo 'Install sudo and grant this user sudo access first.' >&2; exit 1; }
  # Do not silently create competing network managers.
  for service in systemd-networkd.service dhcpcd.service connman.service iwd.service; do
    if systemctl is-active --quiet "$service"; then
      echo "Active network service: $service. Configure migration to NetworkManager first, or use --config-only." >&2
      exit 1
    fi
  done
  sudo -v
  if [[ "$distro" = debian ]]; then
    sudo apt-get update
    sudo apt-get install "${packages[@]}"
  else
    sudo pacman -Syu --needed "${packages[@]}"
  fi
fi
command -v python3 >/dev/null || { echo 'python3 is required for --config-only.' >&2; exit 1; }
python3 deploy.py
if ((!config_only)); then
  # Enable on next boot; do not interrupt the current network/audio session.
  sudo systemctl enable NetworkManager.service bluetooth.service
  if ! systemctl --user enable pipewire.socket pipewire-pulse.socket wireplumber.service; then
    echo 'Could not enable user audio services. Run these after logging in:' >&2
    echo 'systemctl --user enable --now pipewire.socket pipewire-pulse.socket wireplumber.service' >&2
    exit 1
  fi
fi
echo 'Done. Reboot, then select Sway at login, or run sway from a local TTY.'
