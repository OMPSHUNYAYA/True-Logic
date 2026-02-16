@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0\.."

echo RUN: STL capsule verification
echo ROOT: %cd%

python scripts\stl_master_verify.py --profile public --out_dir outputs --verify_replay --cases core
if errorlevel 1 (
  echo FAIL: stl_master_verify returned non-zero
  exit /b 1
)

set A=outputs\stl_verify_out\REPLAY_A\MANIFEST.sha256
set B=outputs\stl_verify_out\REPLAY_B\MANIFEST.sha256

if not exist "%A%" (
  echo FAIL: missing %A%
  exit /b 1
)

if not exist "%B%" (
  echo FAIL: missing %B%
  exit /b 1
)

for /f "usebackq delims=" %%H in (`python -c "import hashlib; p=r'%A%'; print(hashlib.sha256(open(p,'rb').read()).hexdigest())"`) do set H_A=%%H
for /f "usebackq delims=" %%H in (`python -c "import hashlib; p=r'%B%'; print(hashlib.sha256(open(p,'rb').read()).hexdigest())"`) do set H_B=%%H

echo SHA256_REPLAY_A_MANIFEST: %H_A%
echo SHA256_REPLAY_B_MANIFEST: %H_B%

for /f "usebackq tokens=1,* delims= " %%X in (`findstr /i /c:"Expected SHA256 (REPLAY_A MANIFEST.sha256):" "VERIFY_STL_CAPSULE\EXPECTED_SHA256.txt"`) do set NEXT_A=1
for /f "usebackq delims=" %%L in (`more +0 "VERIFY_STL_CAPSULE\EXPECTED_SHA256.txt"`) do (
  if defined NEXT_A (
    set EXP_A=%%L
    set NEXT_A=
  )
)

for /f "usebackq tokens=1,* delims= " %%X in (`findstr /i /c:"Expected SHA256 (REPLAY_A MANIFEST.sha256):" "VERIFY_STL_CAPSULE\EXPECTED_SHA256.txt"`) do set FOUND_A=1
if not defined FOUND_A (
  echo FAIL: could not locate expected hash label in EXPECTED_SHA256.txt
  exit /b 1
)

rem Extract expected hash by reading the line after the label
set EXP_A=
set SKIP=0
for /f "usebackq delims=" %%L in (`type "VERIFY_STL_CAPSULE\EXPECTED_SHA256.txt"`) do (
  if "!SKIP!"=="1" (
    if not "%%L"=="" (
      set EXP_A=%%L
      goto :got_expected
    )
  )
  echo %%L | findstr /i /c:"Expected SHA256 (REPLAY_A MANIFEST.sha256):" >nul
  if not errorlevel 1 set SKIP=1
)

:got_expected
if "%EXP_A%"=="" (
  echo FAIL: expected hash not found in EXPECTED_SHA256.txt
  exit /b 1
)

if /i not "%H_A%"=="%EXP_A%" (
  echo FAIL: CAPSULE_FINGERPRINT mismatch
  echo EXPECTED: %EXP_A%
  echo ACTUAL:   %H_A%
  exit /b 1
)

if /i not "%H_B%"=="%EXP_A%" (
  echo FAIL: REPLAY_B MANIFEST mismatch vs expected
  echo EXPECTED: %EXP_A%
  echo ACTUAL:   %H_B%
  exit /b 1
)

echo CAPSULE_FINGERPRINT: PASS
echo OK: STL capsule verification complete
exit /b 0
