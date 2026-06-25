# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Trunk-based CI (`ci.yml`): tests gate every PR; ruff lint/format and `ty`
  type checks run as advisory signal.
- Tag-driven release pipeline (`release.yml`): a `v*` tag builds the sdist +
  wheel and cuts a GitHub Release with those artifacts attached.
- `CONTRIBUTING.md` documenting the dev setup, quality gates, and release flow.
- `ruff` (lint + format) and `ty` added to the dev dependency group, with
  `just lint`, `just fmt`, `just fmt-check`, `just ci`, and `just build`
  recipes.

### Changed
- Package version is now derived from git tags via `hatch-vcs` instead of being
  hardcoded in `pyproject.toml` and `__init__.py`.
- `pyproject.toml` gained release metadata (license, authors, classifiers, URLs).

[Unreleased]: https://github.com/PNNL/dizzy/compare/HEAD
