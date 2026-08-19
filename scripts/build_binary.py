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

Network drives (found 2026-08-19 on a real mapped drive): BUILDING on a share
works, but RUNNING the result from one does not -- Windows denies CreateProcess
for an executable on a UNC path ("[WinError 5] Access is denied"), and
Path.resolve() silently rewrites a mapped drive letter into its
server/share form, so even a drive-letter invocation ends up UNC. Both verification gates
therefore run the binary from a LOCAL temp copy, which is also how a parent will
actually run it.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
import tempfile
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


def run(cmd: list[str], cwd: Path | None = None, **kw) -> None:
    print(f"\n$ {' '.join(cmd)}", flush=True)
    subprocess.run(cmd, check=True, cwd=cwd or REPO, **kw)


def install_dependencies() -> None:
    """Exactly what the workflow installs. `waitress` (in the web extra) is the
    one whose absence fails silently rather than loudly -- see the module docstring."""
    run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "-e", ".[web,setup]"])
    run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def check_prerequisites() -> None:
    # Deliberately kept: ruff calls this dead because requires-python is
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


def selftest(binary: Path, workdir: Path) -> None:
    print("\n=== gate 1: --selftest (are all bundled assets present?) ===", flush=True)
    run([str(binary), "--selftest"], cwd=workdir)


def _stop(proc: subprocess.Popen) -> None:
    """Stop the server AND its children.

    A PyInstaller one-file binary is two processes: the bootloader that unpacks
    the bundle, and the real app it spawns. Popen.terminate() only ends the
    bootloader, so on Windows the app kept serving and kept a LOCK on the .exe
    -- which is what made the temp-dir cleanup fail, and left a server running
    after the script had exited (maintainer, 2026-08-19). taskkill /T ends the
    tree. POSIX terminate() already reaped the child here, but the same
    belt-and-braces wait applies.
    """
    if sys.platform.startswith("win"):
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True, check=False,
        )
    else:
        proc.terminate()
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print("WARNING: the test server did not exit; check for a stray process",
                  file=sys.stderr)


def serve_check(binary: Path, workdir: Path) -> None:
    """Start the built binary and prove it actually serves. Mirrors the workflow's
    'Start it and check it actually serves' step, including its two assertions."""
    print(f"\n=== gate 2: real server start on port {PORT} ===", flush=True)
    log_path = workdir / "serve.log"
    handle = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [str(binary), "serve", "--port", str(PORT)],
        stdout=handle, stderr=subprocess.STDOUT, text=True, cwd=str(workdir),
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
        _stop(proc)
        handle.close()
        # Give the OS a moment to release the executable before anything tries
        # to delete it (Windows holds the lock briefly past process exit).
        time.sleep(1.5)

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


def verify(binary: Path) -> None:
    """Run both gates against a LOCAL copy of the binary.

    Never run the artifact in place: on Windows a repo on a mapped/UNC drive
    cannot be executed at all ("[WinError 5] Access is denied"), and even the
    working directory must be local -- Windows has no real notion of a UNC
    current directory. Copying first is not a workaround for a corner case; it
    is closer to the thing being tested, since a parent runs the binary from
    their own disk.
    """
    # mkdtemp + an EXPLICIT ignore_errors cleanup, not TemporaryDirectory: on
    # Windows a PyInstaller one-file binary runs a CHILD process that outlives
    # terminate() by a moment and keeps a lock on the .exe, so removing the
    # directory raises WinError 5 -- AFTER both gates have already passed
    # (maintainer, 2026-08-19). A stray file in %TEMP% must never fail a
    # verified build; the OS clears it later. shutil.rmtree(ignore_errors=True)
    # says that in one unambiguous flag rather than relying on the context
    # manager's cleanup semantics.
    workdir = Path(tempfile.mkdtemp(prefix="mentar-verify-"))
    try:
        local = workdir / binary.name
        shutil.copy2(binary, local)
        if not sys.platform.startswith("win"):
            local.chmod(0o755)
        print(f"verifying a local copy at {local} "
              f"(the repo may be on a network drive, which cannot execute)")
        try:
            selftest(local, workdir)
            serve_check(local, workdir)
        except PermissionError as exc:
            sys.exit(
                f"could not execute the built binary even from a local temp dir: {exc}\n"
                "  Antivirus or an execution policy is likely blocking it."
            )
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def publish(binary: Path, artifact_name: str) -> Path | None:
    """File the verified binary under dist/binaries/ using CI's artifact name.

    BEST EFFORT, deliberately: this runs AFTER both gates have passed, so the
    build is already good and a filing problem must not throw that away. On a
    network share the destination can be owned by another user (a previously
    downloaded CI artifact, root-owned over SMB), and the copy fails with
    "Permission denied" -- which is exactly how a green build ended in a
    traceback (maintainer, 2026-08-19). An existing file is cleared first where
    permissions allow; if the copy still fails, say where the binary IS and
    carry on.
    """
    out_dir = REPO / "dist" / "binaries" / artifact_name
    destination = out_dir / artifact_name
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            try:
                destination.chmod(0o666)      # a read-only leftover blocks the write
            except OSError:
                pass
            destination.unlink()
        shutil.copy2(binary, destination)
        return destination
    except OSError as exc:
        print(f"\nNOTE: could not file a copy into {out_dir} ({exc.strerror or exc}).")
        print("      The build and BOTH gates passed -- the verified binary is at:")
        print(f"      {binary}")
        print("      Copy it from there; nothing needs rebuilding.")
        return None


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
        verify(binary)

    size_mb = binary.stat().st_size / (1024 * 1024)
    published = publish(binary, artifact_name)

    print(f"\nOK -- built and verified  ({size_mb:.1f} MB)")
    print(f"   {published if published else binary}")
    if args.skip_verify:
        print("WARNING: built WITHOUT the selftest/serve gates (--skip-verify).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
