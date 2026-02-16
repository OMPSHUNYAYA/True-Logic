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
T5_TRANS = [T5_Z0, T5_EPLUS, T5_EMINUS]
T5_STABLE = [T5_S, T5_ZSTAR]

def phi_T(state: str) -> str:
    if state == T5_S:
        return "TRUE"
    if state == T5_ZSTAR:
        return "FALSE"
    return "UNDEFINED"

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
    # Conservative form:
    # 1) Stable FALSE dominates
    if a == T5_ZSTAR or b == T5_ZSTAR:
        return T5_ZSTAR
    # 2) Both stable TRUE -> stable TRUE
    if a == T5_S and b == T5_S:
        return T5_S
    # 3) Any transitional input with no Zstar -> transitional (conservative uncertainty)
    if (a in T5_TRANS) or (b in T5_TRANS):
        # if both Z0 -> Z0 else preserve direction if possible
        if a == T5_Z0 and b == T5_Z0:
            return T5_Z0
        if a == T5_EPLUS or b == T5_EPLUS:
            return T5_EPLUS
        if a == T5_EMINUS or b == T5_EMINUS:
            return T5_EMINUS
        return T5_Z0
    # 4) Remaining case: (S with something non-transitional and not Zstar) -> S
    return T5_S

def OR_s(a: str, b: str) -> str:
    # Conservative form:
    # 1) Stable TRUE dominates
    if a == T5_S or b == T5_S:
        return T5_S
    # 2) Both stable FALSE -> stable FALSE
    if a == T5_ZSTAR and b == T5_ZSTAR:
        return T5_ZSTAR
    # 3) Any transitional input with no S -> transitional (conservative uncertainty)
    if (a in T5_TRANS) or (b in T5_TRANS):
        if a == T5_Z0 and b == T5_Z0:
            return T5_Z0
        if a == T5_EPLUS or b == T5_EPLUS:
            return T5_EPLUS
        if a == T5_EMINUS or b == T5_EMINUS:
            return T5_EMINUS
        return T5_Z0
    # 4) Remaining case: (Zstar with something non-transitional and not S) -> Zstar
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

    out_csv = os.path.join(args.out_dir, "operator_transition_propagation_v1_4.csv")
    summary = os.path.join(args.out_dir, "summary.txt")

    rows = []
    fails = []

    def add_check(name: str, expr: str, ok: bool) -> None:
        rows.append([name, expr, "PASS" if ok else "FAIL"])
        if not ok:
            fails.append(f"{name}: {expr}")

    # 1) Dominance laws
    for X in T5_ALL:
        out1 = OR_s(T5_S, X)
        add_check("DOM_OR_S", f"OR_s(S,{X})={out1} phi={phi_T(out1)} expected TRUE", phi_T(out1) == "TRUE")

        out2 = AND_s(T5_ZSTAR, X)
        add_check("DOM_AND_ZSTAR", f"AND_s(Zstar,{X})={out2} phi={phi_T(out2)} expected FALSE", phi_T(out2) == "FALSE")

    # 2) No accidental collapse: transition-only pairs must remain UNDEFINED
    for A in T5_TRANS:
        for B in T5_TRANS:
            out_and = AND_s(A, B)
            add_check("NOACC_AND_TRANS", f"AND_s({A},{B})={out_and} phi={phi_T(out_and)} expected UNDEFINED", phi_T(out_and) == "UNDEFINED")

            out_or = OR_s(A, B)
            add_check("NOACC_OR_TRANS", f"OR_s({A},{B})={out_or} phi={phi_T(out_or)} expected UNDEFINED", phi_T(out_or) == "UNDEFINED")

    # 3) Mixed stable+transitional conservative behavior
    for X in T5_TRANS:
        out_and = AND_s(T5_S, X)
        add_check("MIX_AND_S_TRANS", f"AND_s(S,{X})={out_and} phi={phi_T(out_and)} expected UNDEFINED", phi_T(out_and) == "UNDEFINED")

        out_or = OR_s(T5_ZSTAR, X)
        add_check("MIX_OR_ZSTAR_TRANS", f"OR_s(Zstar,{X})={out_or} phi={phi_T(out_or)} expected UNDEFINED", phi_T(out_or) == "UNDEFINED")

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["check", "expression", "result"])
        for r in rows:
            w.writerow(r)

    with open(summary, "w", encoding="utf-8", newline="\n") as f:
        f.write("STL TRANSITION PROPAGATION v1.4\n")
        f.write("Purpose: dominance + no-accidental-collapse checks\n")
        f.write(f"Total checks: {len(rows)}\n")
        f.write(f"FAIL count: {len(fails)}\n")
        if fails:
            f.write("Failures:\n")
            for line in fails:
                f.write(f"  {line}\n")
        else:
            f.write("All checks: PASS\n")

    write_manifest(args.out_dir, ["operator_transition_propagation_v1_4.csv", "summary.txt"])
    print(f"WROTE: {out_csv}")
    print(f"WROTE: {summary}")
    print(f"WROTE: {os.path.join(args.out_dir, 'MANIFEST.sha256')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
