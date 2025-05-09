import sys
from pathlib import Path

import pytest

from mmcore_schema import __main__


@pytest.mark.parametrize("ext", [".json", ".yaml", ".cfg", ""])
def test_cli(
    cfg_file: Path,
    ext: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test the CLI for mmcore_schema."""
    if ext:
        out_file = tmp_path / f"test{ext}"
        monkeypatch.setattr(sys, "argv", ["mmconfig", str(cfg_file), str(out_file)])
    else:
        monkeypatch.setattr(sys, "argv", ["mmconfig", str(cfg_file)])
    __main__.main()
    captured = capsys.readouterr()
    # calling without second argument should print to stdout
    assert bool(captured.out) is bool(ext == "")
