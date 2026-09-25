import re
from pathlib import Path

from smartconnect import __version__


def test_version_matches_pyproject():
    """__version__ must stay aligned with pyproject.toml (it drifted once:
    the 1.11.2 release left it at 1.11.0)."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    match = re.search(
        r'^version\s*=\s*"([^"]+)"', pyproject.read_text(), re.MULTILINE
    )
    assert match, "no version in pyproject.toml"
    assert __version__ == match.group(1)
