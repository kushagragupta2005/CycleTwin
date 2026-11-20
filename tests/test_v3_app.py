"""Tests for the deployed interface: app.py -> ui3.app.main() -> ui3/* pages.

Pages are selected by seeding ``session_state["view"]`` before the first run.
(AppTest 1.50 cannot rerun a script that contains ``st.segmented_control``.)
"""
import os
import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.adapters.apple_health import parse_upload_bytes
from src.adapters.synthetic_export import build_synthetic_export
from src.paths import REPO_URL, ROOT
from ui3.app import _renderers
from ui3.navigation import PAGES

APP = str(ROOT / "app.py")


def render(page="Home", entry=APP, **state):
    at = AppTest.from_file(entry, default_timeout=90)
    at.session_state["view"] = page
    for key, value in state.items():
        at.session_state[key] = value
    return at.run()


def text_of(at):
    return "\n".join(str(element.value) for element in (*at.markdown, *at.caption))


class DeployedPages(unittest.TestCase):
    def test_every_navigation_entry_has_a_renderer(self):
        self.assertEqual(set(_renderers({"frozen_summary": []}, "Simple")), set(PAGES))

    def test_every_page_renders_without_exceptions(self):
        for page in PAGES:
            with self.subTest(page=page):
                at = render(page)
                self.assertEqual([e.message for e in at.exception], [])
                self.assertGreater(len(at.markdown), 3)
                if page != "Home":
                    self.assertIn("Synthetic research prototype", text_of(at))   # footer

    def test_app_v3_alias_renders_the_same_interface(self):
        at = render(entry=str(ROOT / "app_v3.py"))
        self.assertEqual(at.exception, [])
        self.assertGreater(len(at.markdown), 3)


class EntryPointRegression(unittest.TestCase):
    def test_page_renders_on_every_run_in_the_same_process(self):
        # Regression: app.py used to `import app_v3`; Python caches the module, so every run
        # after the first in a server process rendered an empty page.
        counts = [len(render().markdown) for _ in range(3)]
        self.assertTrue(all(count > 3 for count in counts), counts)
        self.assertEqual(len(set(counts)), 1, counts)

    def test_app_starts_from_any_working_directory(self):
        previous = os.getcwd()
        with tempfile.TemporaryDirectory() as elsewhere:
            os.chdir(elsewhere)
            try:
                at = render("Evidence")
            finally:
                os.chdir(previous)
        self.assertEqual([e.message for e in at.exception], [])
        self.assertGreater(len(at.markdown), 3)


class AboutAndSafety(unittest.TestCase):
    def test_project_record_links_point_to_github(self):
        text = text_of(render("About and safety"))
        self.assertNotIn("](docs/", text)
        self.assertIn(f"]({REPO_URL}/blob/main/docs/assumptions.md)", text)

    def test_synthetic_apple_import_runs_in_memory(self):
        export = ROOT / "apple_health_export" / "export.xml"
        before = export.stat().st_mtime_ns if export.exists() else None
        at = render("About and safety", apple_loaded=True)
        self.assertEqual(at.exception, [])
        self.assertIn("Synthetic XML parsed: 36 dates · 1 cycle starts.", text_of(at))
        after = export.stat().st_mtime_ns if export.exists() else None
        self.assertEqual(before, after, "the demo must not write into the app directory")

    def test_synthetic_export_is_deterministic_and_parseable(self):
        payload = build_synthetic_export()
        self.assertEqual(payload, build_synthetic_export())
        parsed = parse_upload_bytes(payload)
        self.assertEqual((len(parsed["daily"]), parsed["cycle_starts"]), (36, ["2025-01-01"]))


if __name__ == "__main__":
    unittest.main()
