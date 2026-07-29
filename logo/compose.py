"""Build the double-M monogram from two offset geometric glyphs.

The logo is recoloured to the active theme's accent and written to the CV and
website asset directories.

  python logo/compose.py                 # regenerate for the active theme
  python logo/compose.py --gap 0.08      # upward offset (fraction of height)
  python logo/compose.py --opacity 1.0   # render both M glyphs at full strength
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import cairosvg
except Exception:  # missing cairosvg or a broken native cairo library
    cairosvg = None

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = ROOT / "logo" / "original.svg"
GAP = 0.0       # upward shift of the back M, as a fraction of glyph height
OPACITY = 0.28  # quieter offset M behind the primary glyph


def _glyphs() -> list[str]:
    """Return the two M path elements from the source artwork."""
    return re.findall(r"<path.*?/>", ORIGINAL.read_text(), re.DOTALL)


def build(color: str, gap: float = GAP, opacity: float = OPACITY) -> str:
    back, front = _glyphs()
    shift = -gap * 720  # original glyph box is 720 tall; SVG y grows downward
    back = back.replace('fill="#B8860B"', f'fill="{color}" fill-opacity="{opacity}"')
    front = front.replace('fill="#B8860B"', f'fill="{color}"')
    pad = 8
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{-15-pad} {shift-pad} {690+2*pad} {720-shift+2*pad}">'
        f'<g transform="translate(-15 0)">'
        f'<g transform="translate(0 {shift:.1f})">{back}</g>'
        f"{front}</g></svg>"
    )


def generate_for_theme(gap: float = GAP, opacity: float = OPACITY) -> list[Path]:
    sys.path.insert(0, str(ROOT))
    from src.theme import load_theme

    color = "#" + load_theme()["colors"]["gold"]
    svg = build(color, gap, opacity)
    targets = [
        ROOT / "cv" / "assets" / "logo-gold.svg",
        ROOT / "website" / "public" / "logo-gold.svg",
    ]
    for t in targets:
        t.write_text(svg)
    if cairosvg is not None:
        cairosvg.svg2pdf(url=str(targets[0]), write_to=str(ROOT / "cv" / "assets" / "logo-gold.pdf"))
    else:
        print("warning: cairo unavailable — logo-gold.pdf not regenerated (SVGs updated)")
    return targets


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=float, default=GAP)
    ap.add_argument("--opacity", type=float, default=OPACITY)
    ap.add_argument("--png", action="store_true")
    args = ap.parse_args()
    for t in generate_for_theme(args.gap, args.opacity):
        print(f"wrote {t.relative_to(ROOT)}")
    if args.png:
        cairosvg.svg2png(url=str(ROOT / "cv/assets/logo-gold.svg"),
                         write_to="/tmp/logo/preview.png", output_width=400,
                         background_color="white")
        print("wrote /tmp/logo/preview.png")


if __name__ == "__main__":
    main()
