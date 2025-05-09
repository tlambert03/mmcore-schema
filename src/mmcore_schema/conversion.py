"""Utility functions for converting between config file formats."""

from __future__ import annotations

import warnings
from copy import deepcopy
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from .mmconfig import (
    ConfigGroup,
    Configuration,
    Device,
    MMConfig,
    PixelSizeConfiguration,
    PropertySetting,
    PropertyValue,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from typing_extensions import Unpack

    from .mmconfig import DumpKwargs


__all__ = ["convert_file", "read_mm_cfg_file"]


def convert_file(
    input: str | Path,
    output: str | Path,
    *,
    indent: int | None = None,
    **dump_kwargs: Unpack[DumpKwargs],
) -> None:
    """Convert a Micro-Manager config from one format to another."""
    mm_config = MMConfig.from_file(input)
    mm_config.write_file(output, indent=indent, **dump_kwargs)


DELIM = ","
CORE = "Core"


class CfgCmd(str, Enum):
    """Enum for configuration commands."""

    ConfigGroup = "ConfigGroup"
    ConfigPixelSize = "ConfigPixelSize"
    Configuration = "Config"
    Delay = "Delay"
    Device = "Device"
    FocusDirection = "FocusDirection"
    Label = "Label"
    Parent = "Parent"
    PixelSize_um = "PixelSize_um"
    PixelSizeAffine = "PixelSizeAffine"
    PixelSizeAngle_dxdz = "PixelSizeAngle_dxdz"
    PixelSizeAngle_dydz = "PixelSizeAngle_dydz"
    PixelSizeOptimalZ_Um = "PixelSizeOptimalZ_Um"
    Property = "Property"

    def __str__(self) -> str:
        """Return the string representation of the command."""
        return self.value


def read_mm_cfg_file(file_path: str | Path) -> MMConfig:
    """Read a legacy Micro-Manager config file into a MMConfigFile object.

    Parameters
    ----------
    file_path : Union[str, Path]
        Path to the configuration file
    """
    # Track if we've passed the initialize line
    passed_init = False

    # Dictionary to map device labels to Device objects
    devices: dict[str, Device] = {}
    config_groups: dict[str, ConfigGroup] = {}
    pixel_size_configs: dict[str, PixelSizeConfiguration] = {}
    core_properties: list[PropertySetting] = []

    # Read file line by line
    for line in _iter_lines(file_path):
        # Split the line by commas
        # mimics the C++ CDeviceUtils::Tokenize function, which skips empty tokens
        cmd, *tokens = [t for t in line.split(DELIM) if t]

        # Process the command
        match cmd:
            # for ease of comparison, these cases are in the same order as in
            # CMMCore::loadSystemConfigurationImpl()
            case CfgCmd.Device:
                if len(tokens) != 3:
                    raise _invalid_line_error(line, 3, len(tokens))
                device = Device.model_validate(tokens)
                if device.label in devices:
                    warnings.warn(
                        f"Device {device.label} already exists. Skipping.",
                        stacklevel=2,
                    )
                    continue
                devices[device.label] = device

            case CfgCmd.Property:
                # Property,<device>,<property>,<value>
                if len(tokens) == 2:
                    dev_label, prop = tokens
                    value = ""
                elif len(tokens) == 3:
                    dev_label, prop, value = tokens
                else:
                    raise _invalid_line_error(line, {2, 3}, len(tokens))
                # Check if this is the special initialize line
                if dev_label == CORE:
                    if prop == "Initialize" and passed_init is False:
                        passed_init = bool(value == "1")
                    else:
                        core_properties.append(
                            PropertySetting(
                                device_label=CORE, property=prop, value=value
                            )
                        )
                else:
                    device = _ensure_device(dev_label, devices)
                    prop_value = PropertyValue(property=prop, value=value)
                    if passed_init:
                        device.post_init_properties.append(prop_value)
                    else:
                        device.pre_init_properties.append(prop_value)

            case CfgCmd.Delay:
                if len(tokens) != 2:
                    raise _invalid_line_error(line, 2, len(tokens))
                dev_label, delay = tokens
                device = _ensure_device(dev_label, devices)
                device.delay_ms = int(delay)

            case CfgCmd.FocusDirection:
                if len(tokens) != 2:
                    raise _invalid_line_error(line, 2, len(tokens))
                dev_label, direction = tokens
                device = _ensure_device(dev_label, devices)
                device.focus_direction = int(direction)  # type: ignore[assignment]

            case CfgCmd.Label:
                if len(tokens) != 3:
                    raise _invalid_line_error(line, 3, len(tokens))
                dev_label, state, state_label = tokens
                device = _ensure_device(dev_label, devices)
                if state in device.state_labels:
                    warnings.warn(
                        f"Label {state} already exists for device {dev_label}.",
                        stacklevel=2,
                    )
                device.state_labels[state] = state_label

            case "Config":
                warnings.warn(
                    "Obsolete command 'Config' ignored in configuration file. ",
                    stacklevel=2,
                )

            case CfgCmd.ConfigGroup:
                if len(tokens) == 1:
                    grp_name = tokens[0]
                    config_groups.setdefault(grp_name, ConfigGroup(name=grp_name))
                    continue

                if len(tokens) == 4:
                    grp_name, cfg_name, dev_label, prop = tokens
                    value = ""
                elif len(tokens) == 5:
                    grp_name, cfg_name, dev_label, prop, value = tokens
                else:
                    raise _invalid_line_error(line, {1, 4, 5}, len(tokens))
                grp = config_groups.setdefault(grp_name, ConfigGroup(name=grp_name))
                for cfg in grp.configurations:
                    if cfg.name == cfg_name:
                        break
                else:
                    cfg = Configuration(name=cfg_name, settings=[])
                    grp.configurations.append(cfg)

                cfg.settings.append(
                    PropertySetting(device_label=dev_label, property=prop, value=value)
                )

            case CfgCmd.ConfigPixelSize:
                if len(tokens) != 4:
                    raise _invalid_line_error(line, 4, len(tokens))

                res_id, dev_label, prop, value = tokens

                cfg = pixel_size_configs.setdefault(
                    res_id, PixelSizeConfiguration(name=res_id)
                )
                s = PropertySetting(device_label=dev_label, property=prop, value=value)
                cfg.settings.append(s)

            case CfgCmd.PixelSize_um:
                if len(tokens) != 2:
                    raise _invalid_line_error(line, 2, len(tokens))
                res_id, pixel_size = tokens
                cfg = _ensure_pixel_size_config(res_id, pixel_size_configs)
                cfg.pixel_size_um = float(pixel_size)

            case CfgCmd.PixelSizeAffine:
                if len(tokens) != 7:
                    raise _invalid_line_error(line, 7, len(tokens))
                res_id, *matrix = tokens
                cfg = _ensure_pixel_size_config(res_id, pixel_size_configs)
                cfg.affine_matrix = tuple(float(m) for m in matrix)  # type: ignore[assignment]

            case CfgCmd.PixelSizeAngle_dxdz:
                if len(tokens) != 2:
                    raise _invalid_line_error(line, 2, len(tokens))
                res_id, value = tokens
                cfg = _ensure_pixel_size_config(res_id, pixel_size_configs)
                cfg.dxdz = float(value)

            case CfgCmd.PixelSizeAngle_dydz:
                if len(tokens) != 2:
                    raise _invalid_line_error(line, 2, len(tokens))
                res_id, value = tokens
                cfg = _ensure_pixel_size_config(res_id, pixel_size_configs)
                cfg.dydz = float(value)

            case CfgCmd.PixelSizeOptimalZ_Um:
                if len(tokens) != 2:
                    raise _invalid_line_error(line, 2, len(tokens))
                res_id, value = tokens
                cfg = _ensure_pixel_size_config(res_id, pixel_size_configs)
                cfg.optimal_z_um = float(value)

            case "Equipment":
                warnings.warn(
                    "Obsolete command 'Equipment' ignored in configuration file. ",
                    stacklevel=2,
                )
            case "ImageSynchro":
                warnings.warn(
                    "Obsolete command 'ImageSynchro' ignored in configuration file. ",
                    stacklevel=2,
                )

            case CfgCmd.Parent:
                if len(tokens) != 2:
                    raise _invalid_line_error(line, 2, len(tokens))
                child, parent = tokens
                parent_device = _ensure_device(parent, devices)
                _ensure_device(child, devices)
                parent_device.children.append(child)

            case default:
                warnings.warn(
                    f"Unknown config command '{default!r}' in line {line!r}. Ignored.",
                    stacklevel=2,
                )

    config = MMConfig(
        devices=list(devices.values()),
        startup_configuration=list(core_properties),
        configuration_groups=list(config_groups.values()),
        pixel_size_configurations=list(pixel_size_configs.values()),
    )
    return config


def iter_mm_cfg_lines(cfg: MMConfig) -> Iterator[str]:
    """Yield lines of a legacy Micro-Manager .cfg from an MMConfig schema."""
    # Header with generation timestamp
    stamp = datetime.now().isoformat(sep=" ", timespec="seconds")
    yield f"# Generated by mmcore-schema on {stamp}"
    yield ""

    # Reset/init marker
    yield "# Reset"
    yield _join(CfgCmd.Property, CORE, "Initialize", "0")
    yield ""

    # Devices
    yield "# Devices"
    for device in cfg.devices:
        yield _join(CfgCmd.Device, device.label, device.library, device.name)
    yield ""

    # Pre-init settings
    yield "# Pre-init settings for devices"
    for device in cfg.devices:
        for prop in device.pre_init_properties:
            yield _join(CfgCmd.Property, device.label, prop.property, prop.value)
    yield ""

    # Parent references
    yield "# Hub (parent) references"
    for device in cfg.devices:
        for child in device.children:
            yield _join(CfgCmd.Parent, child, device.label)
    yield ""

    # Initialization marker for post-init
    yield "# Initialize"
    yield _join(CfgCmd.Property, CORE, "Initialize", "1")
    yield ""

    # Post-init settings
    for device in cfg.devices:
        for prop in device.post_init_properties:
            yield _join(CfgCmd.Property, device.label, prop.property, prop.value)
    yield ""

    # Focus directions
    yield "# Focus directions"
    for device in cfg.devices:
        if device.focus_direction is not None:
            yield _join(CfgCmd.FocusDirection, device.label, device.focus_direction)
    yield ""

    # Core properties
    # ... these seem to be the only "currentX" that are written to a config file
    # (and CMMCore::saveSystemConfiguration does not write AutoShutter)
    ROLE_PROPERTIES = {"Camera", "Shutter", "Focus", "AutoShutter"}
    yield "# Roles"
    for setting in cfg.startup_configuration:
        if setting.device_label == CORE and setting.property in ROLE_PROPERTIES:
            yield _join(CfgCmd.Property, CORE, setting.property, setting.value)
    yield ""

    # State labels
    yield "# Labels"
    for device in cfg.devices:
        if device.state_labels:
            yield f"# {device.label}"
            for state, label in device.state_labels.items():
                yield _join(CfgCmd.Label, device.label, state, label)

    # Configuration groups
    # merge in startup_configuration and shutdown_configuration into the system group
    cfg_groups: dict[str, ConfigGroup] = {
        grp.name: deepcopy(grp) for grp in cfg.configuration_groups
    }

    # first remove the system group, if it exists
    # (this will only be the case if System exists, with something other than
    # startup/shutdown)
    sys_group = cfg_groups.pop("System", ConfigGroup(name="System"))
    if cfg.startup_configuration:
        sys_group.configurations.append(
            Configuration(name="Startup", settings=cfg.startup_configuration)
        )
    if cfg.shutdown_configuration:
        sys_group.configurations.append(
            Configuration(name="Shutdown", settings=cfg.shutdown_configuration)
        )
    merged_groups = list(cfg_groups.values())
    # Add the system group at the end if it has any configurations
    if sys_group.configurations:
        merged_groups.append(sys_group)

    if merged_groups:
        yield ""
        yield "# Configuration groups"
    for group in merged_groups:
        yield ""
        yield f"# Group: {group.name}"
        for config in group.configurations:
            yield f"# Preset: {config.name}"
            for setting in config.settings:
                yield _join(
                    CfgCmd.ConfigGroup,
                    group.name,
                    config.name,
                    setting.device_label,
                    setting.property,
                    setting.value,
                )

    # Pixel size configurations
    for psize in cfg.pixel_size_configurations:
        yield ""
        yield f"# Resolution preset: {psize.name}"
        for setting in psize.settings:
            yield _join(
                CfgCmd.ConfigPixelSize,
                psize.name,
                setting.device_label,
                setting.property,
                setting.value,
            )

        # numeric and matrix settings
        yield _join(CfgCmd.PixelSize_um, psize.name, psize.pixel_size_um)
        if psize.affine_matrix is not None:
            matrix_vals = DELIM.join(str(v) for v in psize.affine_matrix)
            yield _join(CfgCmd.PixelSizeAffine, psize.name, matrix_vals)
        if psize.dxdz is not None:
            yield _join(CfgCmd.PixelSizeAngle_dxdz, psize.name, psize.dxdz)
        if psize.dydz is not None:
            yield _join(CfgCmd.PixelSizeAngle_dydz, psize.name, psize.dydz)
        if psize.optimal_z_um is not None:
            yield _join(CfgCmd.PixelSizeOptimalZ_Um, psize.name, psize.optimal_z_um)


# --------------- helpers -----------------


def _join(*parts: Any) -> str:
    """Join a command and its arguments with DELIM."""
    return DELIM.join(str(p) for p in parts)


def _invalid_line_error(line: str, expected: int | set, actual: int) -> ValueError:
    """Return an error if the line does not match the expected format."""
    return ValueError(
        f"Invalid configuration file line encountered: {line},\n"
        f"Expected {expected} tokens, but got {actual}."
    )


def _ensure_device(name: str, devices: dict[str, Device]) -> Device:
    """Get a device by name or raise an error if not found."""
    if (device := devices.get(name)) is None:
        raise ValueError(f"Device {name!r} not found in configuration file.")
    return device


def _ensure_pixel_size_config(
    name: str, pixel_size_configs: dict[str, PixelSizeConfiguration]
) -> PixelSizeConfiguration:
    """Get a pixel size configuration by name or raise an error if not found."""
    if (cfg := pixel_size_configs.get(name)) is None:
        raise ValueError(
            f"Pixel size configuration {name!r} not found in configuration file."
        )
    return cfg


def _iter_lines(file_path: str | Path) -> Iterator[str]:
    """Iterate over lines in a file, stripping whitespace and skipping comments."""
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            yield line
