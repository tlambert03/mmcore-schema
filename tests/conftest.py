from __future__ import annotations

from pathlib import Path

import pytest

CONFIGS = Path(__file__).parent / "configs"
CFG_FILES = CONFIGS.glob("*.cfg")


@pytest.fixture(params=sorted(CFG_FILES), ids=lambda x: x.stem)
def cfg_file(request: pytest.FixtureRequest) -> Path:
    """Fixture to provide configuration files for testing."""
    return request.param  # type: ignore
