"""Smoke test — confirms the package imports and version is set."""

import mentar


def test_version_is_set():
    assert mentar.__version__
    assert mentar.__version__.startswith("0.")
