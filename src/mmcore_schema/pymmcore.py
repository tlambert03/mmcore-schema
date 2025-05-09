"""Utility functions for loading system configuration into pymmcore."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Container, Iterator, Sequence
    from typing import Protocol

    from mmcore_schema.mmconfig import MMConfig

    # defining a protocol, so as to support pymmcore-nano as well as pymmcore
    class _CoreProtocol(Protocol):
        def isGroupDefined(self, group: str, /) -> bool: ...
        def defineConfigGroup(self, group: str, /) -> None: ...
        def defineConfig(
            self, group: str, config: str, device: str, prop: str, value: str
        ) -> None: ...
        def definePixelSizeConfig(
            self, key: str, device: str, prop: str, value: str
        ) -> None: ...
        def defineStateLabel(self, device: str, state: int, label: str, /) -> None: ...
        def initializeAllDevices(self, /) -> None: ...
        def isFeatureEnabled(self, feature: str, /) -> bool: ...
        def enableFeature(self, feature: str, enabled: bool, /) -> None: ...
        def isConfigDefined(self, group: str, config: str, /) -> bool: ...
        def loadDevice(self, label: str, library: str, name: str, /) -> None: ...
        def setAutoFocusDevice(self, device: str, /) -> None: ...
        def setAutoShutter(self, state: bool, /) -> None: ...
        def setCameraDevice(self, device: str, /) -> None: ...
        def setChannelGroup(self, device: str, /) -> None: ...
        def setConfig(self, group: str, config: str, /) -> None: ...
        def setDeviceDelayMs(self, device: str, value: float, /) -> None: ...
        def setFocusDevice(self, device: str, /) -> None: ...
        def setFocusDirection(self, device: str, value: int, /) -> None: ...
        def setGalvoDevice(self, device: str, /) -> None: ...
        def setImageProcessorDevice(self, device: str, /) -> None: ...
        def setPixelSizeUm(self, device: str, value: float, /) -> None: ...
        def setPixelSizeAffine(
            self, device: str, matrix: Sequence[float], /
        ) -> None: ...
        def setPixelSizedxdz(self, key: str, value: float, /) -> None: ...
        def setPixelSizedydz(self, key: str, value: float, /) -> None: ...
        def setPixelSizeOptimalZUm(self, key: str, value: float, /) -> None: ...
        def setProperty(
            self, label: str, propName: str, propValue: bool | float | int | str, /
        ) -> None: ...
        def setShutterDevice(self, device: str, /) -> None: ...
        def setSLMDevice(self, device: str, /) -> None: ...
        def setTimeoutMs(self, timeout: int, /) -> None: ...
        def setXYStageDevice(self, device: str, /) -> None: ...
        def unloadAllDevices(self, /) -> None: ...
        def updateSystemStateCache(self, /) -> None: ...
        def waitForSystem(self, /) -> None: ...


@contextmanager
def _parallel_init_enabled(core: _CoreProtocol, enable: bool | None) -> Iterator[None]:
    """Context manager to enable or disable parallel device initialization.

    Restores the previous state of the feature after exiting the context.

    Parameters
    ----------
    core : CMMCore | CMMCorePlus
        The core object to set the feature on.
    enable : bool | None
        If True, enables parallel device initialization.
        If False, disables it.
        If None, does nothing.
    """
    if enable is None:
        yield
        return

    before = core.isFeatureEnabled("ParallelDeviceInitialization")
    core.enableFeature("ParallelDeviceInitialization", enable)
    try:
        yield
    finally:
        # Restore the previous state of the feature
        core.enableFeature("ParallelDeviceInitialization", before)


def load_system_configuration(
    core: _CoreProtocol, config: MMConfig, *, exclude_devices: Container[str] = ()
) -> None:
    """Load system configuration from a MMConfigFile object.

    Parameters
    ----------
    core : CMMCore | CMMCorePlus
        The core object to load the configuration into.
    config : MMConfig
        The configuration object to load.
    exclude_devices : Container[str], optional
        A list of device labels to exclude from loading, usually for testing or
        for missing devices. By default, no devices are excluded.
    """
    core.unloadAllDevices()

    # 1. Load devices & their per-device settings (delay, focus, state labels)
    for dev in config.devices:
        core.loadDevice(dev.label, dev.library, dev.name)
        for prop in dev.pre_init_properties:
            core.setProperty(dev.label, prop.property, prop.value)

    # 2. Initialize all devices
    with _parallel_init_enabled(core, config.enable_parallel_device_initialization):
        core.initializeAllDevices()

    # 3. Post-init property settings
    for dev in config.devices:
        if dev.label not in exclude_devices:
            for prop in dev.post_init_properties:
                core.setProperty(dev.label, prop.property, prop.value)
            if dev.delay_ms is not None:
                core.setDeviceDelayMs(dev.label, dev.delay_ms)
            if dev.focus_direction is not None:
                core.setFocusDirection(dev.label, dev.focus_direction)
            if dev.state_labels:
                for state, lbl in dev.state_labels.items():
                    core.defineStateLabel(dev.label, int(state), lbl)

        # if isinstance(dev, CoreDevice):
        #     method_map: Mapping[str, Callable[[str], Any]] = {
        #         "Camera": core.setCameraDevice,
        #         "XYStage": core.setXYStageDevice,
        #         "Focus": core.setFocusDevice,
        #         "Shutter": core.setShutterDevice,
        #         "AutoFocus": core.setAutoFocusDevice,
        #         "ImageProcessor": core.setImageProcessorDevice,
        #         "SLM": core.setSLMDevice,
        #         "Galvo": core.setGalvoDevice,
        #         "ChannelGroup": core.setChannelGroup,
        #     }
        #     for prop in dev.properties:
        #         prop_name = prop.property
        #         if prop_name == "TimeoutMs":
        #             core.setTimeoutMs(int(prop.value))
        #         if prop_name == "AutoShutter":
        #             core.setAutoShutter(bool(prop.value))
        #         elif method := method_map.get(prop_name):
        #             method(prop.value)

    # 4. Configuration groups
    # Special case: "System" Configuration group
    if startup := config.startup_configuration:
        if not core.isGroupDefined("System"):
            core.defineConfigGroup("System")
        for s in startup:
            if s.device not in exclude_devices:
                core.defineConfig("System", "Startup", s.device, s.property, s.value)
    if shutdown := config.shutdown_configuration:
        if not core.isGroupDefined("System"):
            core.defineConfigGroup("System")
        for s in shutdown:
            if s.device not in exclude_devices:
                core.defineConfig("System", "Shutdown", s.device, s.property, s.value)

    for group in config.configuration_groups:
        # this line is actually needed when using pure pymmcore
        # to trigger `updateAllowedChannelGroups`.
        if not core.isGroupDefined(group.name):
            core.defineConfigGroup(group.name)

        for conf in group.configurations:
            for s in conf.settings:
                if s.device not in exclude_devices:
                    core.defineConfig(
                        group.name, conf.name, s.device, s.property, s.value
                    )

    # 5. Pixel-size configurations
    for pix in config.pixel_size_configurations:
        for s in pix.settings:
            if s.device not in exclude_devices:
                core.definePixelSizeConfig(pix.name, s.device, s.property, s.value)
        if pix.pixel_size_um is not None:
            core.setPixelSizeUm(pix.name, pix.pixel_size_um)
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

    # CMMCore::loadSystemConfigurationImpl would emit
    # externalCallback_->onSystemConfigurationLoaded() at this point.
    # we can't do that with pymmcore[-nano] since it's not a public API.
    # but we can emit the event if the core is a CMMCorePlus instance.
    if pymmcore_plus := sys.modules.get("pymmcore_plus"):
        if TYPE_CHECKING:
            from pymmcore_plus import CMMCorePlus
        else:
            CMMCorePlus = getattr(pymmcore_plus, "CMMCorePlus", type(None))
        if isinstance(core, CMMCorePlus):
            core.events.systemConfigurationLoaded.emit()
