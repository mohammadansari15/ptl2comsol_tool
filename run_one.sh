#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/setup_env.sh"
PTL="${1:-$DIR/../top_dogger.ptl}"
OUT="$DIR/../out"
mkdir -p "$OUT"
python3 "$DIR/ptl2comsol_all.py" \
  --ptl "$PTL" \
  --out-dir "$OUT" \
  --decimate "${DECIMATE:-0.85}" \
  --ogs-reader "$OGS_GOCAD_READER" \
  --pvpython "$PVPYTHON"
