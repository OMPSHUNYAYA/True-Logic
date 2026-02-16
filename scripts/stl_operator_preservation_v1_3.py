#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import os

T5_S = "S"
T5_ZSTAR = "Zstar"

def phi_T(state: str) -> str:
    if state == T5_S:
        return "TRUE"
    if state == T5_ZSTAR:
        return "FALSE"
    return "UNDEFINED"

def NOT_bool(x: str) -> str:
    return "FALSE" if x == "TRUE" else "TRUE"

def AND_bool(a: str, b: str) -> str:
    return "TRUE" if (a == "TRUE" and b == "TRUE") else "FALSE"

def OR_bool(a: str, b: str) -> str:
    return "TRUE" if (a == "TRUE" or b == "TRUE") else "FALSE"

def NOT_s(a: str) -> str:
    if a == T5_S:
        return T5_ZSTAR
    if a == T5_ZSTAR:
        return T5_S
    return a

def AND_s(a: str, b: str) -> str:
    # Stable endpoint table (conservative):
    if a == T5_ZSTAR or b == T5_ZSTAR:
        return T5_ZSTAR
    return T5_S

def OR_s(a: str, b: str) -> str:
    # Stable endpoint table (conservative):
    if a == T5_S or b == T5_S:
        return T5_S
    return T5_ZSTAR

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

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", required=True)
    args = ap.parse_args()

    ensure_dir(args.out_dir)

    out_csv = os.path.join(args.out_dir, "operator_preservation_v1_3.csv")
    summary = os.path.join(args.out_dir, "summary.txt")

    stable = [T5_S, T5_ZSTAR]

    rows = []
    fails = []

    # NOT test
    for A in stable:
        phiA = phi_T(A)
        lhs = phi_T(NOT_s(A))
        rhs = NOT_bool(phiA)
        ok = (lhs == rhs)
        rows.append(["NOT", A, "", lhs, rhs, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(f"NOT fail: A={A} lhs={lhs} rhs={rhs}")

    # AND test
    for A in stable:
        for B in stable:
            phiA = phi_T(A)
            phiB = phi_T(B)
            lhs = phi_T(AND_s(A, B))
            rhs = AND_bool(phiA, phiB)
            ok = (lhs == rhs)
            rows.append(["AND", A, B, lhs, rhs, "PASS" if ok else "FAIL"])
            if not ok:
                fails.append(f"AND fail: A={A} B={B} lhs={lhs} rhs={rhs}")

    # OR test
    for A in stable:
        for B in stable:
            phiA = phi_T(A)
            phiB = phi_T(B)
            lhs = phi_T(OR_s(A, B))
            rhs = OR_bool(phiA, phiB)
            ok = (lhs == rhs)
            rows.append(["OR", A, B, lhs, rhs, "PASS" if ok else "FAIL"])
            if not ok:
                fails.append(f"OR fail: A={A} B={B} lhs={lhs} rhs={rhs}")

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["op", "A", "B", "lhs_phi_T(op_s(...))", "rhs_op_bool(phi_T(...))", "result"])
        for r in rows:
            w.writerow(r)

    with open(summary, "w", encoding="utf-8", newline="\n") as f:
        f.write("STL OPERATOR PRESERVATION v1.3\n")
        f.write("Domain: stable endpoint homomorphism check\n")
        f.write("Stable set: {S, Zstar}\n")
        f.write(f"Total checks: {len(rows)}\n")
        f.write(f"FAIL count: {len(fails)}\n")
        if fails:
            f.write("Failures:\n")
            for line in fails:
                f.write(f"  {line}\n")
        else:
            f.write("All checks: PASS\n")

    write_manifest(args.out_dir, ["operator_preservation_v1_3.csv", "summary.txt"])
    print(f"WROTE: {out_csv}")
    print(f"WROTE: {summary}")
    print(f"WROTE: {os.path.join(args.out_dir, 'MANIFEST.sha256')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
