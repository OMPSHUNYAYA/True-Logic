#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import os

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def write_manifest(out_dir: str, rel_paths: list) -> None:
    manifest_path = os.path.join(out_dir, "MANIFEST.sha256")
    lines = []
    for rel in sorted(rel_paths):
        p = os.path.join(out_dir, rel)
        digest = sha256_file(p)
        lines.append(f"{digest}  {rel}")
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def clamp01(x: float) -> float:
    if x < 0.0: return 0.0
    if x > 1.0: return 1.0
    return x

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--dt", type=float, default=1.0)
    ap.add_argument("--t0", type=float, default=0.0)
    args = ap.parse_args()

    ensure_dir(args.out_dir)

    # A deterministic "ice-like" dominance trace d_t in [0,1]
    # Segment design (no randomness):
    # 1) metastable liquid (supercooling-like): d ~ 0.02, flat -> intended Z0 (not stable FALSE if tau_l=0.05 and W=10? it IS <= tau_l; stability may label Zstar if stable window is satisfied.
    #    To force Z0, keep d in mid-range with r=0 and s=0 by oscillating within (tau_l, tau_s).
    #    We will keep it around 0.10 (mid), flat -> Z0.
    #
    # 2) nucleation jump: d rises sharply -> Eplus
    # 3) stabilize solid: d ~ 0.98 for long -> S
    # 4) warming melt: d decreases -> Eminus
    # 5) stabilize liquid: d ~ 0.02 for long -> Zstar

    rows = []
    t = args.t0

    # Segment 1: pre-structural (mid, flat) ~ Z0
    for _ in range(15):
        rows.append((t, 0.10))
        t += args.dt

    # Segment 2: emerging (rising) ~ Eplus
    for d in [0.16, 0.24, 0.33, 0.43, 0.54, 0.66, 0.79, 0.88, 0.93]:
        rows.append((t, d))
        t += args.dt

    # Segment 3: stable solid ~ S (needs W steps)
    for _ in range(20):
        rows.append((t, 0.98))
        t += args.dt

    # Segment 4: destabilizing (falling) ~ Eminus
    for d in [0.92, 0.85, 0.76, 0.64, 0.51, 0.39, 0.28, 0.18, 0.12]:
        rows.append((t, d))
        t += args.dt

    # Segment 5: stable liquid ~ Zstar (needs W steps)
    for _ in range(20):
        rows.append((t, 0.02))
        t += args.dt

    out_csv = os.path.join(args.out_dir, "ice_like_trace.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "d"])
        for (tt, dd) in rows:
            w.writerow([f"{tt:.6f}", f"{clamp01(dd):.6f}"])

    write_manifest(args.out_dir, ["ice_like_trace.csv"])
    print(f"WROTE: {out_csv}")
    print(f"WROTE: {os.path.join(args.out_dir, 'MANIFEST.sha256')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
