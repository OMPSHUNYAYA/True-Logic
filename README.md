# ⭐ Shunyaya True Logic (STL)

**Govern Collapse Admissibility Before Boolean Evaluation — Without Modifying Classical Logic**

---

![STL](https://img.shields.io/badge/STL-Structural%20Collapse%20Logic-blue)
![Deterministic](https://img.shields.io/badge/Deterministic-Yes-green)
![Replay--Verified](https://img.shields.io/badge/Replay--Verified-B_A%20%3D%20B_B-green)
![Finite--T5](https://img.shields.io/badge/T5%20Truth%20Space-Finite%20(5)--State-green)
![Boolean--Preserved](https://img.shields.io/badge/Boolean%20Logic-Unmodified-green)
![Collapse--Governed](https://img.shields.io/badge/Collapse-Admissibility%20Governed-green)
![Premature--Blocked](https://img.shields.io/badge/Premature%20Collapse-Prohibited-green)
![Operator--Closed](https://img.shields.io/badge/Operator%20Closure-T5%20Closed-green)
![No--Nondeterminism](https://img.shields.io/badge/Nondeterminism-None-green)
![Open--Standard](https://img.shields.io/badge/Standard-Open-blue)

---

**Deterministic • Replay-Verifiable • Audit-Ready • Open Standard**

---

## ✅ 60-Second Verification (Start Here)

STL is defined by exact replay — not interpretation.

Verification succeeds **if and only if**:

`B_A = B_B`

There is:

- No randomness  
- No tolerance  
- No approximate equality  
- No statistical equivalence  

Either artifacts are byte-identical — or the run is **NOT VERIFIED**.

---

## 🔐 Fastest Verification Method (Capsule)

From project root:

### Windows
`VERIFY_STL_CAPSULE\RUN_VERIFY.bat`

### macOS / Linux
`bash VERIFY_STL_CAPSULE/RUN_VERIFY.sh`

Expected output:

```
VERIFY_REPLAY: PASS
SHA256_REPLAY_A_MANIFEST: <hash>
SHA256_REPLAY_B_MANIFEST: <hash>
CAPSULE_FINGERPRINT: PASS
OK: STL capsule verification complete
```

**Expected capsule manifest hash (`REPLAY_A/MANIFEST.sha256`):**

`ca3c6579c0198656d6073e9dc9ce6cf6c953bf316fc17408c78c13db43e0cb44`

If this value differs, the capsule does **not** match this release state.

The capsule performs:

- Deterministic trace generation  
- Deterministic `T5` classification  
- Operator preservation validation  
- Collapse mapping validation  
- `SAD(P)` audit computation  
- `MANIFEST.sha256` generation  
- Independent replay comparison  

If replay identity fails, STL fails.

There is no partial success.

---

## 🔁 Manual Verification (Direct Execution)

From project root:

`python scripts/stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core`

Expected output:

`VERIFY_REPLAY: PASS`

Manual verification confirms deterministic replay equivalence for core conformance.

Capsule fingerprinting additionally enforces pinned release identity via SHA-256 comparison of `MANIFEST.sha256`.

---

## 🔎 Scope Boundary (Read Before Use)

Shunyaya True Logic (STL) is a deterministic structural collapse-governance standard.

It operates strictly at the level of:

- Structural admissibility  
- Collapse timing  
- Replay-verifiable determinism  

It does **not** operate at the level of:

- Magnitude modeling  
- Prediction  
- Optimization  
- Physical simulation  
- Control authority  

STL governs when Boolean values are allowed to collapse.

It does not change what TRUE or FALSE mean.

---

## 🔁 Replay Determinism Rule

Replay determinism is defined strictly as:

`B_A = B_B`

Where equality means:

- Byte-identical CSV/TXT artifacts  
- Identical `T5` classifications  
- Identical operator outcomes  
- Identical collapse mapping  
- Identical `MANIFEST.sha256` file content  
- Identical SHA-256 digest of `MANIFEST.sha256`  

Replay equivalence is structural proof.  
Fingerprint equivalence is release identity proof.

---

## 📂 Dataset Scope & Input Policy

### Core Verification (Authoritative Path)

`--cases core`

Core verification is:

- Fully self-contained  
- Dataset-free  
- Deterministic  
- Replay-complete  

Includes:

- NEGCTL structural sweep  
- Deterministic `T5` classification  
- Operator preservation  
- Collapse mapping validation  
- `SAD(P)` audit accounting  

No external datasets are required for core conformance.

Core replay is the authoritative STL verification pathway.

---

### Optional Extended Verification

`--cases full`

Includes SPX drawdown validation and requires:

`data/SPX_Daily.tsv`

This dataset is **not distributed** in this repository.

Users must independently obtain datasets and comply with original provider licenses.

The repository:

- Does not redistribute datasets  
- Does not embed proprietary data  
- Does not provide financial advice  
- Does not provide cybersecurity advice  

STL performs no prediction, inference, or optimization on these datasets.

---

## 🔎 What Is STL?

STL is a deterministic structural collapse-governance overlay for Boolean evaluation.

It formalizes a simple principle:

**Truth must be structurally admissible before it collapses.**

STL does not:

- Modify Boolean logic  
- Change domain equations  
- Simulate systems  
- Predict outcomes  

It governs collapse — not magnitude.

---

## 🔗 Quick Links

### 📘 Documentation

- [Quickstart Guide](docs/Quickstart.md)  
- [FAQ](docs/FAQ.md)  
- [STL Collapse Model](docs/STL-Collapse-Model.md)  
- [STL Conformance Specification](docs/STL-Conformance-Specification.md)  
- [Collapse Topology Diagram](docs/STL_Collapse_Topology_Diagram.png)  
- [Full Specification (PDF)](docs/STL_v2.0.pdf)  
- [Concept Flyer (High-Level Overview PDF)](docs/Concept-Flyer_STL_v2.0.pdf)

---

### ⚙ Deterministic Verification (Canonical Entrypoint)

Primary conformance script:

- [`scripts/stl_master_verify.py`](scripts/stl_master_verify.py)

Run (core verification):

`python scripts/stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core`

Replay condition:

`B_A = B_B`

Byte identity is required.  
No tolerance.  
No statistical equivalence.

---

### 🧪 Independent Verification Capsule (Recommended First Step)

Verification capsule directory:

- [`VERIFY_STL_CAPSULE/`](VERIFY_STL_CAPSULE/)

Contents:

- [`VERIFY_STL_CAPSULE/README.md`](VERIFY_STL_CAPSULE/README.md)  
- [`VERIFY_STL_CAPSULE/RUN_VERIFY.bat`](VERIFY_STL_CAPSULE/RUN_VERIFY.bat)  
- [`VERIFY_STL_CAPSULE/RUN_VERIFY.sh`](VERIFY_STL_CAPSULE/RUN_VERIFY.sh)  
- [`VERIFY_STL_CAPSULE/EXPECTED_SHA256.txt`](VERIFY_STL_CAPSULE/EXPECTED_SHA256.txt)

Verification succeeds only if replay is byte-identical.

---

### 📂 Replay Evidence Structure

**Runtime outputs (ephemeral — generated locally):**

- [`outputs/`](outputs/)

These are not authoritative and must not be treated as frozen conformance artifacts.

**Authoritative replay-verified reference bundle:**

- [`reference_outputs/`](reference_outputs/)

Conformance is defined by deterministic replay equivalence — not by pre-generated example files.

All replay runs must remain byte-identical under declared scope.

---

### 📜 License

- [`LICENSE`](LICENSE)

Shunyaya True Logic (STL) is published as an open deterministic standard.

Conformance is defined structurally by replay equivalence:

`B_A = B_B`

---

## ⚡ Core Structural Claim

STL demonstrates that:

- Structural truth space can remain finite  
- Boolean logic can remain unchanged  
- Collapse can be governed deterministically  
- Operators can remain closed and conservative  
- Replay execution can remain byte-identical  

Across:

- Synthetic traces  
- Negative control traces  
- Independently obtained regime traces  
- Threshold stress domains  

Without:

- Predictive modeling  
- Probabilistic inference  
- Equation modification  
- Fuzzy blending  

STL governs collapse admissibility — not causation.

---

## 🧠 Core Structural Model

Classical Boolean logic evaluates:

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

STL never alters Boolean truth once stability is achieved.

This invariant is non-negotiable.

---

## 🧱 Structural Truth Space (T5)

`T5 = {Z0, Eplus, S, Eminus, Zstar}`

Interpretation:

- `Z0` — declared structural zero  
- `Eplus` — positive edge transition  
- `S` — stable positive regime  
- `Eminus` — negative edge transition  
- `Zstar` — stable negative regime  

`T5` is:

- Finite  
- Closed under operators  
- Deterministic  
- Replay-stable  

---

## 🧮 Operator Discipline

Structural operators:

`NOT_s`  
`AND_s`  
`OR_s`

Properties:

- Closed over `T5`  
- Deterministic  
- Conservative on stable endpoints  
- Replay-verifiable  

For stable endpoints:

If `A, B in {S, Zstar}` then:

`phi_T(op_s(A,B)) = op_bool(phi_T(A), phi_T(B))`

Transitional states collapse to `UNDEFINED`.

Boolean logic remains intact.

---

## 📊 SAD(P) — Structural Admissibility Alignment Score

`SAD(P) = 1 - (E_premature / E_total)`

Where:

- `E_total` = total Boolean crossing events  
- `E_premature` = premature collapse events  

Some texts use the complementary form:

`SAD_premature = (E_premature / E_total)`

This document reports the alignment score form above.

`SAD(P)`:

- Does not redefine truth  
- Does not alter classification  
- Does not introduce prediction  

It measures structural timing alignment only.

---

## ⏱ Early Structural Admissibility

Let:

`t_bool` = first Boolean crossing time  
`t_struct` = first stable structural collapse time  

If:

`t_struct > t_bool`

STL returns `UNDEFINED` until structural stability is achieved.

STL governs collapse timing — not magnitude.

---

## 🛡 Deterministic Conformance

An implementation conforms to STL **if and only if**:

`B_A = B_B`

- `T5` classification is deterministic  
- Operator closure holds  
- Collapse mapping preserves Boolean logic  
- No nondeterminism is introduced  

Partial conformance is not recognized.

---

## 🛑 What STL Does Not Claim

STL does not:

- Replace Boolean logic  
- Predict system behavior  
- Optimize systems  
- Simulate dynamics  
- Provide probabilistic reasoning  
- Guarantee safety outcomes  

STL governs collapse admissibility only.

---

## 🌍 Open Standard

STL is published as an Open Standard.

- Independent implementations encouraged  
- Conformance defined by deterministic replay  
- No branding dependency  
- No licensing lock-in  

Verification is structural, not institutional.

---

## 👤 Who Is STL For?

- Audit-critical deterministic systems  
- Safety-adjacent admissibility overlays  
- Formal logic research  
- Infrastructure governance studies  
- Deterministic AI reasoning traces  

It is not:

- A predictive engine  
- A physics theory  
- A control system  
- A simulation framework  

STL is a deterministic logical substrate.

---

## 📄 License Summary

Open Standard — observation-only, as-is, no warranty.

Attribution recommended but not required:

Implements Shunyaya True Logic (STL).

---

## 🏷 Topics

Deterministic-Logic • Structural-Truth-Space • Collapse-Governance • Replay-Verification • T5-Logic • Structural-Admissibility • Open-Standard • Shunyaya

---

## One-Line Summary

Shunyaya True Logic (STL) introduces a deterministic five-state structural truth space that governs when Boolean values are allowed to collapse, preserving classical logic while enforcing exact replay equivalence:

`B_A = B_B`
