# outputs/

This folder is intentionally empty in the public repository.

It serves as the runtime output directory for STL verification commands.

Artifacts generated here are **ephemeral** and are not considered authoritative.

---

## What This Folder Is For

When executing:

`python scripts/stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core`

STL will generate:

- `stl_verify_out/`
- `stl_verify_out/REPLAY_A/`
- `stl_verify_out/REPLAY_B/`
- Deterministic trace artifacts
- `stl_verify_out/**/MANIFEST.sha256`
- `stl_verify_out/**/summary.txt`

These are runtime artifacts created during verification.

---

## What This Folder Is NOT

- It is not the canonical reference bundle  
- It does not contain frozen verification artifacts  
- It does not replace `reference_outputs/`  
- It does not define conformance  

Authoritative replay-verified core conformance artifacts are stored under:

`reference_outputs/`

---

## Reproducibility

To reproduce canonical reference outputs:

`python scripts/stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core`

Expected:

`VERIFY_REPLAY: PASS`

---

This separation preserves:

- Deterministic execution discipline  
- Clear distinction between runtime outputs and frozen reference artifacts  
- Structural clarity within the STL repository
