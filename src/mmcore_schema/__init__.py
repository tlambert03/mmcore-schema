"""Schema for mmCoreAndDevices."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mmcore-schema")
except PackageNotFoundError:
    __version__ = "uninstalled"


from .mmconfig import (
    SCHEMA_URL_BASE,
    ConfigGroup,
    Configuration,
    Device,
    MMConfigFile,
    PixelSizeConfiguration,
    PropertySetting,
    PropertyValue,
)

__all__ = [
    "SCHEMA_URL_BASE",
    "ConfigGroup",
    "Configuration",
    "Device",
    "MMConfigFile",
    "PixelSizeConfiguration",
    "PropertySetting",
    "PropertyValue",
    "__version__",
    "print_schema",
]


def print_schema() -> None:
    """Print the schema for mmCoreAndDevices to stdout."""
    import json

    print(json.dumps(MMConfigFile.model_json_schema(), indent=2))
