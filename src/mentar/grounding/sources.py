r"""ZIM source-location handling: local paths, mounted NAS, and SMB/Samba shares.

A ZIM lives somewhere; ``libzim`` can only open a **local filesystem path** (it
mmaps the file for random access). This module turns a configured *location* into
a local path the reader can open:

    materialize_zim(location, cfg) -> Path | None

Supported location forms:
  - **Local path**            ``/data/zims/vikidia.zim`` — returned as-is.
  - **Mounted NAS / share**   ``/mnt/nas/zims/vikidia.zim`` or a Windows drive /
                              UNC that the OS has already mounted — also just a
                              filesystem path, returned as-is (NO copy: the whole
                              point of NAS storage is to avoid a local copy).
  - **SMB URL / UNC**         ``smb://nas/share/vikidia.zim`` /
                              ``\\nas\share\vikidia.zim`` / ``//nas/share/...`` —
                              not a real local file, so it is **copied once** to a
                              local cache dir (``grounding.zim_cache_dir``) via
                              ``smbclient`` (optional dep ``smbprotocol``), then the
                              cached path is returned.

NOW (W7.4): local + mounted-NAS + SMB read/download.
FUTURE GOAL: pull from global Kiwix mirrors to any reasonable destination on any
OS (see ``scripts/fetch_zim.py``). Catalog/mirror discovery is not built yet.

Degradation contract (SAFETY §1.5 / SPEC §15): every failure returns ``None`` and
logs a warning — this module NEVER raises. ``smbprotocol`` is optional; if an SMB
location is requested without it installed, we warn and return ``None``.

Spec: docs/design/W7_grounding_reader.md (ZIM acquisition / SMB read row).
"""

from __future__ import annotations

import logging
import os
import re
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_COPY_CHUNK = 8 * 1024 * 1024  # 8 MiB streaming chunk for SMB → local copies
_DEFAULT_ZIM_CACHE = ".cache/zim"
_DATE_RE = r"\d{4}-\d{2}"  # Kiwix embeds a YYYY-MM build date in the filename


# ── Location classification & joining ─────────────────────────────────────────


def is_smb_location(location: str) -> bool:
    """True if ``location`` is an SMB URL or UNC path (not a plain/mounted path).

    Recognises ``smb://host/share/...``, ``\\\\host\\share\\...`` and
    ``//host/share/...``. A path that the OS has already *mounted* (e.g.
    ``/mnt/nas/...`` or ``Z:\\...``) is NOT an SMB location — it is a normal
    filesystem path and needs no SMB client.
    """
    s = str(location).strip()
    return s.startswith("smb://") or s.startswith("\\\\") or s.startswith("//")


def smb_url_to_unc(location: str) -> str:
    """Normalise an SMB location to a UNC path (``\\\\host\\share\\...``).

    ``smbclient`` expects UNC. ``smb://nas/share/f.zim`` and ``//nas/share/f.zim``
    both become ``\\\\nas\\share\\f.zim``; an already-UNC path is returned as-is.
    """
    s = str(location).strip()
    if s.startswith("smb://"):
        return "\\\\" + s[len("smb://"):].replace("/", "\\")
    if s.startswith("//"):
        return "\\\\" + s[2:].replace("/", "\\")
    return s  # already \\host\share\...


def join_location(base: str, filename: str) -> str:
    """Join ``filename`` onto a ZIM directory ``base`` (SMB-aware).

    For local/mounted bases this is an ordinary path join. For SMB bases the
    scheme/separator style is preserved (``smb://`` and ``//`` join with ``/``;
    a backslash UNC joins with ``\\``).
    """
    b = str(base)
    if is_smb_location(b):
        if b.startswith("\\\\"):
            return b.rstrip("\\/") + "\\" + filename
        return b.rstrip("/") + "/" + filename
    return str(Path(b).expanduser() / filename)


# ── Filename grammar: <project>_<lang>_<selection>_<flavour>_<YYYY-MM>.zim ─────
# Kiwix names embed project, language, selection (subject/"all"), flavour
# (maxi|nopic|mini) and a YYYY-MM build date — e.g. wikipedia_en_astronomy_maxi_2026-02.zim
# or wikipedia_ace_all_nopic_2026-04.zim. A source is declared by those parts in
# config; the NEWEST matching file is used automatically (latest wins) unless pinned.


def parse_index(html: str) -> list[str]:
    """Return the .zim filenames linked in a Kiwix directory-index HTML page."""
    return re.findall(r'href="([^"?/]+\.zim)"', html)


def pick_latest(filenames: list[str], regex: str) -> Optional[str]:
    """Pick the newest filename matching ``regex`` (YYYY-MM sorts lexicographically)."""
    rx = re.compile(regex)
    cands = sorted(f for f in filenames if rx.search(f))
    return cands[-1] if cands else None


def build_filename_regex(spec: dict) -> str:
    """Build an anchored filename regex from a structured source spec.

    spec keys: ``project`` (req), ``lang`` (req), ``selection`` (opt, e.g. "all" /
    "astronomy" / "simple_all"), ``flavour`` (opt, e.g. "maxi" / "nopic"),
    ``pin`` (opt: a ``YYYY-MM`` date to fix the build; a full ``*.zim`` pin is
    handled earlier in :func:`resolve_filename`).
    """
    parts = [re.escape(str(spec["project"])), re.escape(str(spec["lang"]))]
    if spec.get("selection"):
        parts.append(re.escape(str(spec["selection"])))
    if spec.get("flavour"):
        parts.append(re.escape(str(spec["flavour"])))
    body = "_".join(parts)
    pin = spec.get("pin")
    date = re.escape(str(pin)) if (pin and re.fullmatch(_DATE_RE, str(pin))) else _DATE_RE
    return rf"^{body}_{date}\.zim$"


