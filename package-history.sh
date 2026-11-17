#!/usr/bin/env bash

package_snapshot() {
  if [[ "$1" = debian ]]; then
    dpkg-query -W -f='${binary:Package}\t${Version}\t${db:Status-Status}\n' |
      awk -F '\t' '$3 == "installed" {print $1 "\t" $2}' | LC_ALL=C sort -u
  else
    pacman -Q | awk '{print $1 "\t" $2}' | LC_ALL=C sort -u
  fi
}

package_explicit() {
  if [[ "$1" = debian ]]; then apt-mark showmanual; else pacman -Qqe; fi | LC_ALL=C sort -u
}

record_package_result() {
  local result=$1
  printf '%s\n' "$result" > "$history/package-exit-code"
  if ! package_snapshot "$distribution" > "$history/after.tsv" ||
     ! package_explicit "$distribution" > "$history/explicit-after.txt"; then
    echo "Incomplete package history: $history" >&2
    return 1
  fi
  cut -f1 "$history/before.tsv" > "$history/before-names.txt"
  cut -f1 "$history/after.tsv" > "$history/after-names.txt"
  LC_ALL=C comm -13 "$history/before-names.txt" "$history/after-names.txt" > "$history/added.txt"
  LC_ALL=C comm -23 "$history/before-names.txt" "$history/after-names.txt" > "$history/removed.txt"
  awk 'NR == FNR {requested[$1]=1; next} {name=$1; sub(/:.*/, "", name); if (name in requested) print $1}' \
    "$history/requested.txt" "$history/added.txt" > "$history/added-requested.txt"
  awk -F '\t' 'FILENAME == ARGV[1] {old[$1]=$2; next} ($1 in old) && old[$1] != $2 {print $1 "\t" old[$1] "\t" $2}' \
    "$history/before.tsv" "$history/after.tsv" > "$history/version-changes.tsv"
  LC_ALL=C comm -13 "$history/explicit-before.txt" "$history/explicit-after.txt" > "$history/newly-explicit.txt"
  printf 'Package history: %s\n' "$history"
}

install_packages_logged() (
  set -euo pipefail
  distribution=$1; shift
  base="$HOME/.local/state/sway-portable/packages"
  mkdir -p "$base"
  history=$(mktemp -d "$base/$(date +%Y%m%d-%H%M%S)-XXXXXX")
  printf '%s\n' "$distribution" > "$history/distribution"
  printf '%s\n' "$@" | LC_ALL=C sort -u > "$history/requested.txt"
  package_snapshot "$distribution" > "$history/before.tsv"
  package_explicit "$distribution" > "$history/explicit-before.txt"
  # Capture partial changes even when the package manager fails.
  trap 'result=$?; trap - EXIT; record_package_result "$result" || result=1; exit "$result"' EXIT
  if [[ "$distribution" = debian ]]; then
    sudo apt-get update
    sudo apt-get install "$@"
  else
    sudo pacman -Syu --needed "$@"
  fi
)
