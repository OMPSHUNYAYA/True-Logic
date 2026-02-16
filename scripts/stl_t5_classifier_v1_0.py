#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import os
import sys

T5_Z0 = "Z0"
T5_EPLUS = "Eplus"
T5_S = "S"
T5_EMINUS = "Eminus"
T5_ZSTAR = "Zstar"

def phi_T(state: str) -> str:
    if state == T5_S:
        return "TRUE"
    if state == T5_ZSTAR:
        return "FALSE"
    return "UNDEFINED"

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

def parse_float(s: str, field: str, line_no: int) -> float:
    try:
        v = float(s)
    except Exception:
        raise ValueError(f"Invalid float for {field} on line {line_no}: {s}")
    return v

def clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x

def compute_r(delta_d: float, eps: float) -> int:
    if delta_d > eps:
        return 1
    if delta_d < -eps:
        return -1
    return 0

def in_stable_true(d: float, tau_s: float) -> bool:
    return d >= tau_s

def in_stable_false(d: float, tau_l: float) -> bool:
    return d <= tau_l

def in_mid(d: float, tau_l: float, tau_s: float) -> bool:
    return (d > tau_l) and (d < tau_s)

def stable_window_ok(ds: list, idx: int, W: int, tau_l: float, tau_s: float) -> bool:
    if W <= 1:
        return True
    start = idx - (W - 1)
    if start < 0:
        return False
    d0 = ds[idx]
    if in_stable_true(d0, tau_s):
        for j in range(start, idx + 1):
            if not in_stable_true(ds[j], tau_s):
                return False
        return True
    if in_stable_false(d0, tau_l):
        for j in range(start, idx + 1):
            if not in_stable_false(ds[j], tau_l):
                return False
        return True
    return False

def classify_state(d: float, r: int, s: int, tau_l: float, tau_s: float) -> str:
    if d >= tau_s and s == 1:
        return T5_S
    if d <= tau_l and s == 1:
        return T5_ZSTAR
    if in_mid(d, tau_l, tau_s) and r == 1:
        return T5_EPLUS
    if in_mid(d, tau_l, tau_s) and r == -1:
        return T5_EMINUS
    return T5_Z0

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def read_input_csv(path: str) -> tuple[list, list]:
    ts = []
    ds = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise ValueError("CSV has no header row.")
        req = {"t", "d"}
        missing = req - set([x.strip() for x in r.fieldnames])
        if missing:
            raise ValueError(f"CSV missing required columns: {sorted(list(missing))}. Required: t,d")
        line_no = 1
        for row in r:
            line_no += 1
            t = row.get("t", "").strip()
            d = row.get("d", "").strip()
            if t == "" or d == "":
                raise ValueError(f"Empty t or d on line {line_no}")
            t_val = parse_float(t, "t", line_no)
            d_val = clamp01(parse_float(d, "d", line_no))
            ts.append(t_val)
            ds.append(d_val)
    if len(ts) == 0:
        raise ValueError("No rows found in input CSV.")
    return ts, ds

