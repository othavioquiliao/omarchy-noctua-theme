#!/bin/bash
# Omarchy theme-set hook: sincroniza o tema do herdr a cada troca de tema.
#
# Instalacao (copia, nao symlink — reinstalar o tema apaga o diretorio):
#   mkdir -p ~/.config/omarchy/hooks/theme-set.d
#   cp ~/.config/omarchy/themes/noctua/herdr.hook.sh \
#      ~/.config/omarchy/hooks/theme-set.d/herdr
#
# Se o tema recem-aplicado fornece um herdr.toml, seus blocos [theme] sao
# gravados em ~/.config/herdr/config.toml; senao, o herdr volta para o tema
# "terminal" (que segue as cores do terminal, ja tematizado pelo Omarchy).
# Um bloco [theme] editado a mao pelo usuario nunca e sobrescrito: o hook so
# substitui blocos que ele mesmo gravou (identificados pelo marcador abaixo).

set -u

command -v herdr >/dev/null 2>&1 || exit 0

THEME_TOML="$HOME/.local/state/omarchy/current/theme/herdr.toml"
CONFIG="$HOME/.config/herdr/config.toml"
MARKER="# managed by omarchy theme-set hook"

mkdir -p "${CONFIG%/*}"
touch "$CONFIG"

# Reescreve o config: tudo menos as secoes [theme]/[theme.*], seguido do
# bloco novo com o marcador na linha apos o cabecalho [theme].
write_config() {
  local block="$1" tmp
  tmp=$(mktemp) || exit 0
  awk '
    /^\[/ { in_theme = ($0 ~ /^\[theme[].]/) }
    !in_theme
  ' "$CONFIG" | awk 'NF { if (blank) print ""; blank = 0; print; next } { blank = 1 }' >"$tmp"
  [[ -s $tmp ]] && echo >>"$tmp"
  printf '%s\n' "$block" | awk -v marker="$MARKER" '
    { print; if (!done && /^\[theme\]/) { print marker; done = 1 } }
  ' >>"$tmp"
  mv "$tmp" "$CONFIG"
}

if [[ -f $THEME_TOML ]]; then
  block=$(grep -vE '^[[:space:]]*(#|$)' "$THEME_TOML")
  [[ $block == *"[theme]"* ]] || exit 0
  write_config "$block"
elif grep -qxF "$MARKER" "$CONFIG"; then
  write_config '[theme]
name = "terminal"
auto_switch = false'
else
  exit 0
fi

herdr server reload-config >/dev/null 2>&1 || true
