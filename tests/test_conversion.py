from __future__ import annotations

from pathlib import Path

import pytest

from mmcore_schema import MMConfig, conversion

CONFIGS = Path(__file__).parent / "configs"
CFG_FILES = CONFIGS.glob("*.cfg")


@pytest.fixture(params=sorted(CFG_FILES), ids=lambda x: x.stem)
def cfg_file(request: pytest.FixtureRequest) -> Path:
    """Fixture to provide configuration files for testing."""
    return request.param  # type: ignore


@pytest.mark.parametrize("ext", [".json", ".yaml"])
def test_read_cfg(cfg_file: Path, tmp_path: Path, ext: str) -> None:
    """Test reading a configuration file."""

    mm_cfg = conversion.read_mm_cfg_file(cfg_file)
    assert isinstance(mm_cfg, MMConfig)

    out_file = tmp_path / f"test{ext}"
    conversion.convert_file(cfg_file, out_file)
    assert out_file.exists()
