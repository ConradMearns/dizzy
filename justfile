test:
    uv run pytest

test-update:
    uv run pytest --snapshot-update

check:
    uv run ty check dizzy/src/dizzy dizzy/tests

whitepaper:
    typst compile whitepaper.typ

whitepaper-watch:
    typst watch whitepaper.typ


install-completions:
    mkdir -p $HOME/.local/share/bash-completion
    just --completions bash > $HOME/.local/share/bash-completion/just.bash