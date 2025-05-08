"""Utility functions for loading system configuration into pymmcore."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pymmcore

from .mmconfig import CoreDevice

if TYPE_CHECKING:
    from mmcore_schema.mmconfig import MMConfig


def load_system_configuration(core: pymmcore.CMMCore, config: MMConfig) -> None:
    """Load system configuration from a MMConfigFile object."""
    core.unloadAllDevices()

    # 1. Load devices & their per-device settings (delay, focus, state labels)
    for dev in config.devices:
        if not isinstance(dev, CoreDevice):
            core.loadDevice(dev.label, dev.library, dev.name)
            for prop in dev.pre_init_properties:
                core.setProperty(dev.label, prop.property, prop.value)

    # 2. Initialize all devices (if your API needs an explicit init step)
    core.initializeAllDevices()

    # 3. Post-init property settings
    for dev in config.devices:
        if isinstance(dev, CoreDevice):
            for prop in dev.properties:
                match prop:
                    case pymmcore.g_Keyword_CoreCamera:
                        core.setCameraDevice(dev.label)
                    case pymmcore.g_Keyword_CoreXYStage:
                        core.setXYStageDevice(dev.label)
                    case pymmcore.g_Keyword_CoreFocus:
                        core.setFocusDevice(dev.label)
                    case pymmcore.g_Keyword_CoreShutter:
                        core.setShutterDevice(dev.label)
                    case pymmcore.g_Keyword_CoreAutoFocus:
                        core.setAutoFocusDevice(dev.label)
                    case pymmcore.g_Keyword_CoreImageProcessor:
                        core.setImageProcessorDevice(dev.label)
                    case pymmcore.g_Keyword_CoreSLM:
                        core.setSLMDevice(dev.label)
                    case pymmcore.g_Keyword_CoreGalvo:
                        core.setGalvoDevice(dev.label)
                    case pymmcore.g_Keyword_CoreChannelGroup:
                        core.setChannelGroup(dev.label)
                    case pymmcore.g_Keyword_CoreAutoShutter:
                        core.setAutoShutter(dev.label)
                    case pymmcore.g_Keyword_CoreTimeoutMs:
                        core.setTimeoutMs(dev.label)

        else:
            for prop in dev.post_init_properties:
                core.setProperty(dev.label, prop.property, prop.value)
            if dev.delay_ms is not None:
                core.setDeviceDelayMs(dev.label, dev.delay_ms)
            if dev.focus_direction is not None:
                core.setFocusDirection(dev.label, dev.focus_direction)
            if dev.state_labels:
                for state, lbl in dev.state_labels.items():
                    core.defineStateLabel(dev.label, int(state), lbl)

    # 4. Configuration groups
    for group in config.configuration_groups:
        for conf in group.configurations:
            for s in conf.settings:
                core.defineConfig(
                    group.name, conf.name, s.device_label, s.property, s.value
                )

    # 5. Pixel-size configurations
    for pix in config.pixel_size_configurations:
        for s in pix.settings:
            core.definePixelSizeConfig(pix.name, s.device_label, s.property, s.value)
        if pix.affine_matrix:
            core.setPixelSizeAffine(pix.name, list(pix.affine_matrix))
        if pix.dxdz is not None:
            core.setPixelSizedxdz(pix.name, pix.dxdz)
        if pix.dydz is not None:
            core.setPixelSizedydz(pix.name, pix.dydz)
        if pix.optimal_z_um is not None:
            core.setPixelSizeOptimalZUm(pix.name, pix.optimal_z_um)

    # 6. Finalize: update channel groups, cache & apply startup config
    if core.isConfigDefined("System", "Startup"):
        core.setConfig("System", "Startup")

    core.waitForSystem()
    core.updateSystemStateCache()
