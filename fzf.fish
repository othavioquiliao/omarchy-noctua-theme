set -l color00 '#242424'
set -l color01 '#e06c75'
set -l color02 '#98c379'
set -l color03 '#d19a66'
set -l color04 '#61afef'
set -l color05 '#c678dd'
set -l color06 '#56b6c2'
set -l color07 '#abb2bf'
set -l color08 '#5c6370'
set -l color09 '#e06c75'
set -l color0A '#98c379'
set -l color0B '#e5c07b'
set -l color0C '#61afef'
set -l color0D '#c678dd'
set -l color0E '#56b6c2'
set -l color0F '#ffffff'

set -l FZF_NON_COLOR_OPTS

for arg in (echo $FZF_DEFAULT_OPTS | tr " " "\n")
    if not string match -q -- "--color*" $arg
        set -a FZF_NON_COLOR_OPTS $arg
    end
end

set -Ux FZF_DEFAULT_OPTS "$FZF_NON_COLOR_OPTS"" --color=bg+:$color00,bg:$color00,spinner:$color0E,hl:$color04"" --color=fg:$color07,header:$color05,info:$color0A,pointer:$color04"" --color=marker:$color0E,fg+:$color0F,prompt:$color04,hl+:$color05"
