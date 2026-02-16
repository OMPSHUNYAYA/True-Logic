# Shunyaya True Logic (STL)
## VERIFY_STL_CAPSULE

Deterministic • Replay-Verifiable • Audit-Ready • Open Standard

---

## Purpose

This capsule provides a blind verification pathway for STL core conformance.

Verification succeeds **only if**:

`B_A = B_B`

Where equality means byte-identical artifact bundles across independent replay.

There is:

- No randomness  
- No tolerance  
- No approximate equality  
- No statistical equivalence  

Either replay is identical — or verification fails.

---

## What This Capsule Does

1) Runs the canonical entrypoint:

`python scripts/stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core`

2) Verifies replay identity (REPLAY_A vs REPLAY_B)

3) Computes SHA-256 fingerprints of:

- `outputs/stl_verify_out/REPLAY_A/MANIFEST.sha256`
- `outputs/stl_verify_out/REPLAY_B/MANIFEST.sha256`

4) Compares them against the pinned expected value in:

`VERIFY_STL_CAPSULE/EXPECTED_SHA256.txt`

If replay passes and the pinned fingerprint matches, verification succeeds.

---

## Run Instructions

### Windows

`VERIFY_STL_CAPSULE\RUN_VERIFY.bat`

### Linux / macOS

`bash VERIFY_STL_CAPSULE/RUN_VERIFY.sh`

---

## Expected PASS Output

`VERIFY_REPLAY: PASS`  
`CAPSULE_FINGERPRINT: PASS`

If any check fails, STL verification fails under this declared scope.

There is no partial success.

---

## Scope (Core Conformance)

Core verification is:

- Dataset-free  
- Fully self-contained  
- Deterministic  
- Replay-complete  

It includes:

- NEGCTL structural sweep  
- Deterministic T5 classification  
- Operator preservation  
- Collapse mapping validation  
- SAD(P) audit computation  

No external datasets are required for authoritative verification.

---

## Outputs

All artifacts are written under:

`outputs/stl_verify_out/`

This capsule does not modify scripts or inputs.  
It verifies determinism strictly through exact replay and pinned fingerprint comparison.

---

## License

Open Standard — observation-only, as-is, no warranty.


