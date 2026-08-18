"""Build the single-file Mentar binary for THIS computer, and verify it.

Why this exists: PyInstaller does not cross-compile. It bundles the running
interpreter plus a platform-specific bootloader, so a Windows .exe must be built
on Windows, a macOS binary on macOS. `.github/workflows/build-binary.yml` does
this on three runners; when CI is unavailable (or you just want a build in front
of you), this script is the same recipe, runnable by hand.

It is deliberately NOT just "run pyinstaller": it applies the same two gates CI
does, because a binary that starts and then 404s a child's lesson is worse than
one that never shipped.

  1. --selftest        every bundled asset resolves (curriculum, templates)
  2. a real serve      it answers HTTP, prints the calm banner, and has NOT
                       fallen back to Flask's dev server

That last check is not theoretical. Built on a machine without `waitress`
installed, PyInstaller silently omits it and the packaged binary falls back to
Flask's development server -- which prints a bold red warning under Mentar's
banner that a parent cannot act on (found 2026-08-15, and hit AGAIN during a
local build 2026-08-18). The gate catches it; the install step below prevents it.

Usage, from the repo root:

    python scripts/build_binary.py            # build + verify
    python scripts/build_binary.py --skip-install    # deps already installed

Windows note: use a real Python 3.12 (python.org or the Store), not WSL --
a WSL build produces a LINUX binary that will not run on Windows.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "packaging" / "mentar.spec"
PORT = 5099

# What CI names each platform's artifact, so a hand build lands on the same name.
ARTIFACTS = {
    "Windows": ("dist/mentar.exe", "mentar-windows-x86_64.exe"),
    "Darwin": ("dist/mentar", "mentar-macos-arm64"),
    "Linux": ("dist/mentar", "mentar-linux-x86_64"),
}


def run(cmd: list[str], **kw) -> None:
    print(f"\n$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True, cwd=REPO, **kw)


def install_dependencies() -> None:
    """Exactly what the workflow installs. `waitress` (in the web extra) is the
    one whose absence fails silently rather than loudly -- see the module docstring."""
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "-e", ".[web,setup]"])
    run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def check_prerequisites() -> None:
    # noqa-worthy on purpose: ruff calls this dead because requires-python is
    # >=3.11, but this script is run BY HAND on a machine whose Python is
    # unknown (a fresh Windows install often has 3.9). A clear sentence beats
    # a confusing pip resolution error.
    if sys.version_info < (3, 11):  # noqa: UP036
        sys.exit(f"Python 3.11+ required (CI builds on 3.12); this is {sys.version.split()[0]}")
    try:
        import waitress  # noqa: F401
    except ImportError:
        sys.exit(
            "waitress is not installed, so PyInstaller would omit it and the binary "
            "would fall back to Flask's dev server.\n"
            '  Fix:  python -m pip install -e ".[web,setup]"   (or drop --skip-install)'
        )
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        sys.exit("pyinstaller is not installed.\n  Fix: python -m pip install pyinstaller")


def selftest(binary: Path) -> None:
    print("\n=== gate 1: --selftest (are all bundled assets present?) ===", flush=True)
    run([str(binary), "--selftest"])


def serve_check(binary: Path) -> None:
    """Start the built binary and prove it actually serves. Mirrors the workflow's
    'Start it and check it actually serves' step, including its two assertions."""
    print(f"\n=== gate 2: real server start on port {PORT} ===", flush=True)
    log_path = REPO / "serve.log"
    handle = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(binary), "serve", "--port", str(PORT)],
        stdout=handle, stderr=subprocess.STDOUT, text=True, cwd=REPO,
    )
    status = None
    try:
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                handle.flush()
                print(log_path.read_text(encoding="utf-8", errors="replace"))
                sys.exit(f"server exited early with code {proc.returncode}")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=2) as r:
                    status = r.status
                    break
            except urllib.error.HTTPError as e:
                status = e.code           # a 4xx/5xx still proves it is serving
                break
            except Exception:
                time.sleep(1)
        if status is None:
            sys.exit(f"server never answered on port {PORT}")
        print(f"served HTTP {status}")    # 302 is the expected first-run answer
        if status >= 500:
            sys.exit(f"server answered {status}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        handle.close()

    banner = log_path.read_text(encoding="utf-8", errors="replace")
    print("--- what a parent sees on startup ---")
    print(banner)
    if "development server" in banner:
        sys.exit(
            "FAILED: the packaged binary fell back to Flask's dev server -- waitress "
            "is missing from the bundle. Reinstall deps and rebuild."
        )
    if "Only THIS computer" not in banner:
        sys.exit("FAILED: the default-mode banner did not print")
    log_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skip-install", action="store_true",
                    help="dependencies are already installed")
    ap.add_argument("--skip-verify", action="store_true",
                    help="build only (NOT recommended -- the gates are the point)")
    args = ap.parse_args(argv)

    system = platform.system()
    if system not in ARTIFACTS:
        sys.exit(f"unsupported platform {system!r}")
    rel_binary, artifact_name = ARTIFACTS[system]
    print(f"Building Mentar for {system} ({platform.machine()}) with "
          f"Python {sys.version.split()[0]}")
    print("NOTE: this produces a binary for THIS operating system only -- "
          "PyInstaller cannot cross-compile.")

    if not args.skip_install:
        install_dependencies()
    check_prerequisites()

    run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", str(SPEC)])

    binary = REPO / rel_binary
    if not binary.exists():
        sys.exit(f"expected {binary} to exist after the build")

    if not args.skip_verify:
        selftest(binary)
        serve_check(binary)

    out_dir = REPO / "dist" / "binaries" / artifact_name
    out_dir.mkdir(parents=True, exist_ok=True)
    destination = out_dir / artifact_name
    shutil.copy2(binary, destination)

    size_mb = destination.stat().st_size / (1024 * 1024)
    print(f"\nOK -- {destination.relative_to(REPO)}  ({size_mb:.1f} MB)")
    if args.skip_verify:
        print("WARNING: built WITHOUT the selftest/serve gates (--skip-verify).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
