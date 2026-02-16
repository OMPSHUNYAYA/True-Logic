#!/usr/bin/env python3
# Deterministic negative control trace for STL:
# Produces a dominance trace d_t that includes:
# - long stable FALSE region
# - transitional ramp up
# - long stable TRUE region
# - transitional ramp down
# - long stable FALSE region
#
# Purpose: a classical stability-gated Boolean (debounced) will align with STL collapse,
# so SAD(P) should be 0.

import argparse
import csv
import os
import hashlib

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def write_manifest(out_dir: str, files: list[str]) -> None:
    manifest_path = os.path.join(out_dir, "MANIFEST.sha256")
    rows = []
    for rel in sorted(files):
        abspath = os.path.join(out_dir, rel)
        rows.append((sha256_file(abspath), rel.replace("\\", "/")))
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        for digest, rel in rows:
            f.write(f"{digest}  {rel}\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--dt", type=int, default=1)
    args = ap.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    # Deterministic trace construction (no randomness):
    # stable low (0.0) -> ramp up -> stable high (1.0) -> ramp down -> stable low (0.0)
    dt = args.dt
    seq = []

    # 1) Stable FALSE region (20 steps)
    seq += [0.0] * 20

    # 2) Ramp up (10 steps): 0.0 -> 1.0
    for k in range(1, 11):
        seq.append(round(k / 10.0, 6))

    # 3) Stable TRUE region (25 steps)
    seq += [1.0] * 25

    # 4) Ramp down (10 steps): 1.0 -> 0.0
    for k in range(9, -1, -1):
        seq.append(round(k / 10.0, 6))

    # 5) Stable FALSE region (20 steps)
    seq += [0.0] * 20

    out_csv = os.path.join(out_dir, "negctl_debounced_trace_v1_0.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "d"])
        for i, d in enumerate(seq):
            t = i * dt
            w.writerow([t, f"{d:.6f}"])

    summary_path = os.path.join(out_dir, "summary.txt")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("Negative Control Trace (Debounced Boolean Alignment)\n")
        f.write("Deterministic dominance trace for STL negative control.\n")
        f.write(f"rows={len(seq)} dt={dt}\n")
        f.write("shape=stable_low -> ramp_up -> stable_high -> ramp_down -> stable_low\n")

    write_manifest(out_dir, ["negctl_debounced_trace_v1_0.csv", "summary.txt"])
    print("OK: negative control trace created")
    print(f"Output folder: {out_dir}")

if __name__ == "__main__":
    main()
