"""Theme contract gate — every named theme is COMPLETE, structural-token-free,
and legible, checked as arithmetic rather than by eye (2026-08-14).

Three failure classes this exists to make impossible:

1. **Silent token inheritance.** A theme block that omits a token does not
   error — it quietly inherits the light value and ships a half-theme (dark
   text on a dark background, say). Nothing in CSS, the browser, or a
   screenshot review reliably catches that; an exact-set assertion does.

2. **A theme changing layout.** `--radius`/`--font`/`--font-mono` are
   STRUCTURAL. If a theme could move or resize things, every future layout fix
   would need testing once per theme. Themes are colour and shadow only.

3. **Illegible colour pairs.** Contrast is arithmetic (WCAG 2.x relative
   luminance), so it belongs in the cheapest possible stage — here, not in a
   render review. Measured 2026-08-14, the shipped themes were failing this
   before the `--on-*` ink tokens were added: white-on-`--primary` in dark mode
   scored **1.94:1** on the primary action button of a maths tutor. Asked
   directly about that exact pair, a vision model replied "white on teal,
   providing strong contrast" — it identified the colours correctly and
   inverted the judgement. Never delegate contrast to a model or a squint.

The pairs below are derived from what the CSS ACTUALLY renders, not from what
a token's name suggests: `--primary` is a button background (label =
`--on-primary`), while `--primary-strong` is link/progress TEXT. An earlier
draft of this spec aimed the button rule at `--primary-strong`, checking a pair
the app never draws while missing the link pair it draws on every page.

    python3 tests/web/test_theme_tokens.py
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]
CSS = REPO / "src" / "mentar" / "web" / "static" / "style.css"

# Thematic tokens: every theme must define exactly these, no more, no fewer.
THEMATIC_TOKENS = {
    "--bg", "--surface", "--text", "--text-muted",
    "--primary", "--primary-strong", "--accent",
    "--on-primary", "--on-accent", "--on-danger",
    "--mastered", "--learning", "--not-started",
    "--danger", "--danger-bg", "--warn-bg", "--warn-border", "--border",
    "--shadow", "--shadow-hover",
}

# Structural tokens: defined once on :root, never themed.
STRUCTURAL_TOKENS = {"--radius", "--font", "--font-mono"}

# Shadows are composite values (offsets + rgba), not colour pairs — exempt from
# both the hex-only rule and the contrast maths.
SHADOW_TOKENS = {"--shadow", "--shadow-hover"}

# (foreground token, background token, minimum ratio, what the user sees)
CONTRAST_PAIRS = [
    ("--text", "--bg", 7.0, "body text on the page"),
    ("--text", "--surface", 7.0, "body text on cards"),
    ("--text-muted", "--surface", 4.5, "muted hints on cards"),
    ("--primary-strong", "--surface", 4.5, "links / progress text on cards"),
    ("--primary-strong", "--bg", 4.5, "links on the page"),
    ("--on-primary", "--primary", 3.0, ".btn label"),
    ("--on-accent", "--accent", 3.0, ".btn-accent label"),
    ("--on-danger", "--danger", 3.0, ".btn-danger label"),
]

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _relative_luminance(hex_colour: str) -> float:
    """WCAG 2.x relative luminance of a #RRGGBB colour (linearised sRGB)."""
    h = hex_colour.lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    r, g, b = linear
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    """WCAG contrast ratio, always >= 1.0 regardless of argument order."""
    lf, lb = _relative_luminance(fg), _relative_luminance(bg)
    lighter, darker = max(lf, lb), min(lf, lb)
    return (lighter + 0.05) / (darker + 0.05)


def _parse_blocks(css: str) -> dict[str, dict[str, str]]:
    """{theme_name: {token: value}} for :root (as "light") and every
    [data-theme="..."] rule. Deliberately a small regex parser, not a CSS
    engine: the hex-only rule below keeps the value grammar trivial enough
    that this stays honest."""
    blocks: dict[str, dict[str, str]] = {}
    for selector, body in re.findall(r"(:root|\[data-theme=\"[a-z-]+\"\])\s*\{([^}]*)\}", css):
        name = "light" if selector == ":root" else selector.split('"')[1]
        tokens = dict(re.findall(r"(--[a-z-]+)\s*:\s*([^;]+);", body))
        blocks[name] = {k: v.strip() for k, v in tokens.items()}
    return blocks


def _themes() -> dict[str, dict[str, str]]:
    return _parse_blocks(CSS.read_text(encoding="utf-8"))


def test_the_parser_actually_found_the_themes():
    """Guard the instrument before trusting any assertion built on it: a regex
    that silently matched nothing would make every test below vacuously pass."""
    themes = _themes()
    for expected in ("light", "dark", "ocean", "space", "forest", "sunshine"):
        assert expected in themes, f"{expected} theme block not found by the parser"
    assert len(themes["light"]) >= len(THEMATIC_TOKENS)


def test_every_theme_defines_exactly_the_thematic_tokens():
    for name, tokens in _themes().items():
        defined = set(tokens) - STRUCTURAL_TOKENS
        missing = THEMATIC_TOKENS - defined
        extra = defined - THEMATIC_TOKENS
        assert not missing, f"theme {name!r} is missing {sorted(missing)} (would silently inherit)"
        assert not extra, f"theme {name!r} defines unknown token(s) {sorted(extra)}"


def test_only_root_defines_structural_tokens():
    for name, tokens in _themes().items():
        present = STRUCTURAL_TOKENS & set(tokens)
        if name == "light":
            assert present == STRUCTURAL_TOKENS, "the :root block must define the structural tokens"
        else:
            assert not present, (
                f"theme {name!r} overrides structural token(s) {sorted(present)} — "
                "themes change colour and shadow only, never shape or typography"
            )


def test_colour_tokens_are_plain_six_digit_hex():
    for name, tokens in _themes().items():
        for token, value in tokens.items():
            if token in STRUCTURAL_TOKENS or token in SHADOW_TOKENS:
                continue
            assert _HEX_RE.match(value), (
                f"theme {name!r} token {token} is {value!r} — theme colours must be #RRGGBB "
                "(keeps the parser and the contrast maths trivially correct)"
            )


def test_every_theme_meets_its_contrast_floors():
    failures = []
    for name, tokens in _themes().items():
        for fg, bg, floor, what in CONTRAST_PAIRS:
            ratio = contrast_ratio(tokens[fg], tokens[bg])
            if ratio < floor:
                failures.append(
                    f"{name}: {fg} on {bg} = {ratio:.2f}:1 (need {floor}) — {what}"
                )
    assert not failures, "contrast failures:\n  " + "\n  ".join(failures)


def test_contrast_maths_matches_known_wcag_values():
    """Pin the formula itself against published reference ratios, so a broken
    luminance function can't quietly pass every theme."""
    assert round(contrast_ratio("#FFFFFF", "#000000"), 2) == 21.0
    assert round(contrast_ratio("#FFFFFF", "#FFFFFF"), 2) == 1.0
    assert round(contrast_ratio("#777777", "#FFFFFF"), 1) == 4.5  # the classic AA boundary grey
    # order must not matter
    assert contrast_ratio("#000000", "#FFFFFF") == contrast_ratio("#FFFFFF", "#000000")


if __name__ == "__main__":
    for fn_name, fn in sorted(globals().items()):
        if fn_name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {fn_name}")
