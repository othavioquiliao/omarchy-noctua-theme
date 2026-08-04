# README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir e enriquecer o `README.md` do tema Noctua — wallpapers quebrados, preview placeholder, URL antiga e lista de arquivos incompleta — e reduzir o peso do repositório em 89%.

**Arquitetura:** O repo é config-only, sem build nem test runner. O ciclo red-green vem de um verificador próprio (`scripts/check_readme.py`) escrito na Task 1, que falha contra o README atual e só passa na Task 5. Os assets de documentação (paleta SVG e thumbnails) ficam em `.github/assets/`, fora da varredura de `backgrounds/` que o Omarchy faz. A paleta é gerada por script a partir do `colors.toml`, não desenhada à mão, para não virar asset órfão.

**Tech Stack:** Python 3 (stdlib apenas), ImageMagick 7 (`magick`), `grim` para captura Wayland, git.

## Global Constraints

- Spec de referência: `docs/superpowers/specs/2026-08-04-readme-noctua-design.md`.
- README permanece **em inglês**. Commits em português, Conventional Commits, subject ≤50 chars.
- **Nada de arquivo novo em `backgrounds/`** além de wallpapers. `omarchy-theme-bg-next` varre o diretório com `find -maxdepth 1` casando `jpg|jpeg|png|gif|bmp|webp`; qualquer outro arquivo vira wallpaper no ciclo do usuário.
- **Nenhum arquivo de tema é alterado** (cores, `hyprland.conf`, CSS dos apps). O escopo é documentação, assets e wallpapers.
- Toda imagem no README leva alt text descritivo. `![]()` sem alt é o motivo de a seção quebrada de hoje renderizar muda.
- URL canônica do repo: `https://github.com/othavi0/omarchy-noctua-theme`. O username `othavioquiliao` é antigo.
- Sem qualquer marca de autoria de IA em commits ou documentos.

## Estrutura de arquivos

| Caminho | Responsabilidade | Task |
|---|---|---|
| `scripts/check_readme.py` | Valida caminhos do README e cobertura da lista de arquivos | 1 |
| `scripts/gen_palette.py` | Gera o SVG da paleta a partir do `colors.toml` | 2 |
| `.github/assets/palette.svg` | Swatches renderizados no README | 2 |
| `backgrounds/0*-*.jpg` | Wallpapers recomprimidos e renomeados | 3 |
| `.github/assets/0*-*.jpg` | Thumbnails 16:9 da tabela de wallpapers | 4 |
| `README.md` | Documento reescrito | 5 |
| `preview.png` | Captura real do desktop | 6 |
| `AGENTS.md` | Convenções alinhadas ao repo real | 7 |

**Estado intermediário esperado:** entre as Tasks 3 e 5 o README fica temporariamente mais quebrado do que já está (os wallpapers mudam de nome antes de o README ser reescrito). É esperado e se resolve na Task 5. Não interromper o plano por causa disso.

---

### Task 1: Verificador do README

Cria o teste que define "README correto" e demonstra que o README atual falha.

**Files:**
- Create: `scripts/check_readme.py`

**Interfaces:**
- Consumes: nada.
- Produces: executável `python3 scripts/check_readme.py`, que sai com código 0 quando o README está íntegro e 1 quando não. Usado como gate nas Tasks 5, 6 e 7.

- [ ] **Step 1: Escrever o verificador**

Cria `scripts/check_readme.py`:

```python
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
```

- [ ] **Step 2: Rodar o verificador para confirmar que FALHA**

Run: `python3 scripts/check_readme.py`

Expected: FAIL, exit 1, com exatamente 9 problemas — os 8 wallpapers inexistentes (`backgrounds/00-noctua-grid.jpg`, `01-slate-rift.jpg`, `02-blue-current.jpg`, `03-violet-echo.jpg`, `04-cyan-terminal.jpg`, `05-golden-signal.jpg`, `06-red-shift.jpg`, `07-midnight-panel.jpg`) e `firefox.css` não citado.

Se o número não bater, parar e investigar antes de seguir — o verificador é a base de todo o resto do plano.

- [ ] **Step 3: Commit**

```bash
git add scripts/check_readme.py
git commit -m "test: verificador de integridade do README"
```

---

### Task 2: Gerador da paleta

**Files:**
- Create: `scripts/gen_palette.py`
- Create: `.github/assets/palette.svg`

**Interfaces:**
- Consumes: `colors.toml` (lido pelo script, não hardcoded no README).
- Produces: `.github/assets/palette.svg`, 880 px de largura, referenciado pelo README na Task 5.

- [ ] **Step 1: Escrever o gerador**

