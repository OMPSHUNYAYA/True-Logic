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
    ap.add_argument("--bin_sec", type=int, default=60)
    ap.add_argument("--ts_col", default="Timestamp")
    ap.add_argument("--label_col", default="Label")
    ap.add_argument("--benign_label", default="BENIGN")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    df = pd.read_parquet(args.in_parquet)

    if args.ts_col not in df.columns or args.label_col not in df.columns:
        raise SystemExit("Timestamp or Label column not found in parquet.")

    df[args.ts_col] = pd.to_datetime(df[args.ts_col])
    df = df.sort_values(args.ts_col)

    t0 = df[args.ts_col].iloc[0]
    df["sec"] = (df[args.ts_col] - t0).dt.total_seconds().astype(int)
    df["bin"] = (df["sec"] // args.bin_sec) * args.bin_sec

    df["attack"] = (df[args.label_col].str.upper() != args.benign_label.upper()).astype(int)

    grouped = df.groupby("bin").agg(
        total_flows=("attack", "count"),
        attack_flows=("attack", "sum")
    ).reset_index()

    grouped["d"] = grouped["attack_flows"] / grouped["total_flows"]

    out_trace = os.path.join(args.out_dir, "stl_input_t_d.csv")
    out_summary = os.path.join(args.out_dir, "summary.txt")

    grouped[["bin", "d", "total_flows", "attack_flows"]].rename(
        columns={"bin": "t"}
    ).to_csv(out_trace, index=False, float_format="%.6f")

    with open(out_summary, "w", encoding="utf-8", newline="\n") as f:
        f.write("STL CICIDS2017 Parquet Adapter Summary\n")
        f.write(f"in_parquet={args.in_parquet}\n")
        f.write(f"bin_sec={args.bin_sec}\n")
        f.write(f"total_bins={len(grouped)}\n")
        f.write(f"total_flows={grouped['total_flows'].sum()}\n")
        f.write(f"total_attack_flows={grouped['attack_flows'].sum()}\n")

    write_manifest(args.out_dir, ["stl_input_t_d.csv", "summary.txt"])

    print("WROTE:", out_trace)
    print("WROTE:", out_summary)
    print("WROTE:", os.path.join(args.out_dir, "MANIFEST.sha256"))

if __name__ == "__main__":
    main()
