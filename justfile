set export

# List available commands
default:
    just --list --unsorted --list-heading $'Available commands\n'

# Start notebook
start-notebook:
    #!/bin/zsh

    . .venv/bin/activate
    jupyter lab --allow-root

# Set up dev container. This step runs after building the dev container
post-dev-container-create:
    just .devcontainer/post-create
    just bootstrap

# Bootstrap project
bootstrap: install-modules setup-pre-commit

# Install the tools needed to run the project
install-tools: install-rye bootstrap

[private]
install-rye:
    #!/bin/zsh

    curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash

[private]
install-modules:
    #!/bin/zsh

    . "$HOME/.rye/env"
    rye sync

[private]
setup-pre-commit:
    #!/bin/zsh

    . .venv/bin/activate
    pre-commit install
