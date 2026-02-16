import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_ARGS = 2
EXIT_MISSING = 3
EXIT_INVARIANT = 4

CORE_CASES = ["NEGCTL_SWEEP", "OPERATOR_PRESERVATION"]
FULL_CASES = ["NEGCTL_SWEEP", "OPERATOR_PRESERVATION", "SPX_DRAWDOWN_CORE"]

LOCKED_PARAMS = {
    "W": "20",
    "tau_s": "0.90",
    "tau_l": "0.10",
    "eps": "0.02",
}

DATA_SPX_CORE = Path("data") / "SPX_Daily.tsv"

SCRIPT_NEGCTL_TRACE = Path("scripts") / "stl_make_negctl_debounced_trace_v1_0.py"
SCRIPT_CLASSIFIER = Path("scripts") / "stl_t5_classifier_v1_0.py"
SCRIPT_SAD_REPORT = Path("scripts") / "stl_sad_report_v1_0.py"
SCRIPT_OP_PRES = Path("scripts") / "stl_operator_preservation_v1_3.py"
SCRIPT_SPX_ADAPTER = Path("scripts") / "stl_make_d_from_spx_drawdown_v1_0.py"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def relpath_posix(p: Path, base: Path) -> str:
    return p.relative_to(base).as_posix()


def write_manifest(dir_path: Path, manifest_name: str = "MANIFEST.sha256") -> None:
    files = []
    for p in dir_path.rglob("*"):
        if p.is_file() and p.name != manifest_name:
            files.append(p)

    files.sort(key=lambda x: relpath_posix(x, dir_path))
    lines = [f"{sha256_file(p)}  {relpath_posix(p, dir_path)}" for p in files]

    out = dir_path / manifest_name
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")


def ensure_clean_dir(p: Path) -> None:
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)


