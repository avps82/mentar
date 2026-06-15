#!/usr/bin/env python3
"""Download pilot ZIM files for Mentar grounding (W7.4).

Pulls the pilot sources from a Kiwix mirror to a destination that may be **local,
a mounted NAS, or an SMB/Samba share** (``smb://`` URL / UNC):

    # local or mounted-NAS dir (just a path the OS can write to):
    python3 scripts/fetch_pilot_zims.py --dest /mnt/nas/zims

    # SMB share directly (needs: pip install 'mentar[nas]'):
    python3 scripts/fetch_pilot_zims.py --dest smb://nas/share/zims \
        --smb-user me --smb-pass 'secret'

    # pick a specific mirror / a single source:
    python3 scripts/fetch_pilot_zims.py --mirror https://lbo.download.kiwix.org/zim \
        --only vikidia

Mirrors are tried in order until one serves the file. ZIM files are GITIGNORED
(`*.zim`); never commit them.

FUTURE GOAL (not built yet): discover available ZIMs/versions automatically from
the Kiwix OPDS catalog/library so filenames need not be pinned by hand, and target
any reasonable destination on any OS. For now filenames are pinned below and the
destination supports local / mounted-NAS / SMB.

Spec: docs/design/W7_grounding_reader.md (ZIM acquisition / W7.4).
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import urllib.request
from typing import Optional

# ── Mirrors (tried in order). download.kiwix.org redirects to a mirror; the rest
# are direct mirrors. Verify/extend for your region — this is the "global" knob. ──
DEFAULT_MIRRORS = [
    "https://download.kiwix.org/zim",
    "https://master.download.kiwix.org/zim",
    "https://lbo.download.kiwix.org/zim",
    "https://mirror.accum.se/mirror/kiwix.org/zim",
    "https://ftp.fau.de/kiwix/zim",
]

# ── Pilot sources: relative path on the mirror → local destination filename
# (what config/inference.example.yaml's grounding.sources expects).
# Update the version date after a new Kiwix release (browse <mirror>/<project>/). ──
SOURCES = {
    "vikidia": {
        "remote": "vikidia/vikidia_en_all_nopic_2024-09.zim",
        "dest": "vikidia_en_all_nopic.zim",
        "approx": "~200 MB",
    },
    "wikipedia_simple": {
        "remote": "wikipedia/wikipedia_en_simple_all_nopic_2024-09.zim",
        "dest": "wikipedia_en_simple_all.zim",
        "approx": "~900 MB",
    },
}

_CHUNK = 8 * 1024 * 1024  # 8 MiB


def _log(msg: str) -> None:
    print(f"[fetch-zims] {msg}", flush=True)


def _is_smb(dest: str) -> bool:
    s = dest.strip()
    return s.startswith("smb://") or s.startswith("\\\\") or s.startswith("//")


def _http_open(mirrors: list[str], remote: str):
    """Return an open HTTP response for the first mirror that serves ``remote``."""
    last_err: Optional[Exception] = None
    for base in mirrors:
        url = base.rstrip("/") + "/" + remote
        try:
            _log(f"trying {url}")
            return urllib.request.urlopen(url, timeout=60), url  # noqa: S310 (trusted mirrors)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            _log(f"  mirror failed: {exc}")
    raise RuntimeError(f"all mirrors failed for {remote}: {last_err}")


def _write_local(resp, dest_dir: str, filename: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    final = os.path.join(dest_dir, filename)
    if os.path.exists(final):
        _log(f"{filename} already present at {final} — skipping.")
        return final
    tmp = final + ".tmp"
    with open(tmp, "wb") as out:
        _copy(resp, out)
    os.replace(tmp, final)
    return final


def _write_smb(resp, dest_dir: str, filename: str, smb_user, smb_pass, smb_domain) -> str:
    try:
        import smbclient
        from mentar.grounding.sources import join_location, smb_url_to_unc
    except ImportError as exc:
        raise RuntimeError(
            "SMB destination needs the [nas] extra and the mentar package on PYTHONPATH: "
            "pip install 'mentar[nas]'"
        ) from exc
    if smb_user:
        user = f"{smb_domain}\\{smb_user}" if smb_domain else smb_user
        smbclient.ClientConfig(username=user, password=smb_pass)
    unc = smb_url_to_unc(join_location(dest_dir, filename))
    _log(f"writing to SMB: {unc}")
    with smbclient.open_file(unc, mode="wb") as out:
        _copy(resp, out)
    return unc


def _copy(resp, out) -> None:
    total = 0
    while True:
        chunk = resp.read(_CHUNK)
        if not chunk:
            break
        out.write(chunk)
        total += len(chunk)
        _log(f"  ... {total / (1024 * 1024):.0f} MB")


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Download pilot ZIMs to local / NAS / SMB.")
    ap.add_argument("--dest", default=os.environ.get("MENTAR_ZIM_DIR", "./zims"),
                    help="Destination dir: local path, mounted-NAS path, or smb:// URL / UNC.")
    ap.add_argument("--mirror", action="append", default=None,
                    help="Mirror base URL (repeatable). Defaults to the built-in list.")
    ap.add_argument("--only", choices=sorted(SOURCES), default=None,
                    help="Fetch only this source (default: all).")
    ap.add_argument("--smb-user", default=os.environ.get("MENTAR_SMB_USER"))
    ap.add_argument("--smb-pass", default=os.environ.get("MENTAR_SMB_PASSWORD"))
    ap.add_argument("--smb-domain", default=os.environ.get("MENTAR_SMB_DOMAIN", ""))
    args = ap.parse_args(argv)

    mirrors = args.mirror or DEFAULT_MIRRORS
    names = [args.only] if args.only else list(SOURCES)
    smb = _is_smb(args.dest)

    # Make `mentar.grounding.sources` importable for the SMB path helpers.
    if smb:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

    _log(f"dest={args.dest}  smb={smb}  sources={names}")
    failures = 0
    for name in names:
        spec = SOURCES[name]
        _log(f"== {name} ({spec['approx']}) ==")
        try:
            resp, url = _http_open(mirrors, spec["remote"])
            with resp:
                if smb:
                    final = _write_smb(resp, args.dest, spec["dest"],
                                       args.smb_user, args.smb_pass, args.smb_domain)
                else:
                    final = _write_local(resp, args.dest, spec["dest"])
            _log(f"OK: {name} → {final}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            _log(f"FAILED: {name}: {exc}")

    if failures:
        _log(f"done with {failures} failure(s).")
        return 1
    _log("done. Set grounding.zim_dir to your dest in config/inference.yaml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
