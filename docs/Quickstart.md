# ⭐ Shunyaya True Logic (STL)
## Quickstart

**Deterministic • Replay-Verifiable • Collapse-Governed**  
No Prediction • No Equation Modification • No Control Injection

---

## What You Need to Know First

Shunyaya True Logic (STL) is intentionally conservative.

STL does **not**:

- Modify Boolean logic  
- Modify domain equations  
- Introduce predictive models  
- Simulate physical processes  
- Inject control logic  
- Optimize systems  
- Replace classical evaluation  

STL overlays a deterministic structural collapse-governance layer over existing deterministic evaluations.

It:

- Observes structural stability  
- Governs collapse admissibility  
- Preserves classical truth values  
- Produces replay-verifiable artifacts  

---

## Core Invariant (Non-Negotiable)

Collapse mapping:

`phi_T(S) = TRUE`  
`phi_T(Zstar) = FALSE`

For all other structural states:

`phi_T(state) = UNDEFINED`

STL never alters classical truth once structurally stable.

---

## Requirements

- Python 3.9+ (CPython recommended)  
- Standard library only  
- No external dependencies  

All validation is:

- Deterministic  
- Replay-verifiable  
- Byte-identical across machines  
- Offline-capable  

No randomness.  
No training.  
No statistical inference.  
No adaptive tuning.

---

## What Quickstart Guarantees

If you follow this Quickstart exactly, you will verify:

`B_A = B_B`

without:

- Modifying any scripts  
- Inspecting internal code  
- Trusting documentation claims  

Verification proves:

- Deterministic trace generation  
- Deterministic T5 classification  
- Deterministic operator preservation  
- Deterministic collapse mapping  
- Deterministic `SAD(P)` audit accounting  
- Byte-identical artifact bundles  

If verification fails, STL fails.  
There is no partial success.

---

# Repository Layout (Public Release)

```
STL/
├── README.md
├── LICENSE
│
├── docs/
│   ├── Quickstart.md
│   ├── FAQ.md
│   ├── STL-Collapse-Model.md
│   ├── STL-Conformance-Specification.md
│   ├── STL_v2.0.pdf
│   ├── Concept-Flyer_STL_v2.0.pdf
│   └── STL_Collapse_Topology_Diagram.png
│
├── scripts/                         # Authoritative conformance scripts
│   ├── stl_master_verify.py
│   ├── stl_master_verify_public_release_baseline.py
│   ├── stl_make_negctl_debounced_trace_v1_0.py
│   ├── stl_t5_classifier_v1_0.py
│   ├── stl_operator_preservation_v1_3.py
│   ├── stl_sad_report_v1_0.py
│   ├── stl_sad_report_debounced_bool_v1_0.py
│   ├── stl_make_ice_like_dataset_v1_1.py
│   └── stl_make_d_from_spx_drawdown_v1_0.py
│
├── scripts_optional/                # Extended / research adapters (non-core)
│   ├── stl_demorgan_involution_v1_5.py
│   ├── stl_transition_propagation_v1_4.py
│   ├── stl_make_threshold_stress_v1_2.py
│   ├── stl_make_ice_like_dataset_v1_0.py
│   ├── stl_make_d_from_cicids2017_v1_0.py
│   ├── stl_make_d_from_cicids2017_parquet_v1_0.py
│   └── stl_make_d_from_cicids2017_parquet_rowbin_v1_0.py
│
├── outputs/                         # Ephemeral run outputs (empty in repo)
│   └── README.md
│
├── reference_outputs/               # Frozen replay-verified artifacts
│   ├── README.md
│   └── stl_core__cases_core__replay_verify_pass/
│
├── examples/
│   └── README.md
│
├── VERIFY_STL_CAPSULE/              # Deterministic verification entry point
│   ├── EXPECTED_SHA256.txt
│   ├── RUN_VERIFY.bat
│   ├── RUN_VERIFY.sh
│   └── README.md
│
└── STL_SAD_CAPSULE/                 # Quantification integrity capsule
    ├── CAPSULE_MANIFEST.sha256
    └── README_CAPSULE.md
```

