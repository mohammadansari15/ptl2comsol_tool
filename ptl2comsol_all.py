import argparse, os, sys, subprocess, tempfile
from pathlib import Path

def log(m): print(m, flush=True)

def normalize_line_endings(p: Path):
    b=p.read_bytes()
    nb=b.replace(b"\r\n",b"\n").replace(b"\r",b"\n")
    if nb!=b: p.write_bytes(nb)

def parse_schema(s):
    t=s.replace(","," ").split()
    if set(t)!={"x","y","z","i","j"} or len(t)!=5: raise SystemExit("bad schema")
    return {name:k for k,name in enumerate(t)}

def read_ptl_schema(path,pos,negate_z=True):
    pts={}
    with open(path,"rb") as f:
        for raw in f:
            s=raw.strip()
            if not s: continue
            c=s.split()
            if len(c)<5: continue
            try:
                x=float(c[pos["x"]]); y=float(c[pos["y"]]); z=float(c[pos["z"]])
                ii=int(c[pos["i"]]); jj=int(c[pos["j"]])
            except Exception:
                continue
            if negate_z: z=-z
            pts[(ii,jj)]=(x,y,z)
    return pts

def build_mesh_diag(pts,diag):
    if not pts: return [],[]
    iset=sorted({ij[0] for ij in pts})
    jset=sorted({ij[1] for ij in pts})
    index={}; verts=[]
    for j in jset:
        for i in iset:
            if (i,j) in pts:
                index[(i,j)]=len(verts)+1
                verts.append(pts[(i,j)])
    tris=[]
    for j in jset[:-1]:
        for i in iset[:-1]:
            if (i,j) in index and (i+1,j) in index and (i,j+1) in index and (i+1,j+1) in index:
                v00=index[(i,j)]; v10=index[(i+1,j)]; v01=index[(i,j+1)]; v11=index[(i+1,j+1)]
                if diag=="fwd":
                    tris.append((v00,v10,v11))
                    tris.append((v00,v11,v01))
                else:
                    tris.append((v00,v10,v01))
                    tris.append((v10,v11,v01))
    return verts,tris

def write_tsurf_resi(out_path, verts, tris, name):
    with open(out_path,"w",newline="\n") as g:
        g.write("GOCAD TSurf 1\n")
        g.write("HEADER{\n")
        g.write(f"name:{name}\n")
        g.write("}\n")
        g.write("GOCAD_ORIGINAL_COORDINATE_SYSTEM\n")
        g.write("NAME Default\n")
        g.write("AXIS_NAME \"X\" \"Y\" \"Z\"\n")
        g.write("AXIS_UNIT \"m\" \"m\" \"m\"\n")
        g.write("ZPOSITIVE Depth\n")
        g.write("END_ORIGINAL_COORDINATE_SYSTEM\n")
        g.write("TFACE\n")
        for idx,(x,y,z) in enumerate(verts, start=1):
            xs=f"{x:.5e}"; ys=f"{y:.5e}"; zs=f"{z:.2f}"
            g.write(f"VRTX {idx} {xs} {ys} {zs} CNXYZ\n")
        for a,b,c in tris:
            g.write(f"TRGL {a} {b} {c}\n")
        g.write("END\n")

def ts_to_vtu(ts_path: Path, vtu_out_dir: Path, ogs_reader: str):
    vtu_out_dir.mkdir(parents=True, exist_ok=True)
    before={p.name for p in vtu_out_dir.glob("*.vtu")}
    cmd=[ogs_reader,"-i",str(ts_path),"-o",str(vtu_out_dir)]
    proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if proc.returncode!=0: raise RuntimeError(proc.stderr or proc.stdout)
    after=[p for p in vtu_out_dir.glob("*.vtu") if p.name not in before]
    if not after: after=list(vtu_out_dir.glob(f"{ts_path.stem}*.vtu"))
    if not after: raise RuntimeError("No .vtu produced by OGS")
    return sorted(after)

