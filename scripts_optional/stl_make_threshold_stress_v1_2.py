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

    ap.add_argument("--tau_s", type=float, default=0.95)
    ap.add_argument("--tau_l", type=float, default=0.05)

    ap.add_argument("--cycles", type=int, default=4)
    ap.add_argument("--hold_Wminus1", type=int, default=9)
    ap.add_argument("--hold_Wplus1", type=int, default=11)

    ap.add_argument("--eps_step", type=float, default=0.01)
    args = ap.parse_args()

    if not (0.0 <= args.tau_l < args.tau_s <= 1.0):
        raise SystemExit("ERROR: require 0 <= tau_l < tau_s <= 1")
    if args.cycles < 1:
        raise SystemExit("ERROR: cycles must be >= 1")
    if args.hold_Wminus1 < 1 or args.hold_Wplus1 < 1:
        raise SystemExit("ERROR: hold lengths must be >= 1")
    if args.eps_step <= 0.0:
        raise SystemExit("ERROR: eps_step must be > 0")

    ensure_dir(args.out_dir)

    t = args.t0
    rows = []

    # Deterministic pattern per cycle:
    # A) Near tau_s but not stable: hold (W-1) samples just BELOW tau_s, then 1 sample ABOVE, then drop below again.
    # B) Earn stable S: hold (W+1) samples ABOVE tau_s.
    # C) Near tau_l but not stable: hold (W-1) samples just ABOVE tau_l, then 1 sample BELOW, then rise above again.
    # D) Earn stable Zstar: hold (W+1) samples BELOW tau_l.
    #
    # This creates both "almost stable but not enough" and "stable earned" segments.

    below_ts = clamp01(args.tau_s - args.eps_step)
    above_ts = clamp01(args.tau_s + args.eps_step)

    above_tl = clamp01(args.tau_l + args.eps_step)
    below_tl = clamp01(args.tau_l - args.eps_step)

    for _ in range(args.cycles):
        # A) near tau_s, not stable
        for _i in range(args.hold_Wminus1):
            rows.append((t, below_ts)); t += args.dt
        rows.append((t, above_ts)); t += args.dt
        for _i in range(args.hold_Wminus1):
            rows.append((t, below_ts)); t += args.dt

        # B) earn S
        for _i in range(args.hold_Wplus1):
            rows.append((t, above_ts)); t += args.dt

        # C) near tau_l, not stable
        for _i in range(args.hold_Wminus1):
            rows.append((t, above_tl)); t += args.dt
        rows.append((t, below_tl)); t += args.dt
        for _i in range(args.hold_Wminus1):
            rows.append((t, above_tl)); t += args.dt

        # D) earn Zstar
        for _i in range(args.hold_Wplus1):
            rows.append((t, below_tl)); t += args.dt

    out_csv = os.path.join(args.out_dir, "threshold_stress_trace_v1_2.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "d"])
        for (tt, dd) in rows:
            w.writerow([f"{tt:.6f}", f"{dd:.6f}"])

    write_manifest(args.out_dir, ["threshold_stress_trace_v1_2.csv"])
    print(f"WROTE: {out_csv}")
    print(f"WROTE: {os.path.join(args.out_dir, 'MANIFEST.sha256')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
