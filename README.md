# ptl2comsol — PTL → TS(Depth) → VTU → STL

Requirements:
- ParaView pvpython: /Applications/ParaView-6.0.0.app/Contents/bin/pvpython
- OGS GocadTSurfaceReader: /Users/sahim/ogs-env/bin/GocadTSurfaceReader
- Python 3.8+

Setup:
cat > README.md <<'MD'
# ptl2comsol — PTL → TS (Depth) → VTU → STL

Requirements
- ParaView pvpython: /Applications/ParaView-6.0.0.app/Contents/bin/pvpython
- OGS GocadTSurfaceReader: /Users/sahim/ogs-env/bin/GocadTSurfaceReader
- Python 3.8+

Setup
  cd ~/Desktop/ptl2comsol/ptl2comsol_tool
  ./setup_env.sh

Single file
  ./run_one.sh ../top_dogger.ptl

Batch (all .ptl in parent folder)
  ./run_batch.sh

Reset outputs
  ./reset_outputs.sh

Outputs
  ~/Desktop/ptl2comsol/out/{ts,vtu,stl}

TS format (this tool)
  ZPOSITIVE Depth
  VRTX <id> <X scientific> <Y scientific> <Z two-decimals> CNXYZ
  Example: VRTX 1 4.55782e+06 5.30497e+06 5144.79 CNXYZ
