#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import hashlib
import os

T5_Z0 = "Z0"
T5_EPLUS = "Eplus"
T5_S = "S"
T5_EMINUS = "Eminus"
T5_ZSTAR = "Zstar"

T5_ALL = [T5_Z0, T5_EPLUS, T5_S, T5_EMINUS, T5_ZSTAR]
T5_STABLE = [T5_S, T5_ZSTAR]

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
    if a == T5_EPLUS:
        return T5_EMINUS
    if a == T5_EMINUS:
        return T5_EPLUS
    return T5_Z0

def AND_s(a: str, b: str) -> str:
    # Conservative form consistent with document:
    if a == T5_ZSTAR or b == T5_ZSTAR:
        return T5_ZSTAR
    if a == T5_S and b == T5_S:
        return T5_S
    # transitional propagation (not used in De Morgan stable test)
    if (a in [T5_Z0, T5_EPLUS, T5_EMINUS]) or (b in [T5_Z0, T5_EPLUS, T5_EMINUS]):
        if a == T5_Z0 and b == T5_Z0:
            return T5_Z0
        if a == T5_EPLUS or b == T5_EPLUS:
            return T5_EPLUS
        if a == T5_EMINUS or b == T5_EMINUS:
            return T5_EMINUS
        return T5_Z0
    return T5_S

def OR_s(a: str, b: str) -> str:
    # Conservative form consistent with document:
    if a == T5_S or b == T5_S:
        return T5_S
    if a == T5_ZSTAR and b == T5_ZSTAR:
        return T5_ZSTAR
    # transitional propagation (not used in De Morgan stable test)
    if (a in [T5_Z0, T5_EPLUS, T5_EMINUS]) or (b in [T5_Z0, T5_EPLUS, T5_EMINUS]):
        if a == T5_Z0 and b == T5_Z0:
            return T5_Z0
        if a == T5_EPLUS or b == T5_EPLUS:
            return T5_EPLUS
        if a == T5_EMINUS or b == T5_EMINUS:
            return T5_EMINUS
        return T5_Z0
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

    out_csv = os.path.join(args.out_dir, "operator_demorgan_involution_v1_5.csv")
    summary = os.path.join(args.out_dir, "summary.txt")

    rows = []
    fails = []

    def add_row(test: str, expr: str, lhs: str, rhs: str, ok: bool) -> None:
        rows.append([test, expr, lhs, rhs, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(f"{test}: {expr} lhs={lhs} rhs={rhs}")

    # 1) NOT_s involution on full T5
    for A in T5_ALL:
        lhs_state = NOT_s(NOT_s(A))
        rhs_state = A
        add_row("INV_NOTs", f"NOT_s(NOT_s({A}))", lhs_state, rhs_state, lhs_state == rhs_state)

    # 2) De Morgan on stable endpoints via phi_T
    for A in T5_STABLE:
        for B in T5_STABLE:
            # DM1: NOT(AND) == OR(NOT, NOT)
            lhs = NOT_bool(phi_T(AND_s(A, B)))
            rhs = phi_T(OR_s(NOT_s(A), NOT_s(B)))
            add_row("DM1_STABLE", f"NOT(phi_T(AND_s({A},{B}))) vs phi_T(OR_s(NOT_s({A}),NOT_s({B})))", lhs, rhs, lhs == rhs)

            # DM2: NOT(OR) == AND(NOT, NOT)
            lhs2 = NOT_bool(phi_T(OR_s(A, B)))
            rhs2 = phi_T(AND_s(NOT_s(A), NOT_s(B)))
            add_row("DM2_STABLE", f"NOT(phi_T(OR_s({A},{B}))) vs phi_T(AND_s(NOT_s({A}),NOT_s({B})))", lhs2, rhs2, lhs2 == rhs2)

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["test", "expression", "lhs", "rhs", "result"])
        for r in rows:
            w.writerow(r)

    with open(summary, "w", encoding="utf-8", newline="\n") as f:
        f.write("STL DEMORGAN + INVOLUTION v1.5\n")
        f.write("Purpose: NOT_s involution on T5 + De Morgan on stable endpoints via phi_T\n")
        f.write(f"Total checks: {len(rows)}\n")
        f.write(f"FAIL count: {len(fails)}\n")
        if fails:
            f.write("Failures:\n")
            for line in fails:
                f.write(f"  {line}\n")
        else:
            f.write("All checks: PASS\n")

    write_manifest(args.out_dir, ["operator_demorgan_involution_v1_5.csv", "summary.txt"])
    print(f"WROTE: {out_csv}")
    print(f"WROTE: {summary}")
    print(f"WROTE: {os.path.join(args.out_dir, 'MANIFEST.sha256')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
