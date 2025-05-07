from typing import Literal

from pydantic import BaseModel, Field


class Device(BaseModel):
    label: str = Field(
        ...,
        description="The user-determined label to assign to the device",
    )
    library: str = Field(
        ...,
        description="The adapter library that provides the device.",
    )
    name: str = Field(
        ...,
        description="The name of the device to load from the library",
    )

    delay_ms: float | None = Field(
        default=None,
        description=(
            "Delay, in milliseconds, for device acitons. "
            "(note: Some devices ignore this setting.)"
        ),
    )
    focus_direction: Literal[-1, 0, 1] | None = Field(
        default=None,
        description=(
            "Focus direction (only applicable for Stage Devices, ignored otherwise). "
            "-1 = increasing position moves objective away from sample. "
            " 0 | None = unknown. "
            " 1 = increasing position moves objective towards sample. "
        ),
    )
    state_labels: dict[int, str] | None = Field(
        default=None,
        description=(
            "A dictionary mapping state numbers to labels (only applicable for State "
            "Devices, ignored otherwise). "
            "Provides a human-readable label for each state of the device."
        ),
    )


class DeviceProperty(BaseModel):
    device_label: str = Field(
        ...,
        description="The label of the device to set the property on",
    )
    property_name: str = Field(
        ...,
        description="The name of the property to set on the device",
    )
    value: str = Field(
        ...,
        description="The value to set for the property on the device",
    )


class CoreProperties(BaseModel):
    camera_device: str | None = Field(
        default=None,
        description=("The label of the device to use as the camera."),
    )
    xy_stage_device: str | None = Field(
        default=None,
        description=("The label of the device to use as the XY stage."),
    )
    focus_device: str | None = Field(
        default=None,
        description=("The label of the device to use as the focus device."),
    )
    auto_focus_device: str | None = Field(
        default=None,
        description=("The label of the device to use as the auto focus device."),
    )
    shutter_device: str | None = Field(
        default=None,
        description=("The label of the device to use as the shutter device."),
    )
    image_processor_device: str | None = Field(
        default=None,
        description=("The label of the device to use as the image processor device."),
    )
    slm_device: str | None = Field(
        default=None,
        description=("The label of the device to use as the SLM device."),
    )
    galvo_device: str | None = Field(
        default=None,
        description=("The label of the device to use as the galvo device."),
    )
    channel_group: str | None = Field(
        default=None,
        description=(
            "Name of the configuration group that contains optical configuration "
            "(i.e. channel group) settings."
        ),
    )
    auto_shutter: bool | None = Field(
        default=None,
        description=("Whether to enable the auto shutter feature."),
    )
    timeout_ms: int | None = Field(
        default=None,
        description=("Default timeout for device actions, in milliseconds."),
    )


class PropertySetting(BaseModel):
    """A single device property setting."""

    device_label: str = Field(
        ...,
        description="The label of the device to set the configuration on",
    )
    property_name: str = Field(
        ...,
        description="The name of the property to set on the device",
    )
    value: str = Field(
        ...,
        description="The value to set for the property on the device",
    )


class Configuration(BaseModel):
    """A group of device property settings."""

    name: str = Field(
        ...,
        description="A name for this configuration. ",
    )
    settings: list[PropertySetting] = Field(
        default_factory=list,
        description=(
            "List of settings to apply to the configuration. "
            "Settings will be applied in the order they are listed."
        ),
    )


class ConfigGroup(BaseModel):
    """A group of configuration presets."""

    name: str = Field(
        ...,
        description="The name of the configuration group.",
    )
    configurations: list[Configuration] = Field(
        default_factory=list, description=("Configuration settings for the group. ")
    )


class PixelSizeConfiguration(Configuration):
    """Configuration of a pixel size."""

    pixel_size_um: float = Field(
        ...,
        description=(
            "Pixel size in micrometers. "
            "This is the size of a pixel in the image sensor of the camera."
        ),
    )
    affine_matrix: tuple[float, float, float, float, float, float] | None = Field(
        default=None,
        description=(
            "Affine transformation matrix to apply to the configuration group. "
            "This is a 2x3 matrix represented as a tuple of 6 floats."
        ),
    )
    dxdz: float | None = Field(
        default=None,
        description=(
            "The angle between the camera's x axis and the axis (direction)"
            "of the z drive for the given pixel size configuration. This angle is"
            "dimensionless (i.e. the ratio of the translation in x caused by a "
            "translation in z, i.e. dx / dz)."
        ),
    )
    dydz: float | None = Field(
        default=None,
        description=(
            "The angle between the camera's y axis and the axis (direction)"
            "of the z drive for the given pixel size configuration. This angle is"
            "dimensionless (i.e. the ratio of the translation in y caused by a "
            "translation in z, i.e. dy / dz)."
        ),
    )
    optimal_z_um: float | None = Field(
        default=None,
        description=(
            "User-defined 'optimal' z step size for this pixel size configuration."
        ),
    )


class MMConfigFile(BaseModel):
    devices: list[Device] = Field(
        default_factory=list,
        description=(
            "List of devices to load. "
            "Devices will be loaded in the order they are listed."
        ),
    )
    pre_init_properties: list[DeviceProperty] = Field(
        default_factory=list,
        description=(
            "List of properties to set on devices before device initialization. "
            "Properties will be set in the order they are listed."
        ),
    )
    post_init_properties: list[DeviceProperty] = Field(
        default_factory=list,
        description=(
            "List of properties to set on devices after device initialization. "
            "Properties will be set in the order they are listed."
        ),
    )
    core_properties: CoreProperties = Field(
        default_factory=CoreProperties,
        description=("Default properties to set on the Micro-Manager core."),
    )
    configuration_groups: list[ConfigGroup] = Field(
        default_factory=list,
        description=("Configuration groups to create."),
    )
    pixel_size_configurations: list[PixelSizeConfiguration] = Field(
        default_factory=list,
        description=(
            "Pixel size configurations to create. "
            "These configurations will be used to set the pixel size of the camera."
        ),
    )

    extra: dict = Field(
        default_factory=dict,
        description=("User-defined extra properties. Not used by Micro-Manager."),
    )
