#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import hashlib
import os
import pandas as pd

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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_parquet", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--bin_rows", type=int, default=5000)
    ap.add_argument("--label_col", default="Label")
    ap.add_argument("--benign_label", default="BENIGN")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    df = pd.read_parquet(args.in_parquet)

    if args.label_col not in df.columns:
        raise SystemExit("Label column not found in parquet.")

    labels = df[args.label_col].astype(str)
    attack = (labels.str.upper() != args.benign_label.upper()).astype(int)

    n = len(attack)
    if n == 0:
        raise SystemExit("No rows in parquet.")

    bin_rows = int(args.bin_rows)
    if bin_rows <= 0:
        raise SystemExit("bin_rows must be positive.")

    bins = []
    for start in range(0, n, bin_rows):
        end = min(start + bin_rows, n)
        total = end - start
        atk = int(attack.iloc[start:end].sum())
        d = 0.0 if total == 0 else (atk / total)
        t = start
        bins.append((t, d, total, atk))

    out_trace = os.path.join(args.out_dir, "stl_input_t_d.csv")
    out_summary = os.path.join(args.out_dir, "summary.txt")

    out_df = pd.DataFrame(bins, columns=["t", "d", "total_flows", "attack_flows"])
    out_df.to_csv(out_trace, index=False, float_format="%.6f")

    with open(out_summary, "w", encoding="utf-8", newline="\n") as f:
        f.write("STL CICIDS2017 Parquet Row-Bin Adapter Summary\n")
        f.write(f"in_parquet={args.in_parquet}\n")
        f.write(f"bin_rows={bin_rows}\n")
        f.write(f"total_rows={n}\n")
        f.write(f"bins={len(out_df)}\n")
        f.write(f"total_attack_flows={int(attack.sum())}\n")

    write_manifest(args.out_dir, ["stl_input_t_d.csv", "summary.txt"])

    print("WROTE:", out_trace)
    print("WROTE:", out_summary)
    print("WROTE:", os.path.join(args.out_dir, "MANIFEST.sha256"))

if __name__ == "__main__":
    main()
