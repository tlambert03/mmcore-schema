from __future__ import annotations

from pathlib import Path

import pytest

from mmcore_schema import MMConfigFile, conversion

CONFIGS = Path(__file__).parent / "configs"
CFG_FILES = CONFIGS.glob("*.cfg")


@pytest.fixture(params=sorted(CFG_FILES), ids=lambda x: x.stem)
def cfg_file(request):
    """Fixture to provide configuration files for testing."""
    return request.param


def test_read_cfg(cfg_file: Path, tmp_path: Path) -> None:
    """Test reading a configuration file."""

    mm_cfg = conversion.read_mm_cfg_file(cfg_file)
    assert isinstance(mm_cfg, MMConfigFile)

    out_file = tmp_path / "test.json"
    conversion.convert_file(cfg_file, out_file)
    assert out_file.exists()
