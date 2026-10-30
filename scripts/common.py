import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
RESULTS = ROOT / "results"
PQ = ROOT / "third_party/pqclean/crypto_kem/ml-kem-512/clean"
COMMON = ROOT / "third_party/pqclean/common"
FLAGS = ["-std=c99", "-O2", "-Wall", "-Wextra", "-Werror", "-fno-lto"]


def save(name, data):
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run(cmd, **kw):
    return subprocess.run([str(x) for x in cmd], cwd=ROOT, check=True, **kw)


def verify_sources():
    manifest = json.loads((ROOT / "upstream-lock.json").read_text())
    for name, item in manifest["files"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != item["sha256"]:
            raise RuntimeError(f"Upstream hash mismatch: {name}")
    return manifest["sources"]


def compile_c(name, sources, includes=(), flags=(), libs=()):
    BUILD.mkdir(exist_ok=True)
    cc = os.environ.get("CC", "gcc")
    if not shutil.which(cc):
        raise RuntimeError(f"BLOCKED: C compiler {cc} unavailable")
    extension = (".dll" if os.name == "nt" else ".so") if "-shared" in flags else (".exe" if os.name == "nt" else "")
    output = BUILD / (name + extension)
    cmd = [cc, *FLAGS, *flags, *["-I" + str(x) for x in includes],
           *[str(x) for x in sources], "-o", str(output), *libs]
    run(cmd, capture_output=True)
    (BUILD / (name + "-build.json")).write_text(json.dumps(cmd, indent=2))
    return output


def kernel_sources():
    return [ROOT / "src" / n for n in ["baseline.c", "masked.c", "kernel.c"]]


def build_mlkem(flags=(), suffix=""):
    verify_sources()
    libs = ["-lbcrypt"] if os.name == "nt" else []
    return compile_c("mlkem" + suffix, [ROOT / "tests/mlkem_driver.c",
        *sorted(PQ.glob("*.c")), COMMON / "fips202.c", COMMON / "randombytes.c"],
        [PQ, COMMON], flags, libs)