def ensure_pv_script(tmpdir: Path) -> Path:
    lines=[
        "import sys",
        "from paraview.simple import OpenDataFile, ExtractSurface, Clean, Decimate",
        "try:\n from paraview.simple import Triangulate\nexcept Exception:\n Triangulate=None",
        "try:\n from paraview.simple import SaveData, SetActiveSource\nexcept Exception:\n pass",
        "vtu, stl, target = sys.argv[1], sys.argv[2], float(sys.argv[3])",
        "src=OpenDataFile(vtu)",
        "surf=ExtractSurface(Input=src)",
        "cln=Clean(Input=surf)",
        "tri=Triangulate(Input=cln) if Triangulate else cln",
        "dec=Decimate(Input=tri); dec.TargetReduction=target",
        "try:\n SaveData(stl, proxy=dec)\nexcept TypeError:\n SetActiveSource(dec); SaveData(stl)",
    ]
    f=tmpdir/"pv_to_stl_runtime.py"; f.write_text("\n".join(lines)); return f

def vtu_to_stl(vtu: Path, stl: Path, decimate: float, pvpython: str):
    stl.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        scr=ensure_pv_script(Path(td))
        cmd=[pvpython,str(scr),str(vtu),str(stl),str(decimate)]
        proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        if proc.returncode!=0: raise RuntimeError(proc.stderr or proc.stdout)

def canonical_base(p: Path) -> str:
    base=p.name
    for _ in range(2):
        if base.lower().endswith(".ptl"): base=base[:-4]
        elif base.lower().endswith(".ts"): base=base[:-3]
    return base

def ptl_to_ts(ptl_path: Path, ts_out: Path):
    normalize_line_endings(ptl_path)
    SCHEMA="x y z i j"
    NEGATE_Z=True
    DIAG="fwd"
    pos=parse_schema(SCHEMA)
    pts=read_ptl_schema(ptl_path,pos,negate_z=NEGATE_Z)
    verts,tris=build_mesh_diag(pts,DIAG)
    if not verts or not tris: raise RuntimeError("No triangles created from PTL")
    ts_out.parent.mkdir(parents=True, exist_ok=True)
    write_tsurf_resi(ts_out, verts, tris, ptl_path.stem)
    return ts_out

def main():
    ap=argparse.ArgumentParser(description="PTL → TS → VTU → STL")
    ap.add_argument("--ptl", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--decimate", type=float, default=0.85)
    ap.add_argument("--pvpython", default=os.environ.get("PVPYTHON","pvpython"))
    ap.add_argument("--ogs-reader", default=os.environ.get("OGS_GOCAD_READER","GocadTSurfaceReader"))
    args=ap.parse_args()

    ptl_path=Path(args.ptl)
    out_dir=Path(args.out_dir)
    ts_dir=out_dir/"ts"; vtu_dir=out_dir/"vtu"; stl_dir=out_dir/"stl"
    ts_dir.mkdir(parents=True, exist_ok=True); vtu_dir.mkdir(parents=True, exist_ok=True); stl_dir.mkdir(parents=True, exist_ok=True)

    base=canonical_base(ptl_path)
    ts_path=ts_dir/f"{base}.ts"
    log(f"[PTL→TS] {ptl_path} → {ts_path}")
    ts_out=ptl_to_ts(ptl_path, ts_path)

    log(f"[TS→VTU] {ts_out} → {vtu_dir}")
    vtus=ts_to_vtu(ts_out, vtu_dir, args.ogs_reader)
    if len(vtus)==1:
        clean_vtu=vtu_dir/f"{base}.vtu"
        if vtus[0].resolve()!=clean_vtu.resolve():
            try: os.replace(vtus[0], clean_vtu)
            except Exception: pass
        vtus=[clean_vtu]
    else:
        tmp=[]
        for i,v in enumerate(vtus,1):
            tgt=vtu_dir/f"{base}_{i:02d}.vtu"
            if v.resolve()!=tgt.resolve():
                try: os.replace(v, tgt)
                except Exception: pass
            tmp.append(tgt)
        vtus=tmp

    for vtu in vtus:
        stl=stl_dir/(vtu.stem+".stl")
        log(f"[VTU→STL] {vtu} → {stl} (decimate={args.decimate})")
        vtu_to_stl(vtu, stl, args.decimate, args.pvpython)

    log(f"Done. TS→ {ts_out}, VTU→ {vtu_dir}, STL→ {stl_dir}")

if __name__=="__main__":
    main()
