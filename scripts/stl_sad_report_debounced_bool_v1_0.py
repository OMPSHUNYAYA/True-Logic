#!/usr/bin/env python3
# SAD report where "naive Boolean" is a classical stability-gated (debounced) Boolean.
# This is a NEGATIVE CONTROL: when classical Boolean already enforces stability,
# STL should not show extra advantage. Expected: SAD(P) = 0.

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

def read_adapter_t_d(path: str):
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for i, row in enumerate(r):
            t = int(float(row["t"]))
            d = float(row["d"])
            rows.append((t, d))
    if not rows:
        raise SystemExit("ERROR: adapter_csv has no rows")
    return rows

def read_trace_phi(path: str):
    # Expect STL classifier output with at least: t, state_t, phi_T
    # We will accept common column names:
    # - t
    # - phi_T or phi
    with open(path, "r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        cols = r.fieldnames or []
        phi_col = None
        for cand in ["phi_T", "phi", "collapse", "phiT"]:
            if cand in cols:
                phi_col = cand
                break
        if phi_col is None:
            raise SystemExit(f"ERROR: trace_csv missing collapse column. Found cols={cols}")
        out = {}
        for row in r:
            t = int(float(row["t"]))
            out[t] = row[phi_col].strip()
    if not out:
        raise SystemExit("ERROR: trace_csv has no rows")
    return out

def debounced_boolean(d_vals, W, tau_s, tau_l):
    # Returns dict[t] -> {"TRUE","FALSE","UNDEFINED"} (UNDEFINED = no new stable decision yet)
    # but we also keep the held stable value separately.
    # Classical debounce:
    # - enter TRUE only after W consecutive d>=tau_s
    # - enter FALSE only after W consecutive d<=tau_l
    # - otherwise hold last stable boolean state
    out = {}
    hold = "FALSE"  # initial default; conservative start
    # Counters
    c_hi = 0
    c_lo = 0
    for (t, d) in d_vals:
        if d >= tau_s:
            c_hi += 1
        else:
            c_hi = 0
        if d <= tau_l:
            c_lo += 1
        else:
            c_lo = 0

        if c_hi >= W:
            hold = "TRUE"
        elif c_lo >= W:
            hold = "FALSE"

        out[t] = hold
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter_csv", required=True)
    ap.add_argument("--trace_csv", required=True)
    ap.add_argument("--out_dir", required=True)

    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--dataset_source", required=True)
    ap.add_argument("--adapter_name", required=True)
    ap.add_argument("--proposition", required=True)
    ap.add_argument("--naive_rule", required=True)

    ap.add_argument("--W", type=int, required=True)
    ap.add_argument("--tau_s", type=float, required=True)
    ap.add_argument("--tau_l", type=float, required=True)
    ap.add_argument("--eps", type=float, required=True)  # logged for parity, not used here

    ap.add_argument("--event_on", choices=["enter_true", "enter_false"], default="enter_true")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    d_vals = read_adapter_t_d(args.adapter_csv)
    phi_by_t = read_trace_phi(args.trace_csv)

    bool_by_t = debounced_boolean(d_vals, args.W, args.tau_s, args.tau_l)

    # Event detection on debounced boolean
    events = []
    prev = None
    for (t, _) in d_vals:
        cur = bool_by_t[t]
        if prev is None:
            prev = cur
            continue
        if args.event_on == "enter_true" and prev != "TRUE" and cur == "TRUE":
            events.append(t)
        if args.event_on == "enter_false" and prev != "FALSE" and cur == "FALSE":
            events.append(t)
        prev = cur

    E_bool = len(events)
    E_prem = 0
    E_aligned = 0

    timing_rows = []
    for idx, t_bool in enumerate(events, start=1):
        # STL collapse at same t if phi_T is TRUE/FALSE and matches event direction
        phi = phi_by_t.get(t_bool, "").upper()
        want = "TRUE" if args.event_on == "enter_true" else "FALSE"

        if phi == want:
            E_aligned += 1
            delta = 0
            timing_rows.append((idx, t_bool, t_bool, delta, "ALIGNED"))
        else:
            # In negative control, this should not happen; would indicate premature bool (or mismatch)
            E_prem += 1
            timing_rows.append((idx, t_bool, "", "", "PREMATURE_OR_MISMATCH"))

    SAD = 0.0 if E_bool == 0 else (E_prem / E_bool)

    # TABLE I.2
    t2_path = os.path.join(args.out_dir, "SAD_TABLE_I2_RUN_DECLARATION.csv")
    with open(t2_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        w.writerow(["dataset_name", args.dataset_name])
        w.writerow(["dataset_source", args.dataset_source])
        w.writerow(["adapter_name", args.adapter_name])
        w.writerow(["proposition", args.proposition])
        w.writerow(["naive_rule", args.naive_rule])
        w.writerow(["W", args.W])
        w.writerow(["tau_s", args.tau_s])
        w.writerow(["tau_l", args.tau_l])
        w.writerow(["eps", args.eps])
        w.writerow(["adapter_csv_sha256", sha256_file(args.adapter_csv)])
        w.writerow(["trace_csv_sha256", sha256_file(args.trace_csv)])

    # TABLE I.3
    t3_path = os.path.join(args.out_dir, "SAD_TABLE_I3_EVENT_ACCOUNTING.csv")
    with open(t3_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["E_bool", "E_prem", "E_aligned", "SAD(P)"])
        w.writerow([E_bool, E_prem, E_aligned, f"{SAD:.6f}"])

    # TABLE I.4 (timing)
    t4_path = os.path.join(args.out_dir, "SAD_TABLE_I4_EVENT_TIMING.csv")
    with open(t4_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["i", "t_bool(i)", "t_stl(i)", "delta_i", "status"])
        for row in timing_rows:
            w.writerow(list(row))

    summary_path = os.path.join(args.out_dir, "summary.txt")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("SAD Negative Control Report (Debounced Boolean)\n")
        f.write("Goal: show SAD(P)=0 when classical Boolean already enforces stability.\n")
        f.write(f"E_bool={E_bool} E_prem={E_prem} E_aligned={E_aligned} SAD(P)={SAD:.6f}\n")
        f.write("If SAD(P) > 0 here, the negative control failed and requires investigation.\n")

    write_manifest(args.out_dir, [
        "SAD_TABLE_I2_RUN_DECLARATION.csv",
        "SAD_TABLE_I3_EVENT_ACCOUNTING.csv",
        "SAD_TABLE_I4_EVENT_TIMING.csv",
        "summary.txt",
    ])

    print("OK: Debounced-Boolean SAD negative control report complete")
    print(f"Output folder: {args.out_dir}")
    print(f"SAD(P) = {SAD:.6f}")

if __name__ == "__main__":
    main()