def write_sample_input_csv(path: str) -> None:
    rows = []
    t = 0.0
    for i in range(0, 10):
        rows.append((t, 0.02))
        t += 1.0
    for i in range(0, 10):
        d = 0.10 + (i * 0.06)
        rows.append((t, d))
        t += 1.0
    for i in range(0, 10):
        rows.append((t, 0.98))
        t += 1.0
    for i in range(0, 10):
        d = 0.90 - (i * 0.07)
        rows.append((t, d))
        t += 1.0
    for i in range(0, 10):
        rows.append((t, 0.02))
        t += 1.0

    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "d"])
        for (tt, dd) in rows:
            w.writerow([f"{tt:.3f}", f"{dd:.6f}"])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=False, help="Input CSV with columns: t,d (d in [0,1])")
    ap.add_argument("--out_dir", required=True, help="Output directory")
    ap.add_argument("--W", type=int, default=10, help="Stability window length (>=1)")
    ap.add_argument("--tau_s", type=float, default=0.95, help="Stable TRUE threshold")
    ap.add_argument("--tau_l", type=float, default=0.05, help="Stable FALSE threshold")
    ap.add_argument("--eps", type=float, default=0.01, help="Derivative threshold")
    ap.add_argument("--make_sample", action="store_true", help="Write a sample input CSV and exit")
    args = ap.parse_args()

    if args.W < 1:
        print("ERROR: W must be >= 1", file=sys.stderr)
        return 2
    if not (0.0 <= args.tau_l < args.tau_s <= 1.0):
        print("ERROR: require 0 <= tau_l < tau_s <= 1", file=sys.stderr)
        return 2
    if args.eps < 0.0:
        print("ERROR: eps must be >= 0", file=sys.stderr)
        return 2

    ensure_dir(args.out_dir)

    sample_path = os.path.join(args.out_dir, "sample_input.csv")
    if args.make_sample:
        write_sample_input_csv(sample_path)
        rels = ["sample_input.csv"]
        write_manifest(args.out_dir, rels)
        print(f"WROTE: {sample_path}")
        return 0

    if not args.in_csv:
        print("ERROR: --in_csv required unless --make_sample is used", file=sys.stderr)
        return 2

    ts, ds = read_input_csv(args.in_csv)

    out_csv = os.path.join(args.out_dir, "stl_trace_out.csv")
    summary = os.path.join(args.out_dir, "summary.txt")

    states = []
    collapses = []
    rs = []
    ss = []
    deltas = []

    prev_d = ds[0]
    for i in range(len(ds)):
        d = ds[i]
        if i == 0:
            delta_d = 0.0
        else:
            delta_d = d - prev_d
        r = compute_r(delta_d, args.eps)
        s_ok = stable_window_ok(ds, i, args.W, args.tau_l, args.tau_s)
        s = 1 if s_ok else 0
        st = classify_state(d, r, s, args.tau_l, args.tau_s)
        ph = phi_T(st)

        deltas.append(delta_d)
        rs.append(r)
        ss.append(s)
        states.append(st)
        collapses.append(ph)

        prev_d = d

    counts = {T5_Z0: 0, T5_EPLUS: 0, T5_S: 0, T5_EMINUS: 0, T5_ZSTAR: 0}
    for st in states:
        counts[st] += 1

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "d", "delta_d", "r", "s", "state", "phi_T"])
        for i in range(len(ds)):
            w.writerow([
                f"{ts[i]:.6f}",
                f"{ds[i]:.6f}",
                f"{deltas[i]:.6f}",
                str(rs[i]),
                str(ss[i]),
                states[i],
                collapses[i],
            ])

    with open(summary, "w", encoding="utf-8", newline="\n") as f:
        f.write("STL T5 CLASSIFIER SUMMARY\n")
        f.write(f"in_csv = {args.in_csv}\n")
        f.write(f"W = {args.W}\n")
        f.write(f"tau_s = {args.tau_s}\n")
        f.write(f"tau_l = {args.tau_l}\n")
        f.write(f"eps = {args.eps}\n")
        f.write(f"rows = {len(ds)}\n")
        f.write("counts:\n")
        for k in [T5_Z0, T5_EPLUS, T5_S, T5_EMINUS, T5_ZSTAR]:
            f.write(f"  {k} = {counts[k]}\n")
        f.write("collapse_counts:\n")
        f.write(f"  TRUE = {sum(1 for x in collapses if x == 'TRUE')}\n")
        f.write(f"  FALSE = {sum(1 for x in collapses if x == 'FALSE')}\n")
        f.write(f"  UNDEFINED = {sum(1 for x in collapses if x == 'UNDEFINED')}\n")

    rels = ["stl_trace_out.csv", "summary.txt"]
    write_manifest(args.out_dir, rels)

    print(f"WROTE: {out_csv}")
    print(f"WROTE: {summary}")
    print(f"WROTE: {os.path.join(args.out_dir, 'MANIFEST.sha256')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
