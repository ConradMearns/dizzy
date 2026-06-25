# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Feature-file format** (`.feat.yaml`): a single artifact declaring a domain
  as commands, events, procedures, policies, projections, models, and queries —
  the reactivity loop (commands → procedures → events → policies) and the data
  loop (events → projections → models → queries).
- **`dizzy generate`** — the three-stage pipeline from a feature-file:
  `definitions` (LinkML `def/` schema stubs), `static` (the `gen_def/` and
  `gen_int/` typed-contract packages), and `libraries` (per-runtime
  implementation-stub packages driven by `libconfig.yaml`).
- **Runtime targets**: `python-uv` (most complete), plus experimental
  `rust-cargo` and `typescript-npm` generators; model adapters (e.g. `sqla`).
- **`dizzy simulate`** — LLM-driven execution of a feature-file against a
  scenario (level 0).
- **`dizzy onboard` / `docs` / `config`** — agent-facing project overview, the
  CLI + authoring documentation, and a config template.
- **Worked examples**: a fully implemented, runnable `guestbook`, plus
  `recipes`, `library`, and `agent` feature-files.
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
