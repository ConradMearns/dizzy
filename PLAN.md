# Dizzy Generator — Plan

Clean up ISSUES.md after completing tasks.

## Phase 1 — Remove Legacy Scripts

- [x] Delete `generate_linkml_from_feature.py` from repo root
- [x] Delete `generate_protocols_from_commands.py` from repo root

---

## Phase 2 — Consolidate Root pyproject.toml

- [ ] Delete `/home/conrad/dizzy/pyproject.toml` (root workspace wrapper)
- [ ] Move `dizzy/pyproject.toml` up to repo root (or verify it already works as the root)
- [ ] Remove `[tool.uv.workspace]` section; confirm `uv` commands still work from repo root

---

## Phase 4 — Add Missing Test Coverage for 2+ Emits

- [x] Add a test in `test_procedures.py` with a procedure that has 2+ emits — assert all emitter fields appear in the generated dataclass
- [x] Add a test in `test_policies.py` with a policy that has 2+ emits — same assertion

---

## Phase 5 — Fix `dizzy gen` Error When def/ Stubs Are Missing

- [x] In `gen()` (`cli.py`), add a guard at the top that checks for the expected `def/` input files
- [x] If any are missing, print a clear message instructing the user to run `dizzy scaffold` first, then exit with a non-zero code
- [x] Add or extend an integration test in `test_cli.py` to cover this error path

---

## Phase 7 — Install & Manual Smoke Test

- [ ] Install dizzy globally: `uv tool install --editable /home/conrad/dizzy/dizzy`
- [ ] Run `dizzy scaffold example.feat.yaml app/example` — verify def stubs created, next-steps message printed
- [ ] Run `dizzy gen example.feat.yaml app/example` — verify all sections generate correctly, src stubs created
- [ ] Re-run both commands — verify existing def/ and src/ files are not overwritten
- [ ] Run `dizzy scaffold /home/conrad/dizzy-recipe/app/01_dj_scripts/recipe.feat.yaml /home/conrad/dizzy-recipe/app/01_dj_scripts` — verify best-effort (no events, no projections → no output for those sections, no errors)
