from rich import print

from mmcore_schema import MMConfigFile


def test_something() -> None:
    cfg = MMConfigFile(
        devices=[
            {"label": "MyDevice", "library": "DemoCamera", "name": "DCam"},
            ("A", "B", "C"),
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
                            ("Camera", "Binning", 2),
                        ],
                    }
                ],
            }
        ],
    )

    print(cfg)
    print(cfg.model_dump(exclude_unset=True))
