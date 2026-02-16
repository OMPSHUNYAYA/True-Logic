#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import os
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

def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x

def parse_date(s: str) -> datetime:
    return datetime.strptime(s.strip(), "%Y-%m-%d")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_tsv", required=True, help="Tab-separated file with header: Date Open High Low Close Volume")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--lookback", type=int, default=252)
    ap.add_argument("--dd_scale", type=float, default=0.20)
    ap.add_argument("--close_col", default="Close")
    ap.add_argument("--date_col", default="Date")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    rows = []
    with open(args.in_tsv, "r", encoding="utf-8", errors="replace", newline="") as f:
        r = csv.DictReader(f, delimiter="\t")
        if args.date_col not in r.fieldnames or args.close_col not in r.fieldnames:
            raise SystemExit(f"Expected columns: {args.date_col}, {args.close_col}. Found: {r.fieldnames}")
        for row in r:
            d = parse_date(row[args.date_col])
            c = float(row[args.close_col])
            rows.append((d, c))

    if len(rows) < args.lookback:
        raise SystemExit("Not enough rows for lookback.")

    rows.sort(key=lambda x: x[0])

    close = [c for _, c in rows]
    dates = [d for d, _ in rows]
    L = int(args.lookback)
    dd_scale = float(args.dd_scale)
    if dd_scale <= 0.0:
        raise SystemExit("dd_scale must be positive.")

    out_trace = os.path.join(args.out_dir, "stl_input_t_d.csv")
    out_summary = os.path.join(args.out_dir, "summary.txt")

    peak = close[0]
    peaks = [0.0] * len(close)

    for i in range(len(close)):
        if i < L:
            peak = max(peak, close[i])
            peaks[i] = peak
        else:
            window_peak = close[i - L + 1]
            for j in range(i - L + 1, i + 1):
                if close[j] > window_peak:
                    window_peak = close[j]
            peaks[i] = window_peak

    with open(out_trace, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["t", "d", "close", "roll_peak", "drawdown"])
        for i in range(len(close)):
            H = peaks[i]
            C = close[i]
            dd = 0.0 if H <= 0.0 else (H - C) / H
            d = clamp01(dd / dd_scale)
            w.writerow([i, f"{d:.6f}", f"{C:.6f}", f"{H:.6f}", f"{dd:.6f}"])

    with open(out_summary, "w", encoding="utf-8", newline="\n") as f:
        f.write("STL SPX Drawdown Adapter Summary\n")
        f.write(f"in_tsv={args.in_tsv}\n")
        f.write(f"rows={len(rows)}\n")
        f.write(f"date_min={dates[0].strftime('%Y-%m-%d')}\n")
        f.write(f"date_max={dates[-1].strftime('%Y-%m-%d')}\n")
        f.write(f"lookback={L}\n")
        f.write(f"dd_scale={dd_scale}\n")

    write_manifest(args.out_dir, ["stl_input_t_d.csv", "summary.txt"])
    print("WROTE:", out_trace)
    print("WROTE:", out_summary)
    print("WROTE:", os.path.join(args.out_dir, "MANIFEST.sha256"))

if __name__ == "__main__":
    main()
