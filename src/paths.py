"""Repository-anchored paths, so the app works from any working directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FIGURES = DOCS / "figures"
THEME_CSS = ROOT / "ui3" / "theme.css"

REPO_URL = "https://github.com/kushagragupta2005/CycleTwin_VIT"


def repo_url(relative_path: str) -> str:
    """Public GitHub URL for a repository file (relative links 404 inside a Streamlit app)."""
    return f"{REPO_URL}/blob/main/{relative_path.lstrip('/')}"
