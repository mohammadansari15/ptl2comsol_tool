#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/setup_env.sh"
OUT="$DIR/../out"
mkdir -p "$OUT"
shopt -s nullglob
for PTL in "$DIR"/../*.ptl; do
  python3 "$DIR/ptl2comsol_all.py" \
    --ptl "$PTL" \
    --out-dir "$OUT" \
    --decimate "${DECIMATE:-0.85}" \
    --ogs-reader "$OGS_GOCAD_READER" \
    --pvpython "$PVPYTHON"
done
