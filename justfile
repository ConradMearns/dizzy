install:
    uv tool install --editable .

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

# --- Code quality (lint + format) ---

lint:
    uv run ruff check dizzy/src/dizzy dizzy/tests

fmt:
    uv run ruff format dizzy/src/dizzy dizzy/tests

fmt-check:
    uv run ruff format --check dizzy/src/dizzy dizzy/tests

# Everything CI runs, in the same order. Tests are the gate; the rest are advisory.
ci: lint fmt-check check test

# Regenerate the example features and fail if anything drifted from what's committed.
examples-check:
    uv run dizzy generate libraries examples/guestbook/guestbook.feat.yaml examples/guestbook
    git diff --exit-code examples/guestbook

# --- Build ---

# Build sdist + wheel into dist/ (version comes from the current git tag via hatch-vcs).
build:
    rm -rf dist
    uv build

whitepaper:
    typst compile docs/whitepaper.typ

whitepaper-watch:
    typst watch docs/whitepaper.typ


install-completions:
    mkdir -p $HOME/.local/share/bash-completion
    just --completions bash > $HOME/.local/share/bash-completion/just.bash