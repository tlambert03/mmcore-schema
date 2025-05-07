# mmcore-schema

[![License](https://img.shields.io/pypi/l/mmcore-schema.svg?color=green)](https://github.com/tlambert03/mmcore-schema/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mmcore-schema.svg?color=green)](https://pypi.org/project/mmcore-schema)
[![Python Version](https://img.shields.io/pypi/pyversions/mmcore-schema.svg?color=green)](https://python.org)
[![CI](https://github.com/tlambert03/mmcore-schema/actions/workflows/ci.yml/badge.svg)](https://github.com/tlambert03/mmcore-schema/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tlambert03/mmcore-schema/branch/main/graph/badge.svg)](https://codecov.io/gh/tlambert03/mmcore-schema)

Proposed schema for the [Micro-Manager](https://micro-manager.org/) configuration file format.

## Schema

This library declares a proposed JSON schema for the Micro-Manager configuration file format.
(Note, the actual file could be written in YAML, JSON, or any structured text format,
but the schema is defined in JSON.)

See [JSON Schema here](/schemas/mmconfig/1.0/mmconfig.schema.json) for the current schema.

## Pseudo-code

Loading the config file would look something like this.

The below example is written in Python, but it is assumed that C++
code and/or Java code would also have the ability to load a config file
and call the same methods.

```python
import json

from pydantic import ValidationError
from pymmcore import CMMCore

from mmcore_schema import MMConfigFile


def load_system_configuration(core: CMMCore, filename: str) -> None:
    """Load system configuration from a JSON/YAML file using the new MMConfig schema."""
    data = json.loads(filename)  # or pyyaml.load(filename)

    try:
        cfg = MMConfigFile.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Invalid configuration file {filename}:\n{e}") from e

    core.unloadAllDevices()
    
    # 2. Load devices & their per-device settings (delay, focus, state labels)
    for dev in cfg.devices:
        core.loadDevice(dev.label, dev.library, dev.name)

    # 3. Pre-init property settings
    for prop in cfg.pre_init_properties:
        core.setProperty(prop.device_label, prop.property_name, prop.value)

    # 4. Initialize all devices (if your API needs an explicit init step)
    core.initializeAllDevices()

    # 5. Post-init property settings
    for prop in cfg.post_init_properties:
        core.setProperty(prop.device_label, prop.property_name, prop.value)

    for dev in cfg.devices:
        if dev.delay_ms is not None:
            core.setDeviceDelayMs(dev.label, dev.delay_ms)
        if dev.focus_direction is not None:
            core.setFocusDirection(dev.label, dev.focus_direction)
        if dev.state_labels:
            for state, lbl in dev.state_labels.items():
                core.defineStateLabel(dev.label, state, lbl)


    # 6. Core properties
    cp = cfg.core_properties
    if cp.camera_device:
        core.setCameraDevice(cp.camera_device)
    if cp.xy_stage_device:
        core.setXYStageDevice(cp.xy_stage_device)
    if cp.focus_device:
        core.setFocusDevice(cp.focus_device)
    if cp.auto_focus_device:
        core.setAutoFocusDevice(cp.auto_focus_device)
    if cp.shutter_device:
        core.setShutterDevice(cp.shutter_device)
    if cp.image_processor_device:
        core.setImageProcessorDevice(cp.image_processor_device)
    if cp.slm_device:
        core.setSLMDevice(cp.slm_device)
    if cp.galvo_device:
        core.setGalvoDevice(cp.galvo_device)
    if cp.channel_group:
        core.setChannelGroup(cp.channel_group)
    if cp.auto_shutter is not None:
        core.setAutoShutter(cp.auto_shutter)
    if cp.timeout_ms is not None:
        core.setTimeoutMs(cp.timeout_ms)

    # 7. Configuration groups
    for group in cfg.configuration_groups:
        for conf in group.configurations:
            for s in conf.settings:
                core.defineConfig(
                    group.name,
                    conf.name,
                    s.device_label,
                    s.property_name,
                    s.value
                )

    # 8. Pixel-size configurations
    for pix in cfg.pixel_size_configurations:
        for s in pix.settings:
            core.definePixelSizeConfig(
                pix.name,
                s.device_label,
                s.property_name,
                s.value
            )
        if pix.affine_matrix:
            core.setPixelSizeAffine(pix.name, list(pix.affine_matrix))
        if pix.dxdz is not None:
            core.setPixelSizedxdz(pix.name, pix.dxdz)
        if pix.dydz is not None:
            core.setPixelSizedydz(pix.name, pix.dydz)
        if pix.optimal_z_um is not None:
            core.setPixelSizeOptimalZUm(pix.name, pix.optimal_z_um)

    # 10. Finalize: update channel groups, cache & apply startup config
    if core.isConfigDefined("System", "Startup"):
        core.setConfig("System", "Startup")

    core.waitForSystem()
    core.updateSystemStateCache()
```
