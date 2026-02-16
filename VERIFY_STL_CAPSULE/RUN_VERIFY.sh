#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

echo "RUN: STL capsule verification"
echo "ROOT: $(pwd)"

python scripts/stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core

A="outputs/stl_verify_out/REPLAY_A/MANIFEST.sha256"
B="outputs/stl_verify_out/REPLAY_B/MANIFEST.sha256"

if [ ! -f "$A" ]; then
  echo "FAIL: missing $A"
  exit 1
fi

if [ ! -f "$B" ]; then
  echo "FAIL: missing $B"
  exit 1
fi

H_A="$(python -c "import hashlib; p='$A'; print(hashlib.sha256(open(p,'rb').read()).hexdigest())")"
H_B="$(python -c "import hashlib; p='$B'; print(hashlib.sha256(open(p,'rb').read()).hexdigest())")"

echo "SHA256_REPLAY_A_MANIFEST: $H_A"
echo "SHA256_REPLAY_B_MANIFEST: $H_B"

EXP_A="$(awk 'found{print; exit} /Expected SHA256 \(REPLAY_A MANIFEST.sha256\):/{found=1}' VERIFY_STL_CAPSULE/EXPECTED_SHA256.txt | tr -d '\r')"

if [ -z "${EXP_A:-}" ]; then
  echo "FAIL: expected hash not found in VERIFY_STL_CAPSULE/EXPECTED_SHA256.txt"
  exit 1
fi

if [ "$H_A" != "$EXP_A" ]; then
  echo "FAIL: CAPSULE_FINGERPRINT mismatch"
  echo "EXPECTED: $EXP_A"
  echo "ACTUAL:   $H_A"
  exit 1
fi

if [ "$H_B" != "$EXP_A" ]; then
  echo "FAIL: REPLAY_B MANIFEST mismatch vs expected"
  echo "EXPECTED: $EXP_A"
  echo "ACTUAL:   $H_B"
  exit 1
fi

echo "CAPSULE_FINGERPRINT: PASS"
echo "OK: STL capsule verification complete"
