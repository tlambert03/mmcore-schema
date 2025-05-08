"""Schema for mmCoreAndDevices."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mmcore-schema")
except PackageNotFoundError:
    __version__ = "uninstalled"


from .conversion import convert_file
from .mmconfig import (
    SCHEMA_URL_BASE,
    ConfigGroup,
    Configuration,
    Device,
    MMConfig,
    PixelSizeConfiguration,
    PropertySetting,
    PropertyValue,
)

__all__ = [
    "SCHEMA_URL_BASE",
    "ConfigGroup",
    "Configuration",
    "Device",
    "MMConfig",
    "PixelSizeConfiguration",
    "PropertySetting",
    "PropertyValue",
    "__version__",
    "convert_file",
]
