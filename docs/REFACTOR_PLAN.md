# CycleTwin refactor plans

- [Part 2: repository presentation](#part-2-repository-presentation) (branch `docs/repo-presentation`)
- [Part 1: app layer](#part-1-app-layer) (merged in #1)

## Part 2: repository presentation

The GitHub landing page still read like an unfinished hackathon submission.
The deadline was 2026-10-20, and the repository is now a public portfolio and
research project.

### Findings

* **Hackathon-first README.**
  * The title used the old repo name (`CycleTwin_VIT`).
  * Two placeholder links were broken: `Live demo — replace LIVE_DEMO_URL`
    and `Video — replace VIDEO_URL`.
  * The opening was registration text ("Team…, College…, Registration and
    contact details are submitted… on Unstop").
  * About 150 table rows (every seed × day × tier) came before any
    explanation of how to run the project.
* **No quick orientation.**
  * There was no badge row, no current screenshot (the PNGs show the
    retired pre-v3 dashboard), no architecture diagram and no
    project-structure map.
  * Testing and regeneration commands were buried in prose.
* **Cluttered root.**
  * Nine result JSON files (`results.json`, `results_*.json`) sat next to
    `app.py`, alongside hackathon files (`SUBMISSION_CHECKLIST.md`,
    `UI_V3_CHANGELOG.md`).
  * There was no `CHANGELOG.md` or `CITATION.cff`.
* **Empty GitHub "About" box.** No description and no topics.
* **Constraint.** `README.md` is generated from `docs/claims.json`, and
  tests and `scripts/validate_claims.py` require the file to match the
  generated copy exactly, so the README cannot be hand-edited.

### Plan

1. **Generator.**
   * `scripts/deliverable_content.compose()` keeps producing the full
     evidence write-up, but as `docs/RESULTS.md` (same sections and
     caveats, plus the moved file paths).
   * It now also builds a conventional project README from the same
     claims: badges, synthetic-data warning, screenshot, overview,
     features, quick start, mermaid architecture, headline results, "where
     it breaks", project structure, development, limitations,
     acknowledgements, citation and licence.
   * `write_claim_deliverables.py` writes both files, and
     `validate_claims.py` checks both.
   * Remove the obsolete `scripts/update_readme_results.py`. It targets
     README markers that no longer exist and is not called by the Makefile.
2. **Root declutter.**
   * `git mv` the result JSONs into `results/`: `results.json` →
     `results/development.json`, `results_X.json` → `results/X.json`.
   * Update every reader and writer (scripts and tests).
   * File contents are untouched, so the frozen receipt hash still
     verifies.
   * Historical audit and gate logs keep their original wording.
3. **Hackathon archive.**
   * Move `SUBMISSION_CHECKLIST.md` to `docs/submission/CHECKLIST.md`
     (`build_submission.py` writes there).
   * Move `UI_V3_CHANGELOG.md` to `docs/UI_V3_CHANGELOG.md`.
   * Add a root `CHANGELOG.md` and `CITATION.cff`.
4. **Screenshots.** Capture the current v3 interface for the README hero
   image.
5. **CI.** Add Python 3.9 next to 3.11, pinned to `ubuntu-24.04` because
   `ubuntu-latest` (26.04) has no 3.9 build, so the README's version badge
   matches what is tested.
6. **GitHub About.** Set the description and topics with `gh repo edit`.

### Regression gate

* The deck, architecture, video-script and runbook entries in
  `docs/claims.json` stay byte-identical, so the PPTX/PDF deliverables need
  no rebuild.
* All moved result files keep their SHA-256.
* All tests pass, as do `build_claims.py --check` and `validate_claims.py`.

---

## Part 1: app layer

Branch: `fix/cycletwin-app-entry`.

Scope: the deployed Streamlit app and its tests. The research pipeline,
frozen artifacts, `docs/claims.json` and the generated README are not touched,
because their contents are checked by `scripts/build_claims.py --check` and
the frozen guards.

## Findings

Ranked by user impact.

### F1. The deployed app goes blank on the first interaction (critical)

`app.py` (the Streamlit Cloud entry) only did `import app_v3`. Streamlit
re-executes `app.py` on every rerun, but Python caches imported modules, so
from the second run onward `import app_v3` does nothing and **no page is
rendered**.

Reproduced with `streamlit run app.py`: the home page loads, then clicking
"Evidence" (or any toggle) leaves an empty page. The same happens to every
later session that shares the server process.

### F2. The deployed UI has no tests

All Streamlit `AppTest`s target `app_legacy.py`, the pre-v3 dashboard, which
is not deployed. `app.py`, `app_v3.py` and `ui3/*` had zero coverage, which
is how F1 shipped with a green CI.

### F3. The app only works when started from the repository root

`ui3/theme.css`, `docs/figures/*.svg` and `apple_health_export/export.xml`
were read through cwd-relative paths. Launching from any other directory
raised `FileNotFoundError: 'ui3/theme.css'` before anything rendered.
`src/claims.py` and `src/inference.py` already used `ROOT`-anchored paths.

### F4. The Apple Health demo writes into the source tree at runtime

The "Load synthetic Apple Health export" button ran
`scripts/make_synthetic_apple_export.py` in a subprocess, using a
cwd-relative script path. That wrote `apple_health_export/export.xml` into
the app directory, which is shared by every session on a hosted deployment,
and then parsed it from disk.

### F5. Broken links and stale copy in the deployed UI

* The "Read the project record" links (`docs/assumptions.md`, ...) are
  relative URLs. In a Streamlit app they resolve against the app's URL and
  return 404.
* The fallback branch of `app_v3.py` pointed users to `streamlit run app.py`
  for "the complete current dashboard". `app.py` now *is* the v3 app.

## Plan

1. **F1.**
   * Move the v3 page body into `ui3/app.py:main()`.
   * `app.py` and `app_v3.py` both call `main()`, so a function call (not an
     import side effect) renders the page on every run.
   * Use a page-to-renderer dict with Home as the fallback, in place of the
     unreachable `else` branch (F5).
2. **F3.** Add `src/paths.py` with `ROOT`-anchored constants (`THEME_CSS`,
   `FIGURES`) and a `repo_url()` helper. Use it everywhere the UI reads a file.
3. **F4.**
   * Move the export builder into `src/adapters/synthetic_export.py`, which
     returns the XML bytes.
   * The UI parses those bytes in memory with the existing
     `parse_upload_bytes`, so nothing is written to the app directory.
   * The script keeps its CLI and writes the identical file.
4. **F5.** Point the document links to the GitHub repository (`repo_url()`).
5. **F2.** Add `tests/test_v3_app.py`:
   * every page renders without exceptions through `app.py`;
   * a regression test that renders `app.py` twice in one process (F1);
   * a launch from a foreign working directory (F3);
   * no file is written by the Apple demo (F4);
   * no relative document links (F5);
   * the export builder is byte-identical to the script's output.

## Regression gate

* The existing 40 tests and `scripts/build_claims.py --check` keep passing.
* The synthetic export XML is byte-identical to the previous script output.

## Outcome

All plan items are done.

**Verified in a real browser.** `streamlit run app.py` was started from `/tmp`
(a foreign working directory). These all render correctly:
* navigating Home → Evidence (previously a blank page);
* switching Simple → Detailed;
* opening About and safety;
* clicking "Load synthetic Apple Health export" ("Synthetic XML parsed: 36
  dates · 1 cycle starts."), with no file written.

The project-record links resolve to GitHub.

**Tests:**
* 48 tests pass: the 40 existing ones and 8 new in `tests/test_v3_app.py`.
* `scripts/build_claims.py --check` passes.
* Run against the old `app.py`/`app_v3.py`/`about_safety.py`, the new tests
  report 10 failures, so they catch every finding above.
* The synthetic export XML is byte-identical to the previous script output.

**Issue found during implementation and fixed:**
* The suite printed Streamlit's deprecation notice for `use_container_width`
  (scheduled for removal) from the deployed pages. The 25 `st.dataframe`
  calls now use `width="stretch"`.
* The 6 `st.altair_chart` calls keep `use_container_width=True`, because
  `altair_chart()` in the pinned Streamlit 1.50 does not accept `width`. The
  new page tests caught that when the first attempt replaced them too.
* The deprecation notice no longer appears.

**Left as-is (out of scope, worth a decision):**
* `app_legacy.py`, `src/kushi_ui.py` and `src/reporting_ui.py` (about 60 KB)
  are not deployed, but still carry the original dashboard tests and put UI
  code inside `src/`. Retiring or relocating them is a product decision.
* The README "Live demo" link is still the `LIVE_DEMO_URL` placeholder. The
  README is generated from `docs/claims.json`, so the URL should be set
  through the claims pipeline.
