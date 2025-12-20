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


fresh-dedupe: dizzy-linkml
    uv run generate_linkml_from_feature.py app/dedupe/scan_and_upload.feat.yaml app/dedupe/scan_and_upload/def --fresh
    # uv run dizzy app/dedupe/def app/dedupe/gen


gen-dedupe: dizzy-linkml
    uv run generate_linkml_from_feature.py app/dedupe/scan_and_upload.feat.yaml app/dedupe/scan_and_upload/def
    # uv run dizzy app/dedupe/def app/dedupe/gen

    # at this point - hopefully user/ai have updated all generated linkml ...

    # todo - need to autogen
    rm app/dedupe/scan_and_upload/gen/ -rf
    mkdir -p app/dedupe/scan_and_upload/gen/commands/pyd/
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/commands/start_scan.yaml > app/dedupe/scan_and_upload/gen/commands/pyd/start_scan.py
    # uvx --from linkml gen-python app/dedupe/scan_and_upload/def/commands/start_scan.yaml > app/dedupe/scan_and_upload/gen/commands/dataclasses/start_scan.py # example

    # Generate procedure contexts and protocol interfaces
    uv run generate_protocols_from_commands.py app/dedupe/scan_and_upload.feat.yaml app/dedupe/scan_and_upload/gen


install-completions:
    mkdir -p $HOME/.local/share/bash-completion
    just --completions bash > $HOME/.local/share/bash-completion/just.bash