Cria `scripts/gen_palette.py`. Lê o `colors.toml` da raiz e escreve o SVG em `.github/assets/palette.svg`:

```python
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
```

- [ ] **Step 2: Gerar o SVG**

Run: `python3 scripts/gen_palette.py`
Expected: imprime `.github/assets/palette.svg 880x382` e cerca de 6400 bytes.

- [ ] **Step 3: Verificar que os 16 hex do colors.toml estão no SVG**

Run:
```bash
python3 - <<'PY'
import re, pathlib
toml = pathlib.Path("colors.toml").read_text()
svg = pathlib.Path(".github/assets/palette.svg").read_text()
want = {v for _, v in re.findall(r'^(\w+)\s*=\s*"(#[0-9a-fA-F]{6})"', toml, re.M)}
missing = sorted(h for h in want if h not in svg)
print("FALTANDO:", missing) if missing else print(f"OK — {len(want)} cores presentes")
PY
```
Expected: `OK — 12 cores presentes`. São 22 chaves no `colors.toml` mas só 12 valores distintos — `#abb2bf` aparece em quatro chaves, `#61afef` em três, e assim por diante. Número conferido rodando a contagem, não estimado.

- [ ] **Step 4: Conferir que o SVG rasteriza sem erro**

Run: `magick -background none .github/assets/palette.svg /tmp/palette-check.png && magick identify -format "%wx%h\n" /tmp/palette-check.png`
Expected: `880x382`, sem warnings de parse.

- [ ] **Step 5: Commit**

```bash
git add scripts/gen_palette.py .github/assets/palette.svg
git commit -m "feat: paleta em SVG gerada do colors.toml"
```

---

### Task 3: Recompressão e renomeação dos wallpapers

**Files:**
- Delete: `backgrounds/00-noctua.jpg`, `backgrounds/01-noctua.png`, `backgrounds/02-noctua.jpg`
- Create: `backgrounds/00-city-dusk.jpg`, `backgrounds/01-lunar-arc.jpg`, `backgrounds/02-alpine-ridge.jpg`

**Interfaces:**
- Consumes: os três wallpapers atuais.
- Produces: os três nomes novos, referenciados pelo README (Task 5) e origem dos thumbnails (Task 4).

- [ ] **Step 1: Registrar o tamanho de partida**

Run: `du -sb backgrounds/ | cut -f1`
Expected: cerca de `10800000` (10,8 MB). Anotar o valor exato para comparar no Step 4.

- [ ] **Step 2: Recomprimir e renomear**

Lado maior 2560 px, qualidade 88, metadados removidos, tudo em JPEG. O `.png` é uma fotografia — PNG só desperdiça bytes.

```bash
magick backgrounds/00-noctua.jpg  -resize 2560x2560\> -quality 88 -strip backgrounds/00-city-dusk.jpg
magick backgrounds/01-noctua.png  -resize 2560x2560\> -quality 88 -strip backgrounds/01-lunar-arc.jpg
magick backgrounds/02-noctua.jpg  -resize 2560x2560\> -quality 88 -strip backgrounds/02-alpine-ridge.jpg
git rm -q backgrounds/00-noctua.jpg backgrounds/01-noctua.png backgrounds/02-noctua.jpg
```

- [ ] **Step 3: Verificar dimensões e contagem**

Run: `magick identify -format "%f %wx%h %b\n" backgrounds/*`
Expected: exatamente três linhas —
```
00-city-dusk.jpg 2560x1440 ~466KB
01-lunar-arc.jpg 2560x1707 ~314KB
02-alpine-ridge.jpg 2560x1707 ~453KB
```
Nenhum arquivo `*-noctua.*` remanescente.

- [ ] **Step 4: Verificar a redução**

Run: `du -sb backgrounds/ | cut -f1`
Expected: cerca de `1230000` (1,23 MB), ~89% menor que o valor do Step 1. Se ficar acima de 2 MB, parar e conferir se algum original sobreviveu no diretório.

- [ ] **Step 5: Commit**

```bash
git add backgrounds/
git commit -m "perf: recomprimir e renomear wallpapers"
```

---

### Task 4: Thumbnails dos wallpapers

**Files:**
- Create: `.github/assets/00-city-dusk.jpg`, `.github/assets/01-lunar-arc.jpg`, `.github/assets/02-alpine-ridge.jpg`

**Interfaces:**
- Consumes: os wallpapers renomeados da Task 3.
- Produces: três thumbnails 800×450 referenciados pela tabela do README na Task 5.

- [ ] **Step 1: Gerar os thumbnails**