def list_zim_dir(zim_dir: str, cfg: dict) -> list[str]:
    """List ``*.zim`` filenames in a local/mounted dir or an SMB dir. ``[]`` on failure."""
    try:
        if is_smb_location(zim_dir):
            try:
                import smbclient
            except ImportError:
                logger.warning("list_zim_dir: SMB dir %r needs the [nas] extra (smbprotocol)", zim_dir)
                return []
            _configure_smb_auth(cfg)
            return [f for f in smbclient.listdir(smb_url_to_unc(zim_dir)) if f.endswith(".zim")]
        d = Path(zim_dir).expanduser()
        if not d.is_dir():
            return []
        return [f.name for f in d.iterdir() if f.suffix == ".zim"]
    except Exception:
        logger.warning("list_zim_dir: cannot list %r — returning []", zim_dir, exc_info=True)
        return []


def resolve_filename(spec, zim_dir: str, cfg: dict) -> Optional[str]:
    """Resolve a source spec to a concrete ZIM filename present in ``zim_dir``.

    ``spec`` may be:
      - **str** — an exact filename (legacy / manual). Returned as-is.
      - **dict** — ``{project, lang, selection?, flavour?, pin?}``. The newest file
        in ``zim_dir`` matching the grammar is chosen (latest ``YYYY-MM`` wins); a
        ``pin`` of a full ``*.zim`` name or a ``YYYY-MM`` date overrides "latest".

    Returns ``None`` if nothing matches (caller applies the degradation contract).
    """
    if isinstance(spec, str):
        return spec or None
    if not isinstance(spec, dict):
        return None
    pin = spec.get("pin")
    if pin and str(pin).endswith(".zim"):
        return str(pin)  # explicit file pin — no listing needed
    regex = build_filename_regex(spec)
    latest = pick_latest(list_zim_dir(zim_dir, cfg), regex)
    if latest is None:
        logger.warning("resolve_filename: no ZIM in %r matches %s (spec=%r)", zim_dir, regex, spec)
    return latest


# ── Materialization ───────────────────────────────────────────────────────────


def materialize_zim(location: str, cfg: dict) -> Optional[Path]:
    """Return a local filesystem path libzim can open, or ``None`` on failure.

    Local / mounted paths are returned as-is (no copy). SMB locations are copied
    once to ``grounding.zim_cache_dir`` and the cached path returned. Never raises.
    """
    try:
        loc = str(location)
        if not is_smb_location(loc):
            p = Path(loc).expanduser()
            if not p.exists():
                logger.warning("materialize_zim: ZIM not found at local/mounted path: %s", p)
                return None
            return p
        return _materialize_smb(loc, cfg)
    except Exception:
        logger.warning("materialize_zim: unexpected error for %r — returning None", location, exc_info=True)
        return None


def _zim_cache_dir(cfg: dict) -> Path:
    raw = (cfg.get("zim_cache_dir") or _DEFAULT_ZIM_CACHE)
    return Path(os.path.expanduser(str(raw)))


def _configure_smb_auth(cfg: dict) -> None:
    """Apply SMB credentials from ``cfg['smb']`` to the global smbclient config.

    No-op when SMB is not enabled or no username is configured (anonymous /
    pre-registered sessions still work). Importing smbclient is the caller's job.
    """
    smb = cfg.get("smb") or {}
    if not smb.get("enabled"):
        return
    user = smb.get("username") or None
    pw = smb.get("password") or None
    domain = smb.get("domain") or None
    if user and domain and "\\" not in user and "@" not in user:
        user = f"{domain}\\{user}"
    if user or pw:
        import smbclient
        smbclient.ClientConfig(username=user, password=pw)


def _materialize_smb(location: str, cfg: dict) -> Optional[Path]:
    """Copy an SMB ZIM to the local cache and return the cached path, or None."""
    try:
        import smbclient
        from smbclient import open_file
    except ImportError:
        logger.warning(
            "materialize_zim: SMB location %r requested but 'smbprotocol' is not installed. "  # t7.3-exempt: operator log message, not a prompt
            "Install it with: pip install 'mentar[nas]'  (or mount the share and point "
            "grounding.zim_dir at the mount). Returning None.",
            location,
        )
        return None

    unc = smb_url_to_unc(location)
    _configure_smb_auth(cfg)

    cache_dir = _zim_cache_dir(cfg)
    cache_dir.mkdir(parents=True, exist_ok=True)
    local = cache_dir / Path(unc.replace("\\", "/")).name

    # Reuse a cached copy when its size matches the remote (cheap freshness check).
    remote_size: Optional[int] = None
    try:
        remote_size = smbclient.stat(unc).st_size
    except Exception:
        logger.warning("materialize_zim: cannot stat SMB path %s", unc, exc_info=True)
    if local.exists() and remote_size is not None and local.stat().st_size == remote_size:
        logger.debug("materialize_zim: reusing cached SMB copy %s", local)
        return local

    logger.info("materialize_zim: copying SMB ZIM %s → %s (this can be large)", unc, local)
    tmp = local.with_name(local.name + ".tmp")
    try:
        with open_file(unc, mode="rb") as src, open(tmp, "wb") as dst:
            shutil.copyfileobj(src, dst, length=_COPY_CHUNK)
        os.replace(tmp, local)
    except Exception:
        logger.warning("materialize_zim: failed copying SMB ZIM %s", unc, exc_info=True)
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass
        return None
    return local
