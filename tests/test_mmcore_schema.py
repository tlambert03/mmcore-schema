import pytest
from pydantic import ValidationError

from mmcore_schema import MMConfig


def test_config() -> None:
    mm_config = MMConfig(
        devices=[
            {"label": "MyCam", "library": "DemoCamera", "name": "DCam"},
            ("Dev", "Lib", "Name"),  # this is allowed
        ],
        startup_configuration=[
            {"device_label": "Core", "property": "TimeoutMs", "value": 1000},
            ("Core", "Camera", "MyCam"),  # this is allowed
        ],
        configuration_groups=[
            {
                "name": "SomeGroup",
                "configurations": [
                    {
                        "name": "SomeConfig",
                        "settings": [
                            {
                                "device_label": "Camera",
                                "property": "PixelSize",
                                "value": "1.0",
                            },
                            ("Camera", "Binning", 2),  # this is allowed
                        ],
                    }
                ],
            }
        ],
    )
    assert mm_config.startup_configuration
    assert not mm_config.shutdown_configuration

    my_cam = mm_config.get_device("MyCam")
    assert my_cam is not None
    assert my_cam.label == "MyCam"
    assert mm_config.get_device("NotMyCam") is None

    cfg_grp = mm_config.get_configuration_group("SomeGroup")
    assert cfg_grp is not None
    assert mm_config.get_configuration_group("NotSomeGroup") is None

    cfg = cfg_grp.get_configuration("SomeConfig")
    assert cfg is not None
    assert cfg_grp.get_configuration("NotSomeConfig") is None

    for mode in ("python", "json"):
        dumped = mm_config.model_dump(exclude_unset=True, mode=mode)
        assert "schema_version" in dumped


def test_special_groups() -> None:
    mm_config = MMConfig(
        devices=[
            {"label": "MyCam", "library": "DemoCamera", "name": "DCam"},
        ],
        configuration_groups=[
            {
                "name": "System",
                "configurations": [
                    {"name": "Startup", "settings": [("MyCam", "Binning", 2)]},
                    {"name": "Shutdown", "settings": [("MyCam", "Binning", 2)]},
                ],
            }
        ],
    )
    assert mm_config.startup_configuration is not None
    assert mm_config.shutdown_configuration is not None


def test_config_errors() -> None:
    # cannot have two devices with the same label
    with pytest.raises(ValidationError):
        MMConfig(devices=[{"label": "Core"}, {"label": "Core"}])

    with pytest.raises(ValidationError):
        MMConfig(devices=[("Dev", "Lib", "Name"), ("Dev", "Lib", "Name")])

    # cannot use Core for any other device
    with pytest.raises(ValidationError):
        MMConfig(devices=[{"label": "Core", "library": "DemoCamera", "name": "DCam"}])

    with pytest.raises(ValidationError):
        MMConfig(devices=[{"label": "core", "library": "DemoCamera", "name": "DCam"}])

    # cannot have a device with empty label
    with pytest.raises(ValidationError):
        MMConfig(
            devices=[
                {"label": "", "library": "DemoCamera", "name": "DCam"},
            ]
        )
    # cannot have a device label with commas
    with pytest.raises(ValidationError):
        MMConfig(
            devices=[
                {"label": "My,Device", "library": "DemoCamera", "name": "DCam"},
            ]
        )