Crop 16:9 uniforme — os originais têm proporções diferentes (16:9 e 3:2) e desalinhariam as células da tabela.

```bash
for f in 00-city-dusk 01-lunar-arc 02-alpine-ridge; do
  magick "backgrounds/$f.jpg" -resize 800x -gravity center \
    -crop 800x450+0+0 +repage -quality 82 -strip ".github/assets/$f.jpg"
done
```

- [ ] **Step 2: Verificar dimensões**

Run: `magick identify -format "%f %wx%h %b\n" .github/assets/*.jpg`
Expected: três linhas, todas `800x450`, cada uma entre 20 KB e 45 KB.

- [ ] **Step 3: Conferir visualmente que os crops não decapitaram o assunto**

Run: `magick montage .github/assets/00-city-dusk.jpg .github/assets/01-lunar-arc.jpg .github/assets/02-alpine-ridge.jpg -tile 3x1 -geometry 420x+8+8 -background '#1c1c1c' /tmp/thumbs-check.jpg`

Abrir `/tmp/thumbs-check.jpg` e confirmar que skyline, lua e cordilheira continuam legíveis e centralizados. Se algum crop cortar mal, ajustar o `-gravity` daquele arquivo (`north` para o skyline, `center` para os demais) e repetir o Step 1.

- [ ] **Step 4: Commit**

```bash
git add .github/assets/
git commit -m "feat: thumbnails dos wallpapers p/ README"
```

---

### Task 5: Reescrita do README

Aqui o verificador da Task 1 vira verde.

**Files:**
- Modify: `README.md` (reescrita completa)

**Interfaces:**
- Consumes: `.github/assets/palette.svg` (Task 2), `backgrounds/0*-*.jpg` (Task 3), `.github/assets/0*-*.jpg` (Task 4).
- Produces: README íntegro; `scripts/check_readme.py` passa a sair 0.

- [ ] **Step 1: Confirmar que o verificador ainda falha**

Run: `python3 scripts/check_readme.py`
Expected: FAIL, exit 1, ainda com os mesmos **9 problemas** da Task 1 — os 8 caminhos de wallpaper antigos e `firefox.css`. A contagem não muda depois das Tasks 3 e 4 porque `backgrounds/` e `.github/` estão em `NOT_THEME_DIRS`, então os arquivos novos não entram na checagem de cobertura.

- [ ] **Step 2: Escrever o README**

Substitui o conteúdo inteiro de `README.md` por:

````markdown
# Omarchy Noctua Theme

Neutral One Dark Pro palette for Omarchy/Hyprland, built on a `#242424` base — matching terminal, shell, editor, and app themes plus three original wallpapers.

![Noctua theme running on Hyprland, with Waybar, editor and terminal](preview.png)

## Install

Use the Omarchy theme installer:

```bash
omarchy-theme-install https://github.com/othavi0/omarchy-noctua-theme
```

## Palette

Noctua keeps the One Dark Pro syntax family while moving the desktop base to `#242424`. The primary Omarchy accent is `#61afef`.

![Noctua palette: core, normal and bright colors with hex values](.github/assets/palette.svg)

## What's included

- Hyprland rules, borders, shadows and animation curves (`hyprland.conf`)
- Hyprlock styling (`hyprlock.conf`)
- Waybar colors (`waybar.css`) and a bundled Waybar variant (`waybar-theme/`)
- Terminals generated by Omarchy from `colors.toml`, plus Warp (`warp.yaml`)
- Shell/tools: Fish colors (`colors.fish`), fzf (`fzf.fish`)
- Apps/UI: GTK (`gtk.css`), Chromium (`chromium.theme`), Firefox (`firefox.css`), Wofi (`wofi.css`), Walker (`walker.css`)
- System tools: btop (`btop.theme`), cava (`cava_theme`), mako (`mako.ini`), SwayOSD (`swayosd.css`)
- Extras: Steam (`steam.css`), Vencord (`vencord.theme.css`), icons pointer (`icons.theme`)
- Aether and Zed theme overrides (`aether.override.css`, `aether.zed.json`)
- bat syntax theme (`bat/Noctua.tmTheme`, opt-in)
- VSCode theme reference (`vscode.json`) and token refinements (`vscode.settings.snippet.jsonc`, opt-in)

## Wallpapers

Click any thumbnail for the full-resolution file.

| | | |
| --- | --- | --- |
| [![City skyline at dusk](.github/assets/00-city-dusk.jpg)](backgrounds/00-city-dusk.jpg) | [![Close view of the moon](.github/assets/01-lunar-arc.jpg)](backgrounds/01-lunar-arc.jpg) | [![Snow-capped mountain ridge](.github/assets/02-alpine-ridge.jpg)](backgrounds/02-alpine-ridge.jpg) |
| `00-city-dusk.jpg` | `01-lunar-arc.jpg` | `02-alpine-ridge.jpg` |