def run_py(args_list, env):
    cp = subprocess.run(
        [sys.executable] + args_list,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if cp.returncode != 0:
        sys.stdout.write(cp.stdout)
        sys.stderr.write(cp.stderr)
        raise RuntimeError(f"subprocess failed: {args_list}")
    return cp.stdout


def compare_dirs(a: Path, b: Path) -> bool:
    a_files = sorted([p for p in a.rglob("*") if p.is_file()], key=lambda x: relpath_posix(x, a))
    b_files = sorted([p for p in b.rglob("*") if p.is_file()], key=lambda x: relpath_posix(x, b))

    if [relpath_posix(p, a) for p in a_files] != [relpath_posix(p, b) for p in b_files]:
        return False

    for ap in a_files:
        rp = relpath_posix(ap, a)
        bp = b / rp
        if ap.stat().st_size != bp.stat().st_size:
            return False
        if sha256_file(ap) != sha256_file(bp):
            return False

    return True


def require_file(p: Path):
    if not p.exists():
        raise FileNotFoundError(str(p))


def summary_write(p: Path, lines):
    p.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")


def build_env():
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    env["TZ"] = "UTC"
    return env


def count_csv_rows(csv_path: Path) -> int:
    n = 0
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        first = True
        for line in f:
            if first:
                first = False
                continue
            if line.strip():
                n += 1
    return n


def normalize_classifier_summary(classify_dir: Path, in_csv: Path):
    summary_path = classify_dir / "summary.txt"
    if not summary_path.exists():
        return

    rows_in = count_csv_rows(in_csv) if in_csv.exists() else 0
    trace_csv = classify_dir / "stl_trace_out.csv"
    rows_out = count_csv_rows(trace_csv) if trace_csv.exists() else 0

    lines = [
        "STL_T5_CLASSIFIER",
        f"in_csv={in_csv.name}",
        f"W={LOCKED_PARAMS['W']}",
        f"tau_s={LOCKED_PARAMS['tau_s']}",
        f"tau_l={LOCKED_PARAMS['tau_l']}",
        f"eps={LOCKED_PARAMS['eps']}",
        f"rows_in={rows_in}",
        f"rows_out={rows_out}",
        "OK",
    ]
    summary_write(summary_path, lines)


def do_negctl_sweep(out_case_dir: Path, env):
    require_file(SCRIPT_NEGCTL_TRACE)
    require_file(SCRIPT_CLASSIFIER)
    require_file(SCRIPT_SAD_REPORT)

    ensure_clean_dir(out_case_dir)

    trace_dir = out_case_dir / "TRACE"
    trace_dir.mkdir(parents=True, exist_ok=True)

    run_py([str(SCRIPT_NEGCTL_TRACE), "--out_dir", str(trace_dir)], env)

    trace_csv = trace_dir / "negctl_debounced_trace_v1_0.csv"
    require_file(trace_csv)

    classify_dir = out_case_dir / "CLASSIFY"
    classify_dir.mkdir(parents=True, exist_ok=True)

    run_py(
        [
            str(SCRIPT_CLASSIFIER),
            "--in_csv",
            str(trace_csv),
            "--out_dir",
            str(classify_dir),
            "--W",
            LOCKED_PARAMS["W"],
            "--tau_s",
            LOCKED_PARAMS["tau_s"],
            "--tau_l",
            LOCKED_PARAMS["tau_l"],
            "--eps",
            LOCKED_PARAMS["eps"],
        ],
        env,
    )

    trace_out = classify_dir / "stl_trace_out.csv"
    require_file(trace_out)

    normalize_classifier_summary(classify_dir, trace_csv)

    sad_dir = out_case_dir / "SAD"
    sad_dir.mkdir(parents=True, exist_ok=True)

    run_py(
        [
            str(SCRIPT_SAD_REPORT),
            "--adapter_csv",
            str(trace_csv),
            "--trace_csv",
            str(trace_out),
            "--out_dir",
            str(sad_dir),
            "--dataset_name",
            "NEGCTL_SYNTH",
            "--dataset_source",
            "STL_NEGATIVE_CONTROL",
            "--adapter_name",
            "stl_make_negctl_debounced_trace_v1_0",
            "--proposition",
            "NEGCTL_T5_CLASSIFICATION",
            "--naive_rule",
            "raw_threshold_crossing",
            "--bool_mode",
            "ge",
            "--threshold",
            "0.5",
            "--event_on",
            "enter_true",
            "--W",
            LOCKED_PARAMS["W"],
            "--tau_s",
            LOCKED_PARAMS["tau_s"],
            "--tau_l",
            LOCKED_PARAMS["tau_l"],
            "--eps",
            LOCKED_PARAMS["eps"],
        ],
        env,
    )

    summary_write(out_case_dir / "summary.txt", ["CASE: NEGCTL_SWEEP", "OK"])

    write_manifest(trace_dir)
    write_manifest(classify_dir)
    write_manifest(sad_dir)
    write_manifest(out_case_dir)


def do_operator_preservation(out_case_dir: Path, env):
    require_file(SCRIPT_OP_PRES)
    ensure_clean_dir(out_case_dir)

    run_py([str(SCRIPT_OP_PRES), "--out_dir", str(out_case_dir)], env)

    if not (out_case_dir / "summary.txt").exists():
        summary_write(out_case_dir / "summary.txt", ["CASE: OPERATOR_PRESERVATION", "OK"])

    write_manifest(out_case_dir)


def do_spx_drawdown_core(out_case_dir: Path, env):
    require_file(SCRIPT_SPX_ADAPTER)
    require_file(SCRIPT_CLASSIFIER)
    require_file(SCRIPT_SAD_REPORT)
    require_file(DATA_SPX_CORE)

    ensure_clean_dir(out_case_dir)

    adapter_dir = out_case_dir / "ADAPTER"
    adapter_dir.mkdir(parents=True, exist_ok=True)

    run_py([str(SCRIPT_SPX_ADAPTER), "--in_tsv", str(DATA_SPX_CORE), "--out_dir", str(adapter_dir)], env)

    adapter_csv = adapter_dir / "stl_input_t_d.csv"
    require_file(adapter_csv)

    classify_dir = out_case_dir / "CLASSIFY"
    classify_dir.mkdir(parents=True, exist_ok=True)

    run_py(
        [
            str(SCRIPT_CLASSIFIER),
            "--in_csv",
            str(adapter_csv),
            "--out_dir",
            str(classify_dir),
            "--W",
            LOCKED_PARAMS["W"],
            "--tau_s",
            LOCKED_PARAMS["tau_s"],
            "--tau_l",
            LOCKED_PARAMS["tau_l"],
            "--eps",
            LOCKED_PARAMS["eps"],
        ],
        env,
    )

    trace_csv = classify_dir / "stl_trace_out.csv"
    require_file(trace_csv)

    normalize_classifier_summary(classify_dir, adapter_csv)

    sad_dir = out_case_dir / "SAD"
    sad_dir.mkdir(parents=True, exist_ok=True)

    run_py(
        [
            str(SCRIPT_SAD_REPORT),
            "--adapter_csv",
            str(adapter_csv),
            "--trace_csv",
            str(trace_csv),
            "--out_dir",
            str(sad_dir),
            "--dataset_name",
            "SPX_DRAWDOWN_CORE",
            "--dataset_source",
            "SPX_CORE_V1",
            "--adapter_name",
            "stl_make_d_from_spx_drawdown_v1_0",
            "--proposition",
            "SPX_DRAWDOWN_T5",
            "--naive_rule",
            "drawdown_threshold",
            "--bool_mode",
            "le",
            "--threshold",
            "-0.2",
            "--event_on",
            "enter_true",
            "--W",
            LOCKED_PARAMS["W"],
            "--tau_s",
            LOCKED_PARAMS["tau_s"],
            "--tau_l",
            LOCKED_PARAMS["tau_l"],
            "--eps",
            LOCKED_PARAMS["eps"],
        ],
        env,
    )

    if not (out_case_dir / "summary.txt").exists():
        summary_write(out_case_dir / "summary.txt", ["CASE: SPX_DRAWDOWN_CORE", "OK"])

    write_manifest(adapter_dir)
    write_manifest(classify_dir)
    write_manifest(sad_dir)
    write_manifest(out_case_dir)


def run_caseset(caseset: str, replay_dir: Path, env):
    cases = CORE_CASES if caseset == "core" else FULL_CASES

    for c in cases:
        out_case_dir = replay_dir / c
        if c == "NEGCTL_SWEEP":
            do_negctl_sweep(out_case_dir, env)
        elif c == "OPERATOR_PRESERVATION":
            do_operator_preservation(out_case_dir, env)
        elif c == "SPX_DRAWDOWN_CORE":
            do_spx_drawdown_core(out_case_dir, env)
        else:
            raise RuntimeError("unknown case: " + c)

    summary_write(replay_dir / "summary.txt", [f"CASESET: {caseset}", "OK: STL verification complete"])
    write_manifest(replay_dir)


def parse_args():
    ap = argparse.ArgumentParser(prog="stl_master_verify.py")
    ap.add_argument("--profile", required=True, choices=["public"])
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--verify_replay", action="store_true")
    ap.add_argument("--run_id", choices=["A", "B"], default="A")
    ap.add_argument("--cases", choices=["core", "full"], default="core")
    return ap.parse_args()


def main():
    try:
        args = parse_args()
    except SystemExit:
        return EXIT_ARGS

    env = build_env()

    out_dir = Path(args.out_dir).resolve()
    base_out = out_dir / "stl_verify_out"
    base_out.mkdir(parents=True, exist_ok=True)

    try:
        if args.verify_replay:
            replay_a = base_out / "REPLAY_A"
            replay_b = base_out / "REPLAY_B"
            ensure_clean_dir(replay_a)
            ensure_clean_dir(replay_b)

            run_caseset(args.cases, replay_a, env)
            run_caseset(args.cases, replay_b, env)

            ok = compare_dirs(replay_a, replay_b)

            sys.stdout.write("VERIFY_REPLAY: PASS\n" if ok else "VERIFY_REPLAY: FAIL\n")
            return EXIT_OK if ok else EXIT_FAIL

        replay_dir = base_out / ("REPLAY_A" if args.run_id == "A" else "REPLAY_B")
        ensure_clean_dir(replay_dir)
        run_caseset(args.cases, replay_dir, env)
        sys.stdout.write("OK: STL verification complete\n")
        return EXIT_OK

    except FileNotFoundError as e:
        sys.stderr.write(f"MISSING: {str(e)}\n")
        return EXIT_MISSING
    except RuntimeError as e:
        sys.stderr.write(f"FAIL: {str(e)}\n")
        return EXIT_FAIL
    except Exception as e:
        sys.stderr.write(f"INVARIANT: {repr(e)}\n")
        return EXIT_INVARIANT


if __name__ == "__main__":
    raise SystemExit(main())
