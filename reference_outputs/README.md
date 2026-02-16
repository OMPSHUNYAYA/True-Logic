# STL Reference Outputs
## Dataset-Free Core Proof

This folder contains reference artifacts produced by running the STL public verification in dataset-free mode:

`--cases core`

These reference outputs are provided for transparency and audit inspection.

They are **NOT required** to run STL, and they do **NOT replace independent verification**.

---

## 1) What These Reference Outputs Prove

The included bundle demonstrates STL’s conformance-critical property:

`B_A = B_B`

Meaning:

- Two independent executions (`REPLAY_A` and `REPLAY_B`)
- Under identical declared inputs and locked parameters
- Produce byte-identical artifacts (including identical `MANIFEST.sha256` content)

This is replay determinism by evidence — not interpretation.

---

## 2) What These Reference Outputs Contain

Folder:

`stl_core__cases_core__replay_verify_pass/`

Contains:

`REPLAY_A/`  
`REPLAY_B/`

Each replay includes:

- `NEGCTL_SWEEP/`  
  - `TRACE/` (deterministic trace generation)  
  - `CLASSIFY/` (deterministic T5 classification)  
  - `SAD/` (deterministic `SAD(P)` audit tables)

- `OPERATOR_PRESERVATION/`  
  (deterministic operator preservation checks)

- `MANIFEST.sha256` (artifact digest list)  
- `summary.txt` (human-readable run summary)

---

## 3) What These Reference Outputs Do NOT Claim

- No prediction is performed  
- No domain equations are modified  
- No control logic is injected  
- No probabilistic inference is used  
- No external datasets are distributed here  
- These artifacts are not financial, security, or medical advice  

These reference outputs demonstrate structural determinism only.

---

## 4) How to Reproduce (Recommended)

From project root:

### Windows

`python scripts\stl_master_verify_public_release_baseline.py --profile public --out_dir outputs__core_verify --verify_replay --cases core`

### macOS / Linux

`python scripts/stl_master_verify_public_release_baseline.py --profile public --out_dir outputs__core_verify --verify_replay --cases core`

Expected:

`VERIFY_REPLAY: PASS`

This reproduces the same directory shape as this reference bundle.

---

## 5) Canonical Verification Method (Capsule)

For fastest verification of the sealed capsule fingerprint:

### Windows

`VERIFY_STL_CAPSULE\RUN_VERIFY.bat`

### macOS / Linux

`bash VERIFY_STL_CAPSULE/RUN_VERIFY.sh`

Expected:

`VERIFY_REPLAY: PASS`  
`CAPSULE_FINGERPRINT: PASS`  
`OK: STL capsule verification complete`
