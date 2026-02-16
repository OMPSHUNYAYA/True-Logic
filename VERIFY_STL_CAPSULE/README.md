⭐ Shunyaya True Logic (STL)

VERIFY_STL_CAPSULE

Deterministic • Replay-Verifiable • Audit-Ready • Open Standard

This capsule provides a blind verification path for STL.

Verification succeeds only if:

`B_A = B_B`

Where equality means byte-identical artifact bundles across independent replay.

No randomness.
No tolerance.
No statistical equivalence.

What this capsule does

1) Runs the canonical entrypoint:

`python scripts/stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core`

2) Verifies replay identity (REPLAY_A vs REPLAY_B)

3) Computes SHA-256 fingerprints of:
- `outputs/stl_verify_out/REPLAY_A/MANIFEST.sha256`
- `outputs/stl_verify_out/REPLAY_B/MANIFEST.sha256`

4) Compares them against the pinned expected values in:
`VERIFY_STL_CAPSULE/EXPECTED_SHA256.txt`

If the pinned fingerprint matches and replay passes, verification is successful.

Run (Windows)

`VERIFY_STL_CAPSULE\RUN_VERIFY.bat`

Run (Linux/macOS)

`bash VERIFY_STL_CAPSULE/RUN_VERIFY.sh`

Expected PASS output

`VERIFY_REPLAY: PASS`
`CAPSULE_FINGERPRINT: PASS`

If any check fails, STL verification fails under this declared scope.

Scope (core cases)

- NEGCTL_SWEEP
- OPERATOR_PRESERVATION
- SPX_DRAWDOWN_CORE

Outputs

All artifacts are written under:

`outputs/stl_verify_out/`

This capsule does not modify scripts or inputs.
It verifies determinism by exact replay and pinned fingerprints.

License

Open Standard (as-is, observation-only, no warranty).
