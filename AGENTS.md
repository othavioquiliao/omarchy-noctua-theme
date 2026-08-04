# Repository Guidelines

## Project Structure & Module Organization
- Root files are per-app theme configs (e.g., `hyprland.conf`, `waybar.css`, `gtk.css`, `colors.toml`).
- Terminal colors come from `colors.toml`; Omarchy generates the per-terminal configs from it.
- `backgrounds/` contains the bundled wallpapers used by the theme. Omarchy scans this directory and treats every image in it as a selectable wallpaper — never put non-wallpaper assets here.
- `waybar-theme/` holds a JSONC + CSS pair for Waybar variants.
- `.github/assets/` holds README-only assets (palette SVG, wallpaper thumbnails).
- `scripts/` holds the palette generator and the README integrity checker.
- `preview.png` is the visual snapshot used in the README.

## Build, Test, and Development Commands
This repo is configuration-only; there is no build system or automated test runner.
- Install the theme with Omarchy: `omarchy-theme-install https://github.com/othavi0/omarchy-noctua-theme`.
- For local iteration, edit files in place and reload the target app (e.g., restart Waybar or reload Hyprland).

## Coding Style & Naming Conventions
- Follow the existing formatting in each file type; do not reformat unrelated sections.
- Indentation: Hyprland configs use 4 spaces inside blocks; Lua uses 2 spaces.
- Colors use hex or rgba formats as already present (e.g., `#abb2bf`, `rgba(0, 0, 0, 0.6)`).
- Keep filenames descriptive and lowercase, especially for wallpapers in `backgrounds/`.

## Testing Guidelines
- Run `python3 scripts/check_readme.py` after touching the README or renaming any asset; it fails if a referenced path is missing or a theme file is undocumented.
- Regenerate the palette with `python3 scripts/gen_palette.py` after changing `colors.toml`.
- No other automated tests are defined.
- Verify changes visually in the target app and update `preview.png` when the UI changes.
- For Neovim, confirm `olimorris/onedarkpro.nvim` loads and keeps the `#242424` background override.

## Commit & Pull Request Guidelines
- Commit history is short and direct (e.g., “update readme”, “color corrections”); keep messages concise and action-focused.
- In PRs, list the files/apps affected and include screenshots when UI output changes.
- If you add or rename assets, update the README’s “What’s included” or wallpapers table accordingly.
