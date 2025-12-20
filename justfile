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
    mkdir -p app/dedupe/scan_and_upload/gen/events/pyd/
    
    # commands
    # uvx --from linkml gen-python app/dedupe/scan_and_upload/def/commands/start_scan.yaml > app/dedupe/scan_and_upload/gen/commands/dataclasses/start_scan.py # example
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/commands/create_image_priority_manifest.yaml > app/dedupe/scan_and_upload/gen/commands/pyd/create_image_priority_manifest.py
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/commands/start_scan.yaml > app/dedupe/scan_and_upload/gen/commands/pyd/start_scan.py
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/commands/upload_blob_using_manifest.yaml > app/dedupe/scan_and_upload/gen/commands/pyd/upload_blob_using_manifest.py

    # events
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/events/manifest_upload_started.yaml > app/dedupe/scan_and_upload/gen/events/pyd/manifest_upload_started.py
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/events/priority_manifest_created.yaml > app/dedupe/scan_and_upload/gen/events/pyd/priority_manifest_created.py
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/events/scan_complete.yaml > app/dedupe/scan_and_upload/gen/events/pyd/scan_complete.py
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/events/scan_item_failed.yaml > app/dedupe/scan_and_upload/gen/events/pyd/scan_item_failed.py
    uvx --from linkml gen-python app/dedupe/scan_and_upload/def/events/scan_item_found.yaml > app/dedupe/scan_and_upload/gen/events/pyd/scan_item_found.py

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

