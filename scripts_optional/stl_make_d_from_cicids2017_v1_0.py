#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import os
import sys
from datetime import datetime

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def write_manifest(out_dir: str, filenames):
    man_path = os.path.join(out_dir, "MANIFEST.sha256")
    with open(man_path, "w", encoding="utf-8", newline="\n") as f:
        for name in filenames:
            p = os.path.join(out_dir, name)
            f.write(f"{sha256_file(p)}  {name}\n")
    return man_path

def parse_ts(s: str) -> datetime:
    s = (s or "").strip()
    fmts = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unrecognized Timestamp format: {s!r}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True, help="CICIDS2017 flow CSV (one file/day)")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--bin_sec", type=int, default=60, help="time bin size in seconds")
    ap.add_argument("--label_col", default="Label")
    ap.add_argument("--ts_col", default="Timestamp")
    ap.add_argument("--benign_label", default="BENIGN")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    rows = []
    with open(args.in_csv, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f)
        if args.ts_col not in r.fieldnames or args.label_col not in r.fieldnames:
            raise SystemExit(
                "Required columns not found. "
                f"Need ts_col={args.ts_col!r} and label_col={args.label_col!r}. "
                f"Found: {r.fieldnames}"
            )
        for row in r:
            ts = parse_ts(row[args.ts_col])
            lab = (row[args.label_col] or "").strip()
            is_attack = 0 if lab.upper() == args.benign_label.upper() else 1
            rows.append((ts, is_attack))

    if not rows:
        raise SystemExit("No rows read from input.")

    rows.sort(key=lambda x: x[0])
    t0 = rows[0][0]

    bins = {}
    for ts, is_attack in rows:
        sec = int((ts - t0).total_seconds())
        b = (sec // args.bin_sec) * args.bin_sec
        if b not in bins:
            bins[b] = [0, 0]  # total, attack
        bins[b][0] += 1
        bins[b][1] += is_attack

    out_trace = os.path.join(args.out_dir, "stl_input_t_d.csv")
    out_meta = os.path.join(args.out_dir, "summary.txt")

    bin_keys = sorted(bins.keys())

    with open(out_trace, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["t", "d", "total_flows", "attack_flows"])
        for b in bin_keys:
            total, attack = bins[b]
            d = 0.0 if total == 0 else (attack / total)
            w.writerow([b, f"{d:.6f}", total, attack])

    total_bins = len(bin_keys)
    total_flows = sum(bins[b][0] for b in bin_keys)
    total_attack = sum(bins[b][1] for b in bin_keys)

    with open(out_meta, "w", encoding="utf-8", newline="\n") as f:
        f.write("STL CICIDS2017 Adapter Summary\n")
        f.write(f"in_csv={args.in_csv}\n")
        f.write(f"bin_sec={args.bin_sec}\n")
        f.write(f"ts_col={args.ts_col}\n")
        f.write(f"label_col={args.label_col}\n")
        f.write(f"benign_label={args.benign_label}\n")
        f.write(f"bins={total_bins}\n")
        f.write(f"total_flows={total_flows}\n")
        f.write(f"total_attack_flows={total_attack}\n")

    write_manifest(args.out_dir, ["stl_input_t_d.csv", "summary.txt"])
    print(f"WROTE: {out_trace}")
    print(f"WROTE: {out_meta}")
    print(f"WROTE: {os.path.join(args.out_dir, 'MANIFEST.sha256')}")

if __name__ == "__main__":
    main()
