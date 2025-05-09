import pytest
from pydantic import ValidationError

from mmcore_schema import MMConfig


def test_config() -> None:
    cfg = MMConfig(
        devices=[
            {"label": "MyDevice", "library": "DemoCamera", "name": "DCam"},
            ("Dev", "Lib", "Name"),  # this is allowed
            {"label": "Core"},
        ],
        configuration_groups=[
            {
                "name": "Default",
                "configurations": [
                    {
                        "name": "Default",
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

    for mode in ("python", "json"):
        dumped = cfg.model_dump(exclude_unset=True, mode=mode)
        assert "schema_version" in dumped


def test_config_errors() -> None:
    # You can have a single label field, but only if it is "Core"
    MMConfig(devices=[{"label": "Core"}])
    with pytest.raises(ValidationError):
        MMConfig(devices=[{"label": "AnythingButCore"}])

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