## Neovim note

`neovim.lua` installs `olimorris/onedarkpro.nvim` and sets LazyVim to the `onedark` colorscheme with the Noctua background override. Comments are lifted to `#6c7380` for legibility, keywords are italic, and functions/types are bold.

## VSCode customization (opt-in)

`vscode.json` only carries the One Dark Pro extension reference because Omarchy's `omarchy-theme-set-vscode` ignores anything else. To get the same italic comments, italic keywords, and bold functions/types as Zed and Neovim, merge `vscode.settings.snippet.jsonc` into `~/.config/Code/User/settings.json` (also works for VSCodium / Cursor under their respective config paths). The block is scoped to `[One Dark Pro]` so it only fires when Noctua is active.

## bat customization (opt-in)

bat does not read theme files from Omarchy. Install the bundled tmTheme manually:

```bash
mkdir -p "$(bat --config-dir)/themes"
cp bat/Noctua.tmTheme "$(bat --config-dir)/themes/"
bat cache --build
echo '--theme="Noctua"' >> "$(bat --config-dir)/config"
```

Verify with `bat --list-themes | grep Noctua`.

## Attribution

- Color base: One Dark Pro by Binaryify: <https://github.com/Binaryify/OneDark-Pro>
- Neovim theme integration: onedarkpro.nvim by olimorris: <https://github.com/olimorris/onedarkpro.nvim>
- Waybar modified from HANCORE-Linux's waybar themes: <https://github.com/HANCORE-linux/waybar-themes>
````

- [ ] **Step 3: Rodar o verificador — deve PASSAR**

Run: `python3 scripts/check_readme.py`
Expected: `OK — README integro`, exit 0.

- [ ] **Step 4: Verificar os links externos**

Run:
```bash
for u in https://github.com/othavi0/omarchy-noctua-theme \
         https://github.com/Binaryify/OneDark-Pro \
         https://github.com/olimorris/onedarkpro.nvim \
         https://github.com/HANCORE-linux/waybar-themes; do
  printf "%s -> " "$u"; curl -sL -o /dev/null -w "%{http_code}\n" "$u"
done
```
Expected: `200` nas quatro linhas.

- [ ] **Step 5: Confirmar que a URL antiga sumiu**

Run: `rg -n "othavioquiliao" README.md || echo "OK — sem username antigo"`
Expected: `OK — sem username antigo`.

- [ ] **Step 6: Commit**

```bash
git add README.md
git commit -m "docs: reescrever README com paleta e wallpapers"
```

---

### Task 6: Captura do preview

Esta task depende de ação do autor e tem gate humano. Não commitar sem aprovação explícita da imagem.

**Files:**
- Modify: `preview.png`

**Interfaces:**
- Consumes: o tema instalado e ativo.
- Produces: `preview.png`, já referenciado pelo README desde a Task 5.

- [ ] **Step 1: Instalar a versão local do tema e ativá-la**

```bash
rm -rf ~/.config/omarchy/themes/noctua
cp -r . ~/.config/omarchy/themes/noctua
rm -rf ~/.config/omarchy/themes/noctua/.git
omarchy-theme-set noctua
```

Copiar em vez de reinstalar do GitHub porque as mudanças ainda não foram pushadas.

- [ ] **Step 2: Pedir ao autor que prepare a tela**

Perguntar ao autor, e **esperar a confirmação**:

> A captura vai registrar tudo que estiver visível no monitor. Feche o que for privado e deixe a tela como quer que apareça no README — a sugestão é Neovim com um arquivo do próprio tema aberto, btop e um terminal, sobre o wallpaper. Me avise em qual monitor (`eDP-1` ou `HDMI-A-1`) e quando estiver pronto.

- [ ] **Step 3: Capturar**

Com o nome do monitor que o autor indicou (exemplo com `eDP-1`):

```bash
grim -o eDP-1 /tmp/preview-raw.png
magick identify -format "%wx%h %b\n" /tmp/preview-raw.png
```
Expected: `1920x1080`.

- [ ] **Step 4: Otimizar**

```bash
magick /tmp/preview-raw.png -strip -define png:compression-level=9 /tmp/preview-opt.png
magick identify -format "%f %wx%h %b\n" /tmp/preview-opt.png
```

