export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="robbyrussell"

plugins=(
    git
    zsh-autosuggestions
    zsh-syntax-highlighting
)

. $ZSH/oh-my-zsh.sh
. "$HOME/.atuin/bin/env"
. "$HOME/.cargo/env"
. "$HOME/.rye/env" || true

eval "$(atuin init zsh)"
