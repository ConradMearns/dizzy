# Whitepaper commands

# Compile whitepaper to PDF
whitepaper:
    typst compile whitepaper.typ

# Watch and recompile whitepaper on changes
whitepaper-watch:
    typst watch whitepaper.typ

# Documentation commands

# Serve documentation locally
docs-serve:
    mkdocs serve

# Deploy documentation to GitHub Pages
docs-deploy:
    mkdocs gh-deploy

# Force deploy documentation to GitHub Pages
docs-deploy-force:
    mkdocs gh-deploy --force
