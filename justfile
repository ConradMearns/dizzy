check:
    uv run ty check dizzy

docs-serve:
    mkdocs serve

docs-deploy:
    mkdocs gh-deploy

docs-deploy-force:
    mkdocs gh-deploy --force


dizzy-linkml:
    # 1. feature hlv -> feature model fm
    uvx --from linkml gen-python dizzy/src/feature_schema.yaml > dizzy/src/feature_model.py


fresh-dedupe: dizzy-linkml
    # 2. hlv+fm -> ecls
    uv run generate_linkml_from_feature.py app/dedupe/scan_and_upload.feat.yaml app/dedupe/scan_and_upload/def --fresh


gen-dedupe: dizzy-linkml
    # 2. hlv+fm -> ecls
    uv run generate_linkml_from_feature.py app/dedupe/scan_and_upload.feat.yaml app/dedupe/scan_and_upload/def
    # uv run dizzy app/dedupe/def app/dedupe/gen

    # 3. user updates the ecls
    # at this point - hopefully user/ai have updated all generated linkml ...

    # 4. gen from hlv+fm+ecls
    rm app/dedupe/scan_and_upload/gen/ -rf
    mkdir -p app/dedupe/scan_and_upload/gen/commands/pyd/
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/commands/start_scan.yaml > app/dedupe/scan_and_upload/gen/commands/pyd/start_scan.py
    # uvx --from linkml gen-python app/dedupe/scan_and_upload/def/commands/start_scan.yaml > app/dedupe/scan_and_upload/gen/commands/dataclasses/start_scan.py # example

    # 5 generate protocols gen+hlv+fm+ecls -> language protocols
    # Generate procedure contexts and protocol interfaces
    uv run generate_protocols_from_commands.py app/dedupe/scan_and_upload.feat.yaml app/dedupe/scan_and_upload/gen

    # 6
    # now that the protocol is done - we need to make a script that scans the partition
    # (executes the command) and logs the events
    # in this case we kinda know what we want our event to look like
    # we may try a few compositions
    # command-ls + protocol + context -> {feat}/procedure/lcpc_py{procedure}.py

    mkdir -p app/dedupe/scan_and_upload/src/procedure/lcpc_a_py/
    # mkdir -p app/dedupe/scan_and_upload/src/procedure/lcpc_py/start_scan.py

    # > @app/dedupe/scan_and_upload/def/commands/start_scan.yaml + @app/dedupe/scan_and_upload/gen/procedure/py/partition_scan_protocol.py + @app/dedupe/scan_and_upload/gen/procedure/py/partition_scan_context.py -> app/dedupe/scan_and_upload/src/procedure/lcpc_py/start_scan.py 

install-completions:
    mkdir -p $HOME/.local/share/bash-completion
    just --completions bash > $HOME/.local/share/bash-completion/just.bash

