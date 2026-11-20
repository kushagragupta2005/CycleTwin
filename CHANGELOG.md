# Changelog

Notable changes to CycleTwin. Dates are ISO 8601. Evaluation numbers live in
[docs/RESULTS.md](docs/RESULTS.md) and are never edited by hand.

## Unreleased

### Changed
- README rebuilt as a project landing page:
  - badges, current screenshot, overview, quick start;
  - architecture diagram, headline results, "where it breaks";
  - project structure and limitations.
- The full evaluation write-up is now generated as `docs/RESULTS.md`.
- Result JSON files moved from the repository root into `results/`:
  - `results.json` → `results/development.json`;
  - `results_*.json` → `results/*.json`.
  - File contents and hashes are unchanged.
- Hackathon material is archived:
  - `SUBMISSION_CHECKLIST.md` → `docs/submission/CHECKLIST.md`;
  - `UI_V3_CHANGELOG.md` → `docs/UI_V3_CHANGELOG.md`.
- CI runs on Python 3.9 and 3.11 and also validates the generated documents.

### Added
- `CITATION.cff` and this changelog.

### Removed
- `scripts/update_readme_results.py`. It targeted README markers that no
  longer exist.

## 2026-11-21: deployed app fix ([#1](https://github.com/kushagragupta2005/CycleTwin/pull/1))

### Fixed
- The Streamlit app went blank after the first interaction (`app.py` imported
  the page module instead of calling it).
- The app crashed unless it was started from the repository root.
- The synthetic Apple Health demo no longer writes into the app directory.
- In-app document links pointed to relative paths that 404 inside Streamlit.

### Added
- Tests for every deployed page (`tests/test_v3_app.py`).

## 2026-10-20: challenge submission (`submission-2026-10-20`)

- v3 interface: Home, synthetic patients, single patient, evidence, the
  fictional persona and about/safety. See
  [docs/UI_V3_CHANGELOG.md](docs/UI_V3_CHANGELOG.md).
- Post-freeze reporting:
  - calibration and subgroups;
  - sequential alert policy;
  - robustness sweeps;
  - Bayesian timing posterior;
  - simulated assay-like extension;
  - local operations;
  - conformal coverage.
- Pitch and architecture decks generated from `docs/claims.json`.

## 2026-10-20: frozen evaluation (`frozen-v1`)

- Predeclared protocol committed before the reserved seeds 7001, 7003 and 7007
  were generated, then executed once under a lock.
- Results are immutable and verified by hash in `results/frozen_receipt.json`.

## 2026-10-19: initial development

- Synthetic-only project scope and evaluation plan.
- Cohort simulator, feature builder, persisted logistic models, safety gate,
  Apple Health adapter and dashboard.