This layout is deterministic, replay-complete, and self-contained.

---

# Verification Path (Recommended)

From project root:

### Windows

`python scripts\stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core`

### macOS / Linux

`python scripts/stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core`

This performs:

- Deterministic trace generation  
- Deterministic T5 classification  
- Operator preservation checks  
- Collapse mapping validation  
- `SAD(P)` audit computation  
- `MANIFEST.sha256` generation  
- Replay comparison  

Verification succeeds **only if**:

`VERIFY_REPLAY: PASS`

and

`B_A = B_B`

Equality requires:

- Byte-identical files  
- Identical T5 classification sequences  
- Identical operator outputs  
- Identical collapse outputs  
- Identical `MANIFEST.sha256` content and digest values  

Byte identity is required.  
No tolerance.  
No statistical interpretation.  
No manual review required.

---

# Dataset Scope

Default verification mode:

`--cases core`

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
- `SAD(P)` audit accounting  

No external datasets are required for core conformance.

Optional extended verification:

`--cases full`

Includes SPX drawdown validation and requires:

`data/SPX_Daily.tsv`

This dataset is **not distributed** in the repository and must be independently obtained.

Core verification remains the authoritative conformance pathway.

---

# Capsule Fingerprint Verification (Fastest Path)

To validate sealed release identity:

### Windows

`VERIFY_STL_CAPSULE\RUN_VERIFY.bat`

### macOS / Linux

`bash VERIFY_STL_CAPSULE/RUN_VERIFY.sh`

Authoritative release fingerprint:

`SHA256(outputs/stl_verify_out/REPLAY_A/MANIFEST.sha256)`

=

`ca3c6579c0198656d6073e9dc9ce6cf6c953bf316fc17408c78c13db43e0cb44`

If this value differs, the capsule does not match this release state.

Successful verification confirms:

- `VERIFY_REPLAY: PASS`  
- `CAPSULE_FINGERPRINT: PASS`

The capsule acts as a deterministic integrity anchor.

This file is generated during verification under outputs/.

---

# Core Structural Model

Classical Boolean systems evaluate:

`m in {TRUE, FALSE}`

STL evaluates structural state:

`state in {Z0, Eplus, S, Eminus, Zstar}`

Collapse mapping:

`phi_T : T5 -> {TRUE, FALSE, UNDEFINED}`

`phi_T(S) = TRUE`  
`phi_T(Zstar) = FALSE`  
`phi_T(Z0) = UNDEFINED`  
`phi_T(Eplus) = UNDEFINED`  
`phi_T(Eminus) = UNDEFINED`

`UNDEFINED` is not a Boolean value and does not modify classical truth tables.

Only `S` and `Zstar` collapse to Boolean truth.

---

# SAD(P) — Structural Admissibility Discipline

`SAD(P) = 1 - (E_premature / E_total)`

Where:

- `E_total` = total Boolean crossing events  
- `E_premature` = collapse events occurring before structural stabilization  

`SAD(P)` is:

- An audit alignment metric  
- Not a truth metric  
- Not predictive  

It measures structural timing alignment only.

---

# Deterministic Replay Rule

Two independent executions, under identical declared inputs, must produce byte-identical artifact bundles.

Only then is STL validation reproducible under declared scope.

---

# What STL Is Not

STL does not:

- Replace Boolean logic  
- Modify domain equations  
- Predict system behavior  
- Simulate physical systems  
- Guarantee safety outcomes  
- Provide probabilistic reasoning  
- Perform optimization  

STL governs collapse admissibility — not causation.

---

# One-Line Summary

Shunyaya True Logic (STL) introduces a deterministic five-state structural truth space that governs collapse admissibility before Boolean evaluation, verified through exact replay equivalence `B_A = B_B`, without modifying classical logic or introducing predictive behavior.
