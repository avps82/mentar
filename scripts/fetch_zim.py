#!/usr/bin/env python3
"""Download ZIM files for Mentar (W7.4) — auto-resolves the LATEST version.

Replaces the version-pinned fetch_pilot_zims.py. Reads a Kiwix mirror's directory
index, picks the newest file matching a name pattern, and downloads it to a
destination that may be **local, a mounted NAS, or an SMB/Samba share** (smb:// / UNC).

    # pilot sources (default — vikidia + simple-wikipedia), to local/mounted dir:
    python3 scripts/fetch_zim.py --dest /mnt/nas/zims

    # a named preset (Khan Academy, PhET, …):
    python3 scripts/fetch_zim.py --preset khan-academy --dest smb://nas/share/zims \
        --smb-user me --smb-pass 'secret'

    # anything, by project subpath + filename regex (auto-picks newest):
    python3 scripts/fetch_zim.py --project gutenberg --match 'gutenberg_en_all_.*\\.zim$'

Mirrors are tried in order until one serves the index/file. ZIMs are GITIGNORED
(`*.zim`); never commit them.

NOTE on sources you might add:
  - Khan Academy ZIMs are **CC BY-NC-SA** — the NC clause blocks commercial/hosted
    redistribution (SPEC §24 #18 / docs/CONTENT_LICENSES.md). Local/personal use only.
  - PhET sims are **CC BY** (more permissive).
  - Project subpaths/filename patterns vary; if a preset misses, pass --project/--match.

FUTURE GOAL (not built): replace directory-index scraping with the Kiwix OPDS
catalog (library.kiwix.org) for richer/global discovery and metadata.

Spec: docs/design/W7_grounding_reader.md (ZIM acquisition / W7.4).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.request
from typing import Optional

DEFAULT_MIRRORS = [
    "https://download.kiwix.org/zim",
    "https://master.download.kiwix.org/zim",
    "https://lbo.download.kiwix.org/zim",
    "https://mirror.accum.se/mirror/kiwix.org/zim",
    "https://ftp.fau.de/kiwix/zim",
]

# preset → (project subpath on the mirror, filename regex, stable dest filename | None).
# dest=None keeps the resolved (versioned) filename. Verify project/match if a fetch misses.
PRESETS: dict[str, dict] = {
    "vikidia": {
        "project": "vikidia",
        "match": r"vikidia_en_all_nopic_.*\.zim$",
        "dest": "vikidia_en_all_nopic.zim",
    },
    "wikipedia_simple": {
        "project": "wikipedia",
        "match": r"wikipedia_en_simple_all_nopic_.*\.zim$",
        "dest": "wikipedia_en_simple_all.zim",
    },
    # CC BY-NC-SA — local/personal use only (see note above).
    "khan-academy": {"project": "other", "match": r"khan-academy_en_.*\.zim$", "dest": None},
    # CC BY — interactive HTML5 sims (would need W7.6 vetting to surface to a child).
    "phet": {"project": "phet", "match": r"phet_.*\.zim$", "dest": None},
}
DEFAULT_PRESETS = ["vikidia", "wikipedia_simple"]

_CHUNK = 8 * 1024 * 1024


def _log(msg: str) -> None:
    print(f"[fetch-zim] {msg}", flush=True)


# ── Pure helpers (unit-tested) ────────────────────────────────────────────────

def parse_index(html: str) -> list[str]:
    """Return the .zim filenames linked in a Kiwix directory-index HTML page."""
    return re.findall(r'href="([^"?/]+\.zim)"', html)


def pick_latest(filenames: list[str], match: str) -> Optional[str]:
    """Pick the newest filename matching ``match``.

    Kiwix filenames embed an ISO ``YYYY-MM`` date, which sorts correctly
    lexicographically, so the max matching name is the most recent build.
    """
    rx = re.compile(match)
    cands = sorted(f for f in filenames if rx.search(f))
    return cands[-1] if cands else None


# ── Network / IO ──────────────────────────────────────────────────────────────

def _is_smb(dest: str) -> bool:
    s = dest.strip()
    return s.startswith("smb://") or s.startswith("\\\\") or s.startswith("//")


def resolve_url(mirrors: list[str], project: str, match: str) -> tuple[str, str]:
    """Return (download_url, filename) for the newest matching ZIM on a mirror."""
    last = "no mirror served an index"
    for base in mirrors:
        idx = base.rstrip("/") + "/" + project + "/"
        try:
            with urllib.request.urlopen(idx, timeout=60) as r:  # noqa: S310
                html = r.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            last = f"{idx}: {exc}"
            _log(f"  index failed: {last}")
            continue
        latest = pick_latest(parse_index(html), match)
        if latest:
            return idx + latest, latest
        last = f"{idx}: no file matched {match!r}"
    raise RuntimeError(f"could not resolve a ZIM for project={project!r} match={match!r}: {last}")


def _copy(resp, out) -> None:
    total = 0
    while True:
        chunk = resp.read(_CHUNK)
        if not chunk:
            break
        out.write(chunk)
        total += len(chunk)
        _log(f"  ... {total / (1024 * 1024):.0f} MB")


def _write_local(resp, dest_dir: str, filename: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    final = os.path.join(dest_dir, filename)
    if os.path.exists(final):
        _log(f"{filename} already at {final} — skipping.")
        return final
    tmp = final + ".tmp"
    with open(tmp, "wb") as out:
        _copy(resp, out)
    os.replace(tmp, final)
    return final


def _write_smb(resp, dest_dir: str, filename: str, user, pw, domain) -> str:
    try:
        import smbclient
        from mentar.grounding.sources import join_location, smb_url_to_unc
    except ImportError as exc:
        raise RuntimeError("SMB dest needs: pip install 'mentar[nas]' (and src/ on PYTHONPATH)") from exc
    if user:
        smbclient.ClientConfig(username=(f"{domain}\\{user}" if domain else user), password=pw)
    unc = smb_url_to_unc(join_location(dest_dir, filename))
    _log(f"writing to SMB: {unc}")
    with smbclient.open_file(unc, mode="wb") as out:
        _copy(resp, out)
    return unc


def fetch_one(spec: dict, dest: str, mirrors: list[str], smb_args: dict) -> str:
    url, latest = resolve_url(mirrors, spec["project"], spec["match"])
    dest_name = spec.get("dest") or latest
    _log(f"resolved newest: {latest}  →  {url}")
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310
        if _is_smb(dest):
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
            return _write_smb(resp, dest, dest_name, smb_args["user"], smb_args["pass"], smb_args["domain"])
        return _write_local(resp, dest, dest_name)


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Download ZIMs (auto-latest) to local / NAS / SMB.")
    ap.add_argument("--dest", default=os.environ.get("MENTAR_ZIM_DIR", "./zims"),
                    help="Destination: local path, mounted-NAS path, or smb:// URL / UNC.")
    ap.add_argument("--preset", action="append", choices=sorted(PRESETS), default=None,
                    help=f"Named preset (repeatable). Default: {DEFAULT_PRESETS}.")
    ap.add_argument("--project", default=None, help="Mirror project subpath (e.g. 'gutenberg').")
    ap.add_argument("--match", default=None, help="Filename regex (newest match is chosen).")
    ap.add_argument("--dest-name", default=None, help="Override the saved filename.")
    ap.add_argument("--mirror", action="append", default=None, help="Mirror base URL (repeatable).")
    ap.add_argument("--smb-user", default=os.environ.get("MENTAR_SMB_USER"))
    ap.add_argument("--smb-pass", default=os.environ.get("MENTAR_SMB_PASSWORD"))
    ap.add_argument("--smb-domain", default=os.environ.get("MENTAR_SMB_DOMAIN", ""))
    args = ap.parse_args(argv)

    mirrors = args.mirror or DEFAULT_MIRRORS
    smb_args = {"user": args.smb_user, "pass": args.smb_pass, "domain": args.smb_domain}

    if args.project and args.match:
        jobs = [{"project": args.project, "match": args.match, "dest": args.dest_name}]
    else:
        jobs = [PRESETS[p] for p in (args.preset or DEFAULT_PRESETS)]

    _log(f"dest={args.dest}  smb={_is_smb(args.dest)}  jobs={len(jobs)}")
    failures = 0
    for spec in jobs:
        try:
            final = fetch_one(spec, args.dest, mirrors, smb_args)
            _log(f"OK → {final}")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            _log(f"FAILED ({spec.get('project')}/{spec.get('match')}): {exc}")

    if failures:
        _log(f"done with {failures} failure(s).")
        return 1
    _log("done. Point grounding.zim_dir at your dest in config/inference.yaml.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
