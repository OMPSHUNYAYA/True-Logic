#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import os

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x

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

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--dt", type=float, default=1.0)
    ap.add_argument("--t0", type=float, default=0.0)

    ap.add_argument("--pre_len", type=int, default=40)
    ap.add_argument("--solid_len", type=int, default=30)
    ap.add_argument("--liquid_len", type=int, default=30)

    ap.add_argument("--d_pre", type=float, default=0.10)
    ap.add_argument("--d_solid", type=float, default=0.98)
    ap.add_argument("--d_liquid", type=float, default=0.02)

    ap.add_argument("--jump_steps", type=int, default=2)
    args = ap.parse_args()

    if args.pre_len < 1 or args.solid_len < 1 or args.liquid_len < 1:
        raise SystemExit("ERROR: lengths must be >= 1")
    if args.jump_steps < 1:
        raise SystemExit("ERROR: jump_steps must be >= 1")

    ensure_dir(args.out_dir)

    rows = []
    t = args.t0

    d_pre = clamp01(args.d_pre)
    d_solid = clamp01(args.d_solid)
    d_liquid = clamp01(args.d_liquid)

    for _ in range(args.pre_len):
        rows.append((t, d_pre))
        t += args.dt

    for _ in range(args.jump_steps):
        rows.append((t, d_solid))
        t += args.dt

    for _ in range(args.solid_len):
        rows.append((t, d_solid))
        t += args.dt

    for _ in range(args.jump_steps):
        rows.append((t, d_liquid))
        t += args.dt

    for _ in range(args.liquid_len):
        rows.append((t, d_liquid))
        t += args.dt

    out_csv = os.path.join(args.out_dir, "ice_like_trace_v1_1.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "d"])
        for (tt, dd) in rows:
            w.writerow([f"{tt:.6f}", f"{dd:.6f}"])

    write_manifest(args.out_dir, ["ice_like_trace_v1_1.csv"])
    print(f"WROTE: {out_csv}")
    print(f"WROTE: {os.path.join(args.out_dir, 'MANIFEST.sha256')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
