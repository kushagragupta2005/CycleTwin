# CycleTwin app-layer refactor plan

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
