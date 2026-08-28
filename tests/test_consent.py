"""Parent cloud-consent record (SAFETY §4.5) — mentar.consent."""

import yaml

from mentar import consent as C


def test_roundtrip_and_default_absent(tmp_path):
    p = tmp_path / "cloud_consent.yaml"
    assert not C.has_cloud_consent("openai", path=p)
    C.record_cloud_consent("openai", path=p)
    assert C.has_cloud_consent("openai", path=p)
    assert not C.has_cloud_consent("claude", path=p), "consent is per-backend"


def test_record_preserves_other_backends(tmp_path):
    p = tmp_path / "cloud_consent.yaml"
    C.record_cloud_consent("openai", path=p)
    C.record_cloud_consent("claude", path=p)
    data = yaml.safe_load(p.read_text())
    assert set(data) == {"openai", "claude"}
    assert data["openai"]["provider"] == "OpenAI"
    assert data["claude"]["provider"] == "Anthropic"
    # UTC ISO timestamp, seconds precision
    assert data["openai"]["acknowledged_at"].endswith("+00:00")


def test_stale_statement_version_means_reconsent(tmp_path):
    """If the parent agreed to DIFFERENT wording, that agreement does not carry
    forward — setup must ask again, not silently reuse it."""
    p = tmp_path / "cloud_consent.yaml"
    C.record_cloud_consent("openai", path=p)
    data = yaml.safe_load(p.read_text())
    data["openai"]["statement_version"] = C.STATEMENT_VERSION - 1
    p.write_text(yaml.safe_dump(data))
    assert not C.has_cloud_consent("openai", path=p)


def test_corrupt_record_reads_as_no_consent(tmp_path):
    """The failure mode of a mangled file is the parent being ASKED AGAIN —
    never a silent cloud turn."""
    p = tmp_path / "cloud_consent.yaml"
    p.write_text("{{{{ not yaml")
    assert not C.has_cloud_consent("openai", path=p)
    # and recording over the corpse works
    C.record_cloud_consent("openai", path=p)
    assert C.has_cloud_consent("openai", path=p)


def test_every_malformed_shape_reads_as_no_consent(tmp_path):
    """This is called from make_llm_call AND the web setup gate, so a crash here
    500'd every page instead of routing the parent to /setup. A hand-written
    `backend: true` line did exactly that (AttributeError, 2026-08-29)."""
    p = tmp_path / "cloud_consent.yaml"
    for forged in ({"openai": True}, {"openai": "yes"}, {"openai": ["x"]},
                   {"openai": None}, {"openai": {"statement_version": "1"}},
                   {"openai": {"statement_version": 999}}, {"openai": {}}):
        p.write_text(yaml.safe_dump(forged))
        assert C.has_cloud_consent("openai", path=p) is False, forged
