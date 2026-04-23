gen-feat-pydantic:
    uv run gen-pydantic dizzy/src/dizzy/def/feat.yaml > dizzy/src/dizzy/feat_schema.py

gen-libconfig-pydantic:
    uv run gen-pydantic dizzy/src/dizzy/def/libconfig.yaml > dizzy/src/dizzy/libconfig_schema.py

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