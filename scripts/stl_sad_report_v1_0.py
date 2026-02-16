#!/usr/bin/env python3
# stl_sad_report_v1_0.py
# Standard library only. Deterministic outputs + SHA-256 manifest.
#
# SAD(P) definition (Appendix G/I aligned):
#   SAD(P) = E_premature / E_total
#
# where an event is a naive Boolean state change at t_bool, and
# "premature" means STL does NOT collapse to the new Boolean truth at t_bool
# (i.e., STL is UNDEFINED or the opposite at that exact time).

import argparse
import csv
import hashlib
import os
from typing import Dict, List, Optional


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(out_dir: str, rel_paths: List[str]) -> None:
    rel_paths_sorted = sorted(rel_paths)
    manifest_path = os.path.join(out_dir, "MANIFEST.sha256")
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        for rp in rel_paths_sorted:
            ap = os.path.join(out_dir, rp)
            digest = sha256_file(ap)
            f.write(f"{digest}  {rp}\n")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_csv_as_dicts(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def parse_float(x: str) -> float:
    return float(x.strip())


def parse_int(x: str) -> int:
    # tolerate "1.0" coming from csv writers
    return int(float(x.strip()))


def bool_from_d(d: float, mode: str, threshold: float) -> bool:
    # mode:
    #   "ge" => TRUE if d >= threshold
    #   "gt" => TRUE if d >  threshold
    #   "le" => TRUE if d <= threshold
    #   "lt" => TRUE if d <  threshold
    if mode == "ge":
        return d >= threshold
    if mode == "gt":
        return d > threshold
    if mode == "le":
        return d <= threshold
    if mode == "lt":
        return d < threshold
    raise ValueError(f"Unsupported --bool_mode: {mode}")


def phi_to_bool(phi: str) -> Optional[bool]:
    # Expect phi_T values: TRUE / FALSE / UNDEFINED
    p = (phi or "").strip().upper()
    if p == "TRUE":
        return True
    if p == "FALSE":
        return False
    return None  # UNDEFINED or missing


def find_first_stl_collapse_at_or_after(
    idx_start: int,
    desired: bool,
    phi_seq: List[Optional[bool]],
    t_seq: List[int],
) -> Optional[int]:
    # Return time t where phi becomes desired first time at/after idx_start, else None
    for j in range(idx_start, len(phi_seq)):
        if phi_seq[j] is not None and phi_seq[j] == desired:
            return t_seq[j]
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--adapter_csv", required=True, help="Path to adapter output CSV with columns: t,d")
    ap.add_argument("--trace_csv", required=True, help="Path to classifier output CSV with column: phi_T")
    ap.add_argument("--out_dir", required=True, help="Output directory for SAD tables + summary + manifest")

    ap.add_argument("--dataset_name", required=True, help="Dataset/run label (Table I.2)")
    ap.add_argument("--dataset_source", required=True, help="Dataset source text (Table I.2)")
    ap.add_argument("--adapter_name", required=True, help="Adapter script/name (Table I.2)")
    ap.add_argument("--proposition", required=True, help="Proposition P text")
    ap.add_argument("--naive_rule", required=True, help="Naive Boolean rule text (Table I.2)")

    ap.add_argument("--bool_mode", required=True, choices=["ge", "gt", "le", "lt"],
                    help="Naive boolean direction vs threshold on d_t")
    ap.add_argument("--threshold", required=True, type=float, help="Threshold applied to d_t for naive Boolean")
    ap.add_argument("--event_on", required=True, choices=["enter_true", "enter_false", "any_change"],
                    help="Which threshold events count: enter_true (FALSE->TRUE), enter_false (TRUE->FALSE), any_change (both)")

    ap.add_argument("--W", required=True, type=int)
    ap.add_argument("--tau_s", required=True, type=float)
    ap.add_argument("--tau_l", required=True, type=float)
    ap.add_argument("--eps", required=True, type=float)

    args = ap.parse_args()
    ensure_dir(args.out_dir)

    adapter_rows = read_csv_as_dicts(args.adapter_csv)
    trace_rows = read_csv_as_dicts(args.trace_csv)

    if len(adapter_rows) != len(trace_rows):
        raise SystemExit(f"Row mismatch: adapter={len(adapter_rows)} trace={len(trace_rows)}")

    t_seq: List[int] = []
    d_seq: List[float] = []
    bool_seq: List[bool] = []
    phi_seq: List[Optional[bool]] = []

    # align by position; verify t matches
    for i in range(len(adapter_rows)):
        ar = adapter_rows[i]
        tr = trace_rows[i]

        t_a = parse_int(ar.get("t", str(i)))
        t_t = parse_int(tr.get("t", str(i)))
        if t_a != t_t:
            raise SystemExit(f"t mismatch at row {i}: adapter t={t_a} trace t={t_t}")

        d = parse_float(ar["d"])
        b = bool_from_d(d, args.bool_mode, args.threshold)

        # prefer phi_T column name, but tolerate alternates
        phi_raw = tr.get("phi_T", tr.get("phi", tr.get("collapse", "")))
        phi = phi_to_bool(phi_raw)

        t_seq.append(t_a)
        d_seq.append(d)
        bool_seq.append(b)
        phi_seq.append(phi)

    # Identify Boolean threshold events = any naive Boolean state change
    events: List[Dict[str, object]] = []
    for i in range(1, len(bool_seq)):
        prev_b = bool_seq[i - 1]
        cur_b = bool_seq[i]
        if prev_b == cur_b:
            continue

        if (not prev_b) and cur_b:
            ev_type = "enter_true"
        elif prev_b and (not cur_b):
            ev_type = "enter_false"
        else:
            ev_type = "any_change"

        if args.event_on != "any_change" and ev_type != args.event_on:
            continue

        t_bool = t_seq[i]
        desired = cur_b  # new Boolean truth after crossing

        # STL collapse status AT t_bool (i.e., at same index i)
        stl_at_bool = phi_seq[i]  # None = UNDEFINED

        aligned = (stl_at_bool is not None and stl_at_bool == desired)

        # SPEC-CORRECT: premature iff NOT aligned at the threshold instant
        premature = not aligned

        # Timing: first time at/after threshold when STL collapses to desired (if ever)
        t_stl = find_first_stl_collapse_at_or_after(i, desired, phi_seq, t_seq)

        events.append({
            "event_index": len(events) + 1,
            "event_type": ev_type,
            "t_bool": t_bool,
            "bool_after": "TRUE" if desired else "FALSE",
            "stl_at_t_bool": "" if stl_at_bool is None else ("TRUE" if stl_at_bool else "FALSE"),
            "t_stl": "" if t_stl is None else t_stl,
            "delta": "" if t_stl is None else (t_stl - t_bool),
            "premature_boolean": "YES" if premature else "NO",
            "aligned": "YES" if aligned else "NO",
        })

    E_total = len(events)
    E_premature = sum(1 for e in events if e["premature_boolean"] == "YES")
    E_aligned = sum(1 for e in events if e["aligned"] == "YES")

    # SPEC-CORRECT SAD
    sad: Optional[float] = None
    if E_total > 0:
        sad = (E_premature / float(E_total))

    # Table I.2 — Dataset/Run Declaration
    table_i2_path = os.path.join(args.out_dir, "SAD_TABLE_I2_RUN_DECLARATION.csv")
    with open(table_i2_path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["field", "value"])
        w.writerow(["dataset_name", args.dataset_name])
        w.writerow(["dataset_source", args.dataset_source])
        w.writerow(["adapter_name", args.adapter_name])
        w.writerow(["proposition_P", args.proposition])
        w.writerow(["naive_boolean_rule", args.naive_rule])
        w.writerow(["parameters_W", args.W])
        w.writerow(["parameters_tau_s", args.tau_s])
        w.writerow(["parameters_tau_l", args.tau_l])
        w.writerow(["parameters_eps", args.eps])
        w.writerow(["bool_mode", args.bool_mode])
        w.writerow(["threshold_on_d_t", args.threshold])
        w.writerow(["event_counting_mode", args.event_on])
        w.writerow(["adapter_csv", os.path.basename(args.adapter_csv)])
        w.writerow(["trace_csv", os.path.basename(args.trace_csv)])

    # Table I.3 — Event-Level SAD Accounting
    table_i3_path = os.path.join(args.out_dir, "SAD_TABLE_I3_EVENT_ACCOUNTING.csv")
    with open(table_i3_path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["E_total", "E_premature", "E_aligned", "SAD(P)"])
        w.writerow([E_total, E_premature, E_aligned, "" if sad is None else f"{sad:.6f}"])

    # Table I.4 — Timing-Based (Optional but Recommended)
    table_i4_path = os.path.join(args.out_dir, "SAD_TABLE_I4_EVENT_TIMING.csv")
    with open(table_i4_path, "w", encoding="utf-8", newline="\n") as f:
        fieldnames = [
            "event_index", "event_type", "t_bool", "bool_after",
            "stl_at_t_bool", "t_stl", "delta", "premature_boolean", "aligned"
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for e in events:
            w.writerow({k: e.get(k, "") for k in fieldnames})

    # Summary
    summary_path = os.path.join(args.out_dir, "summary.txt")
    with open(summary_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("SAD(P) REPORT (Audit-Grade)\n")
        f.write("----------------------------------------\n")
        f.write(f"dataset_name: {args.dataset_name}\n")
        f.write(f"adapter_name: {args.adapter_name}\n")
        f.write(f"proposition_P: {args.proposition}\n")
        f.write(f"naive_boolean_rule: {args.naive_rule}\n")
        f.write(f"bool_mode: {args.bool_mode}\n")
        f.write(f"threshold_on_d_t: {args.threshold}\n")
        f.write(f"event_counting_mode: {args.event_on}\n")
        f.write("\n")
        f.write("parameters:\n")
        f.write(f"  W={args.W} tau_s={args.tau_s} tau_l={args.tau_l} eps={args.eps}\n")
        f.write("\n")
        f.write("event accounting:\n")
        f.write(f"  E_total={E_total}\n")
        f.write(f"  E_premature={E_premature}\n")
        f.write(f"  E_aligned={E_aligned}\n")
        f.write(f"  SAD(P)={'NA' if sad is None else f'{sad:.6f}'}\n")
        f.write("\n")
        f.write("definition (Appendix G/I):\n")
        f.write("  SAD(P) = E_premature / E_total\n")
        f.write("\n")
        f.write("notes:\n")
        f.write("  - A 'threshold event' is a naive Boolean state change at time t_bool.\n")
        f.write("  - premature_boolean=YES means STL does NOT collapse to the new Boolean truth at t_bool.\n")
        f.write("  - timing table reports when STL eventually collapses (t_stl) and delta=t_stl - t_bool.\n")
        f.write("  - if STL never collapses to that Boolean truth, t_stl is blank and the event is still premature.\n")

    # Manifest: generated files only
    rels = [
        "SAD_TABLE_I2_RUN_DECLARATION.csv",
        "SAD_TABLE_I3_EVENT_ACCOUNTING.csv",
        "SAD_TABLE_I4_EVENT_TIMING.csv",
        "summary.txt",
    ]
    write_manifest(args.out_dir, rels)

    print("OK: SAD report complete")
    print("Output folder:", os.path.abspath(args.out_dir))
    print("SAD_TABLE_I3_EVENT_ACCOUNTING.csv created")


if __name__ == "__main__":
    main()
