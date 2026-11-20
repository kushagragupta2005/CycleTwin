"""CycleTwin v3 interface. ``main()`` must be *called* by the Streamlit entry script on every run.

Streamlit re-executes the entry script on each rerun, but Python caches imported
modules, so rendering cannot live in a module's import-time side effects.
"""
from __future__ import annotations

import streamlit as st

from src.claims import load_claims
from src.paths import REPO_URL, THEME_CSS, repo_url
from ui3.about_safety import render_about_safety
from ui3.evidence import render_evidence
from ui3.home import render_home
from ui3.kushi import render_kushi
from ui3.navigation import render_top_navigation
from ui3.patient import render_patient
from ui3.patients import render_patients

FOOTER = (
    '<footer class="ct-footer">Synthetic research prototype. Not for diagnosis, contraception, conception planning, '
    'or treatment decisions. '
    f'<a href="{REPO_URL}" target="_blank" rel="noopener noreferrer">Source code</a> · '
    f'<a href="{repo_url("LICENSE")}" target="_blank" rel="noopener noreferrer">MIT License</a> · Team CycleTwin</footer>'
)


def go_to(page: str) -> None:
    st.session_state["view"] = page


def _renderers(claims: dict, language: str) -> dict:
    return {
        "Home": lambda: render_home(claims=claims, frozen_summary=claims["frozen_summary"], go_to=go_to,
                                    language=language),
        "Synthetic patients": lambda: render_patients(language=language, go_to=go_to),
        "One patient": lambda: render_patient(language=language, claims=claims),
        "Evidence": lambda: render_evidence(claims=claims, language=language),
        "Meet Kushi": lambda: render_kushi(claims=claims, language=language),
        "About and safety": lambda: render_about_safety(claims=claims, language=language),
    }


def main() -> None:
    st.set_page_config(page_title="CycleTwin", layout="wide", initial_sidebar_state="collapsed")
    st.markdown(f"<style>{THEME_CSS.read_text()}</style>", unsafe_allow_html=True)
    claims = load_claims()
    page, language = render_top_navigation()
    renderers = _renderers(claims, language)
    renderers.get(page, renderers["Home"])()
    if page != "Home":
        st.markdown(FOOTER, unsafe_allow_html=True)
