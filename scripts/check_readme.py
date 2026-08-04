#!/usr/bin/env python3
"""Valida a integridade do README do tema.

Duas checagens:
1. Todo caminho relativo referenciado no README existe no repo.
2. Todo arquivo de tema versionado aparece citado no README.

Sai com 0 se tudo passa, 1 caso contrário.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

# Arquivos versionados que nao precisam ser citados no README.
NOT_THEME_FILES = {
    "README.md",
    "AGENTS.md",
    ".gitignore",
    "preview.png",
}
# Prefixos de diretorio que nao contem arquivos de tema.
NOT_THEME_DIRS = ("docs/", "scripts/", ".github/", "backgrounds/")


def tracked_files():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line]


def referenced_paths(text):
    """Caminhos relativos em markdown ![](p) / [](p) e em <img src="p">."""
    paths = set()
    for m in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        paths.add(m.group(1).strip())
    for m in re.finditer(r'<img[^>]+src="([^"]+)"', text):
        paths.add(m.group(1).strip())
    return {
        p for p in paths
        if not p.startswith(("http://", "https://", "#", "mailto:"))
    }


def main():
    text = README.read_text()
    errors = []

    # --- 1. caminhos referenciados existem ---
    for path in sorted(referenced_paths(text)):
        if not (ROOT / path).exists():
            errors.append(f"caminho inexistente no README: {path}")

    # --- 2. arquivos de tema estao citados ---
    for rel in tracked_files():
        if rel in NOT_THEME_FILES or rel.startswith(NOT_THEME_DIRS):
            continue
        name = Path(rel).name
        top = rel.split("/")[0]
        # Aceita citacao do arquivo ou do diretorio que o contem.
        cited = name in text or (top != rel and f"{top}/" in text)
        if not cited:
            errors.append(f"arquivo de tema nao citado no README: {rel}")

    if errors:
        print(f"FALHOU — {len(errors)} problema(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print("OK — README integro")
    return 0


if __name__ == "__main__":
    sys.exit(main())
