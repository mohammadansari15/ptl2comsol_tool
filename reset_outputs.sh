#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$DIR/../out/ts" "$DIR/../out/vtu" "$DIR/../out/stl"
mkdir -p "$DIR/../out"
echo "Outputs cleared: $DIR/../out/{ts,vtu,stl}"
