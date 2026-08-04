#!/usr/bin/env python3
"""Gera .github/assets/palette.svg a partir do colors.toml."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".github" / "assets" / "palette.svg"

BG = "#1c1c1c"
FG = "#abb2bf"
MUTED = "#6c7380"
STROKE = "#3d444d"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"

W, PAD, GAP = 880, 28, 12


def load_colors():
    text = (ROOT / "colors.toml").read_text()
    values = dict(re.findall(r'^(\w+)\s*=\s*"(#[0-9a-fA-F]{6})"', text, re.M))
    missing = [k for k in ("background", "foreground", "accent",
                           "selection_background") if k not in values]
    missing += [f"color{i}" for i in range(16) if f"color{i}" not in values]
    if missing:
        sys.exit(f"colors.toml sem as chaves: {', '.join(missing)}")
    return values


def swatch(x, y, w, h, color, label, sub=None):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
           f'fill="{color}" stroke="{STROKE}" stroke-width="1"/>']
    ty = y + h + 18
    out.append(f'<text x="{x}" y="{ty}" font-family="{MONO}" font-size="12" '
               f'fill="{FG}">{label}</text>')
    if sub:
        out.append(f'<text x="{x}" y="{ty + 16}" font-family="{MONO}" '
                   f'font-size="11" fill="{MUTED}">{sub}</text>')
    return out


def row_label(x, y, text):
    return (f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="11" '
            f'fill="{MUTED}" letter-spacing="1.2">{text}</text>')


def main():
    c = load_colors()
    core = [("Background", c["background"]), ("Foreground", c["foreground"]),
            ("Accent", c["accent"]), ("Selection", c["selection_background"])]
    normal = [c[f"color{i}"] for i in range(8)]
    bright = [c[f"color{i}"] for i in range(8, 16)]

    parts, y = [], PAD

    parts.append(row_label(PAD, y + 10, "CORE"))
    y += 26
    core_w = (W - 2 * PAD - 3 * GAP) // 4
    for i, (name, hexv) in enumerate(core):
        parts += swatch(PAD + i * (core_w + GAP), y, core_w, 56, hexv, name, hexv)
    y += 56 + 58

    cell_w = (W - 2 * PAD - 7 * GAP) // 8
    for title, row in (("NORMAL", normal), ("BRIGHT", bright)):
        parts.append(row_label(PAD, y + 10, title))
        y += 26
        for i, hexv in enumerate(row):
            parts += swatch(PAD + i * (cell_w + GAP), y, cell_w, 44, hexv, hexv)
        y += 44 + 34

    h = y + PAD - 22
    svg = "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
        f'viewBox="0 0 {W} {h}" role="img" aria-label="Noctua color palette">',
        f'<rect width="{W}" height="{h}" rx="10" fill="{BG}"/>',
        *parts, "</svg>",
    ])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"{OUT.relative_to(ROOT)} {W}x{h} {len(svg)} bytes")


if __name__ == "__main__":
    main()
