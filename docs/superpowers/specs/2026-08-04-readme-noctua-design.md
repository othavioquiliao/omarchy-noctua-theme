# README do Omarchy Noctua Theme — design

Data: 2026-08-04
Status: aprovado, pronto para plano de implementação

## Contexto

O pedido original foi "criar um README parecido com o do
[omarchy-miasma-theme](https://github.com/OldJobobo/omarchy-miasma-theme)". O
diagnóstico mostrou que esse pedido já está satisfeito: o README atual é uma
derivação estrutural fiel do miasma — mesma ordem de seções (título → descrição
de uma linha → preview → Install → What's included → Neovim note → Wallpapers em
tabela → Attribution), mesmo tom, mesma tabela de wallpapers. O Noctua ainda tem
três seções a mais (Palette, VSCode opt-in, bat opt-in).

Copiar o molde de novo não produz nada. O que existe é um conjunto de defeitos
concretos que fazem a página renderizada falhar.

## Achados do diagnóstico

Todos verificados contra o repo e contra o Omarchy instalado.

1. **Os oito wallpapers do README não existem.** O commit `666b85e` ("feat: bg")
   removeu os oito arquivos antigos (`00-noctua-grid.jpg`, `01-slate-rift.jpg`,
   …, ~100 KB cada) e adicionou três novos, sem atualizar o README. Como o
   markdown usa `![]()` sem alt text, a seção renderiza uma grade cinza vazia —
   nem o nome do arquivo aparece.
2. **O `preview.png` é um placeholder abstrato.** Vem do commit inicial
   `8f2e643` e nunca mudou: três retângulos escuros com barras azuis e algumas
   linhas coloridas. Não mostra o tema. O equivalente no miasma é um screenshot
   real do desktop (Waybar, Neovim, btop, terminal sobre o wallpaper) — é o
   ativo que converte visitante em instalação.
3. **A URL de install usa o username antigo** (`othavioquiliao/`). Funciona por
   redirect do GitHub, mas o repo é `othavi0/`.
4. **`firefox.css` existe no repo e não aparece em "What's included".** Auditoria
   arquivo por arquivo contra `git ls-files`: é a única omissão; todo o resto da
   lista confere.
5. **Os wallpapers estão em resolução desproporcional.** `00-noctua.jpg` tem
   8192×4608 e 6,6 MB; os três somam ~10,8 MB. Os monitores do autor são
   1920×1080. Como `omarchy-theme-install` faz `git clone` do repo inteiro, todo
   usuário que instala o tema baixa esses 10,8 MB.
6. **O `AGENTS.md` carrega os mesmos defeitos.** Cita `kitty.conf` e
   `alacritty.toml`, que não existem neste repo (vieram junto do molde do
   miasma); repete a URL `othavioquiliao`; e a linha 28 manda atualizar a tabela
   de wallpapers ao renomear assets — exatamente a regra violada em `666b85e`.

## Restrições descobertas

Duas restrições do Omarchy condicionam o design e não são negociáveis.

- **`backgrounds/` é varrido pelo Omarchy.**
  `omarchy-theme-bg-next` roda `find -L … -maxdepth 1 -type f` casando
  `jpg|jpeg|png|gif|bmp|webp` sobre o diretório. Qualquer thumbnail colocado ali
  entraria no ciclo de wallpapers do usuário. Os assets de README precisam morar
  fora de `backgrounds/`.
- **O instalador clona o repo inteiro.** `omarchy-theme-install` faz
  `git clone` para `~/.config/omarchy/themes/<nome>`, onde `<nome>` sai de
  `basename` com `s/^omarchy-//; s/-theme$//` — ou seja, `noctua`. Todo byte
  versionado é peso de instalação.

Verificado também que `preview.png` **não** é consumido por nenhum script do
Omarchy (é convenção de README) e que `.omarchy-theme.yml`, presente no miasma,
não é lido por nada nesta versão — não há motivo para adicioná-lo.

## Escopo

Dentro:

- Reescrita do `README.md`.
- Novos assets em `.github/assets/` (paleta + thumbnails).
- Script gerador da paleta em `scripts/`.
- Substituição do `preview.png` por captura real.
- Recompressão e renomeação dos três wallpapers.
- Alinhamento do `AGENTS.md` com o repo real.

Fora:

- Qualquer mudança nos arquivos de tema (cores, `hyprland.conf`, CSS dos apps).
- Adição de `.omarchy-theme.yml`.
- Novos wallpapers.

## Design

### Estrutura do README

Mantém o molde do miasma. Uma seção muda de lugar.

| # | Seção | Mudança |
|---|---|---|
| 1 | Título + descrição | Reescrita; cita os três wallpapers |
| 2 | `preview.png` | Captura real substitui o placeholder |
| 3 | Install | URL corrigida para `othavi0` |
| 4 | **Palette** | **Movida** para cá, com swatches |
| 5 | What's included | `+ firefox.css` |
| 6 | Wallpapers | Três thumbnails reais, cada um linkando o original |
| 7 | Neovim note | Inalterada |
| 8 | VSCode customization (opt-in) | Inalterada |
| 9 | bat customization (opt-in) | Inalterada |
| 10 | Attribution | Inalterada |

**Palette sobe para a posição 4** porque quem abre um repo de tema decide pela
cor, não pela lista de arquivos — essa lista é material de consulta, lido depois
da decisão. É também onde o Noctua se diferencia do miasma, que não tem seção de
paleta.

O README permanece em inglês: o ecossistema Omarchy e os repos de tema vizinhos
são todos em inglês.

Toda imagem ganha alt text descritivo. A ausência de alt em `![]()` é o motivo de
a seção quebrada de hoje renderizar muda.

### Paleta em swatches

`.github/assets/palette.svg`, gerado por `scripts/gen_palette.py` a partir dos
valores de `colors.toml`. Três faixas: **CORE** (background, foreground, accent,
selection, com nome e hex), **NORMAL** (`color0`–`color7`) e **BRIGHT**
(`color8`–`color15`), cada swatch rotulado com seu hex.

SVG e não PNG: nítido em qualquer DPI, ~6,4 KB, e o GitHub o serve como imagem
estática via camo sem problema. Serviços externos de swatch (shields.io,
dummyimage) foram descartados — um README que depende deles quebra quando eles
saem do ar.

O gerador fica versionado (~2 KB) para que a paleta possa ser regerada se
`colors.toml` mudar, em vez de virar um asset órfão que ninguém sabe reproduzir.

### Thumbnails dos wallpapers

Três arquivos em `.github/assets/`, 800×450 (16:9), qualidade 82, metadados
removidos, ~27 KB cada. O crop uniformiza a altura das células da tabela — os
originais têm proporções diferentes (16:9 e 3:2), que desalinhariam o grid.

Cada thumbnail é um link para o arquivo original em resolução cheia, e a legenda
traz nome e dimensões.

### Wallpapers: recompressão e renomeação

Lado maior reduzido para 2560 px, qualidade 88, metadados removidos, todos em
JPEG. O `.png` atual é uma fotografia — PNG só desperdiça bytes nesse caso.

Renomeação para nomes descritivos, conforme o `AGENTS.md` linha 18 já exige e
como os arquivos antigos faziam. O prefixo numérico preserva a ordem do ciclo:

| Atual | Novo | Resultado medido | Conteúdo |
|---|---|---|---|
| `00-noctua.jpg` (8192×4608, 6,6 MB) | `00-city-dusk.jpg` | 2560×1440, 466 KB | Skyline noturno |
| `01-noctua.png` (5568×3712, 2,2 MB) | `01-lunar-arc.jpg` | 2560×1707, 314 KB | Lua em close |
| `02-noctua.jpg` (6000×4000, 1,9 MB) | `02-alpine-ridge.jpg` | 2560×1707, 453 KB | Cordilheira nevada |

**10,80 MB → 1,23 MB, 89% menor.** Números medidos rodando a conversão, não
estimados. Comparação 1:1 entre original e recomprimido no gradiente escuro da
lua — o pior caso para banding JPEG — não mostra diferença perceptível.

### preview.png

Captura real do desktop com o tema ativo, via `grim` (disponível; sessão
Hyprland em `wayland-1`; monitores `eDP-1` e `HDMI-A-1`, ambos 1920×1080 @1x).

Procedimento: ativar o tema (`omarchy-theme-set noctua`), o autor organiza a tela
com o que quer expor, captura de um monitor, e o autor aprova a imagem antes do
commit. A captura registra o que estiver visível na tela, então a triagem do que
fica aberto é do autor.

Mantém o nome `preview.png` (convenção do README e citado no `AGENTS.md`) e o
formato PNG, otimizado. Fica na raiz, fora da varredura de `backgrounds/`.

### AGENTS.md

Corrigido no mesmo passo, porque é o documento que instrui manutenções futuras e
sua regra da linha 28 é justamente a que falhou:

- Remover `kitty.conf` e `alacritty.toml` da descrição de estrutura; descrever
  como o Omarchy gera os terminais a partir de `colors.toml`.
- Corrigir a URL de install para `othavi0`.
- Documentar `.github/assets/` e `scripts/` na estrutura do projeto.
- Registrar que `backgrounds/` é varrido pelo Omarchy e não aceita arquivos que
  não sejam wallpapers.

## Verificação

A entrega só é considerada completa com as três provas:

1. **Funcional** — toda imagem e todo link do README resolvem; nenhum caminho
   aponta para arquivo inexistente. Verificado por checagem dos caminhos contra
   `git ls-files`, e dos links externos por requisição HTTP.
2. **Perceptual** — o README renderizado no GitHub conferido no browser, seção a
   seção, comparado com o mockup aprovado. Especificamente: a grade de wallpapers
   preenchida e a paleta legível.
3. **Dados** — auditoria da lista "What's included" contra `git ls-files`
   (nenhum arquivo listado que não exista, nenhum arquivo de tema fora da lista),
   e medição do tamanho do repo antes e depois da recompressão.

O `preview.png` depende de aprovação explícita do autor sobre a imagem
capturada, antes do commit.

## Riscos

- **Cache do camo.** O GitHub cacheia imagens por URL; trocar o conteúdo de uma
  URL já cacheada pode mostrar a imagem antiga ou quebrada por alguns minutos.
  Um hard refresh resolve. Vale saber ao conferir logo após o push, para não
  diagnosticar como erro de caminho.
- **Renomear wallpapers muda o alvo do symlink de background** para quem já tem o
  tema instalado. O ciclo de backgrounds do Omarchy se recupera sozinho na
  próxima troca, mas quem já usa o tema pode ver o wallpaper mudar uma vez.
- **A captura de tela expõe o que estiver aberto.** Mitigado pelo gate de
  aprovação do autor antes do commit.
