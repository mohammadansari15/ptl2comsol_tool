# ptl2comsol — PTL → TS (Depth) → VTU → STL

Converts Petrel `.ptl` horizons to:
- **GOCAD TSurf (.ts)** in **Depth** (`ZPOSITIVE Depth`, X/Y scientific, Z two decimals, `CNXYZ`)
- **VTU** via OpenGeoSys **GocadTSurfaceReader**
- **STL** via ParaView **pvpython** (ExtractSurface → Clean → Triangulate → Decimate → SaveData)

## Requirements
- ParaView pvpython: `/Applications/ParaView-6.0.0.app/Contents/bin/pvpython`
- OGS GocadTSurfaceReader: `/Users/sahim/ogs-env/bin/GocadTSurfaceReader`
- Python 3.8+

## Quick start
```bash
cd ~/Desktop/ptl2comsol/ptl2comsol_tool
./setup_env.sh
./run_one.sh ../top_dogger.ptl
# or: ./run_batch.sh
