# Design: hook de tema herdr

**Data:** 2026-08-07 · **Status:** aprovado

## Problema

O Omarchy não tematiza o herdr: `omarchy-theme-set` aplica apenas uma lista
fixa de apps conhecidos, então o `herdr.toml` do tema nunca é aplicado pela
instalação padrão (`omarchy-theme-install`). Hoje o arquivo é opt-in com merge
manual documentado no cabeçalho. Este repo não tem script de instalação
próprio — um tema não consegue injetar código no fluxo de install do Omarchy
(por design).

## Solução

Usar o mecanismo oficial de hooks do Omarchy: scripts em
`~/.config/omarchy/hooks/theme-set.d/` rodam a cada troca de tema.

### Componente: `herdr.hook.sh` (raiz do repo)

Script bash que o usuário instala uma única vez (cópia, não symlink —
`omarchy-theme-install` faz `rm -rf` do diretório do tema a cada
reinstalação). Comportamento a cada troca de tema:

1. `herdr` não instalado → sai silenciosamente.
2. Tema atual (`~/.local/state/omarchy/current/theme/herdr.toml`) fornece um
   tema herdr → extrai os blocos `[theme]`/`[theme.custom]` (descarta
   comentários de linha inteira), substitui as seções `[theme]*` do
   `~/.config/herdr/config.toml` preservando o resto, e marca o bloco com
   `# managed by omarchy theme-set hook`.
3. Tema atual não fornece `herdr.toml` → reverte para `name = "terminal"`
   (segue as cores do terminal, já tematizado pelo Omarchy), **somente** se o
   bloco atual tiver o marcador. Config gerenciada à mão nunca é sobrescrita.
4. `herdr server reload-config`, ignorando falha se o servidor não estiver de
   pé (a config vale no próximo start).

O hook é genérico: lê o `herdr.toml` de qualquer tema que o forneça, não só
do Noctua.

### Documentação

Seção opt-in no README com o comando de instalação do hook e a alternativa de
merge manual. Cabeçalho do `herdr.toml` passa a mencionar o hook.

## Testes

Sandbox com `HOME` falso (tema com/sem `herdr.toml`, config com/sem marcador,
config inexistente, idempotência) + verificação real na máquina.

## Fora do escopo

PR upstream no Omarchy para suporte nativo ao herdr; auto-instalação do hook.