Se o resultado passar de 2,5 MB, **não** converter para JPEG mantendo a extensão `.png` — um arquivo com extensão mentindo sobre o formato confunde qualquer ferramenta que o leia. Manter PNG e reportar o tamanho ao autor, que decide entre aceitar o peso ou refazer a captura com menos ruído visual na tela.

- [ ] **Step 5: Gate de aprovação do autor**

Mostrar `/tmp/preview-opt.png` ao autor e **esperar aprovação explícita**. A imagem mostra a tela dele; ele é quem decide se pode ser publicada. Se pedir nova captura, voltar ao Step 2.

- [ ] **Step 6: Substituir e verificar**

```bash
cp /tmp/preview-opt.png preview.png
python3 scripts/check_readme.py
```
Expected: `OK — README integro`.

- [ ] **Step 7: Commit**

```bash
git add preview.png
git commit -m "docs: preview real do tema no desktop"
```

---

### Task 7: Alinhar o AGENTS.md

**Files:**
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: a estrutura final do repo, já estabelecida pelas Tasks 1–6.
- Produces: nada consumido por outras tasks. É a última.

- [ ] **Step 1: Corrigir a estrutura do projeto**

Em `AGENTS.md`, na seção "Project Structure & Module Organization", substituir a lista inteira por:

```markdown
- Root files are per-app theme configs (e.g., `hyprland.conf`, `waybar.css`, `gtk.css`, `colors.toml`).
- Terminal colors come from `colors.toml`; Omarchy generates the per-terminal configs from it.
- `backgrounds/` contains the bundled wallpapers used by the theme. Omarchy scans this directory and treats every image in it as a selectable wallpaper — never put non-wallpaper assets here.
- `waybar-theme/` holds a JSONC + CSS pair for Waybar variants.
- `.github/assets/` holds README-only assets (palette SVG, wallpaper thumbnails).
- `scripts/` holds the palette generator and the README integrity checker.
- `preview.png` is the visual snapshot used in the README.
```

`kitty.conf` e `alacritty.toml` saem: nunca existiram neste repo, vieram junto do molde do tema de origem.

- [ ] **Step 2: Corrigir a URL de install**

Trocar `othavioquiliao` por `othavi0` na linha do comando `omarchy-theme-install`.

- [ ] **Step 3: Documentar o verificador na seção de testes**

Em "Testing Guidelines", acrescentar como primeiro item:

```markdown
- Run `python3 scripts/check_readme.py` after touching the README or renaming any asset; it fails if a referenced path is missing or a theme file is undocumented.
- Regenerate the palette with `python3 scripts/gen_palette.py` after changing `colors.toml`.
```

- [ ] **Step 4: Verificar que nenhuma referência morta sobrou**

Run:
```bash
rg -n "othavioquiliao|kitty\.conf|alacritty\.toml" AGENTS.md || echo "OK — sem referencias mortas"
```
Expected: `OK — sem referencias mortas`.

- [ ] **Step 5: Verificar que os arquivos citados no AGENTS.md existem**

Run:
```bash
python3 - <<'PY'
import re, pathlib
text = pathlib.Path("AGENTS.md").read_text()
names = set(re.findall(r"`([\w./-]+\.(?:conf|toml|css|json|jsonc|lua|ini|theme|py|png|fish|yaml))`", text))
missing = sorted(n for n in names if not pathlib.Path(n).exists())
print("INEXISTENTES:", missing) if missing else print(f"OK — {len(names)} arquivos citados existem")
PY
```
Expected: `OK — N arquivos citados existem`.

- [ ] **Step 6: Rodar o verificador uma última vez**

Run: `python3 scripts/check_readme.py`
Expected: `OK — README integro`, exit 0.

- [ ] **Step 7: Commit**

```bash
git add AGENTS.md
git commit -m "docs: alinhar AGENTS.md ao repo real"
```

---

## Verificação final

Depois da última task, as três provas exigidas pelo spec:

1. **Funcional** — `python3 scripts/check_readme.py` sai 0; os quatro links externos retornam 200 (Task 5, Steps 3–4).
2. **Perceptual** — abrir o README renderizado no GitHub após o push e conferir, seção a seção, contra o mockup aprovado. Confirmar especificamente que a grade de wallpapers está preenchida e a paleta legível. **Se alguma imagem aparecer quebrada logo após o push, dar hard refresh antes de diagnosticar**: o camo cacheia por URL e mostra conteúdo velho por alguns minutos.
3. **Dados** — `du -sb backgrounds/` confirma a queda de ~10,8 MB para ~1,23 MB; `magick identify backgrounds/*` confirma três arquivos com os nomes novos.

O push não está no escopo deste plano e depende de autorização do autor.
