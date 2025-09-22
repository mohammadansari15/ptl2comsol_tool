#!/usr/bin/env bash
export PVPYTHON="/Applications/ParaView-6.0.0.app/Contents/bin/pvpython"
export OGS_GOCAD_READER="/Users/sahim/ogs-env/bin/GocadTSurfaceReader"
chmod +x "$OGS_GOCAD_READER" 2>/dev/null || true
xattr -dr com.apple.quarantine "$OGS_GOCAD_READER" 2>/dev/null || true
echo "PVPYTHON=$PVPYTHON"
echo "OGS_GOCAD_READER=$OGS_GOCAD_READER"
