check:
    uv run ty check dizzy

docs-serve:
    mkdocs serve

docs-deploy:
    mkdocs gh-deploy

docs-deploy-force:
    mkdocs gh-deploy --force

dizzy-linkml:
    uvx --from linkml gen-python dizzy/src/feature_schema.yaml > dizzy/src/feature_model.py

gen-dedupe: dizzy-linkml
    uv run dizzy app/dedupe/def app/dedupe/gen

install-completions:
    mkdir -p $HOME/.local/share/bash-completion
    just --completions bash > $HOME/.local/share/bash-completion/just.bash
