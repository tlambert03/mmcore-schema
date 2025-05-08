"""Schema for Micro-Manager configuration files."""

from collections.abc import Iterable
from typing import Annotated, Any, ClassVar, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

SCHEMA_URL_BASE = "https://micro-manager.org"


class _Base(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid", coerce_numbers_to_str=True
    )


class PropertyValue(_Base):
    """A value associated with a property.

    Note that `device_label` is not specified here, as this object is always a member
    of a properties list on a specific device.
    """

    property: str = Field(
        default=...,
        description="The name of the property to set on the device",
    )
    value: str = Field(
        default=...,
        description="The value to set for the property on the device",
    )

    @model_validator(mode="before")
    @classmethod
    def _cast_sequence(cls, value: Any) -> Any:
        """Allow a sequence of 2 items to be passed as (property, value)."""
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return {"property": value[0], "value": value[1]}
        return value


DeviceLabel = Annotated[
    str,
    Field(
        description=(
            "The user-determined label to assign to the device."
            "Must have at least one character, no commas, and cannot be 'Core'."
        ),
        pattern="^[^,]+$",
        min_length=1,
        json_schema_extra={"not": {"pattern": "^(?i)core$"}},
    ),
]


class Device(_Base):
    """A device to load from a library."""

    label: DeviceLabel

    library: str = Field(
        default=...,
        description="The adapter library that provides the device.",
    )
    name: str = Field(
        default=...,
        description="The name of the device to load from the library",
    )

    pre_init_properties: list[PropertyValue] = Field(
        default_factory=list,
        description=(
            "List of properties to set on the device before device initialization. "
            "Properties will be set in the order they are listed."
        ),
    )
    post_init_properties: list[PropertyValue] = Field(
        default_factory=list,
        description=(
            "List of properties to set on the device after device initialization. "
            "Properties will be set in the order they are listed."
        ),
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

    @model_validator(mode="before")
    @classmethod
    def _cast_sequence(cls, value: Any) -> Any:
        """Allow a sequence of 3 items to be passed as (label, library, name)."""
        if isinstance(value, (list, tuple)) and len(value) == 3:
            return {"label": value[0], "library": value[1], "name": value[2]}
        return value

    @field_validator("label", mode="after")
    def _check_label(cls, v: str) -> str:
        if v.lower() == "core":
            raise ValueError(
                "The label 'Core' is reserved for the Micro-Manager core device."
            )
        return v

    def __repr_args__(self) -> Iterable[tuple[str | None, Any]]:
        """Only include set fields in the repr."""
        # only include set fields in the repr
        for field, val in super().__repr_args__():
            if field in self.model_fields_set:
                yield field, val


class CoreDevice(_Base):
    """Special device representing the Micro-Manager core."""

    label: Literal["Core"] = Field(
        default=...,
        description=("Label MUST be 'Core', and must be provided."),
        repr=False,
    )


class PropertySetting(_Base):
    """A single device property setting."""

    device_label: str = Field(
        default=...,
        description="The label of the device to set the configuration on",
    )
    property: str = Field(
        default=...,
        description="The name of the property to set on the device",
    )
    value: str = Field(
        default=...,
        description="The value to set for the property on the device",
    )

    @model_validator(mode="before")
    @classmethod
    def _cast_sequence(cls, value: Any) -> Any:
        """Allow a sequence of 3 items to be passed as (dev_label, prop_name, value)."""
        if isinstance(value, (list, tuple)) and len(value) == 3:
            return {
                "device_label": value[0],
                "property": value[1],
                "value": value[2],
            }
        return value


class Configuration(_Base):
    """A group of device property settings."""

    name: str = Field(
        default=...,
        description="A name for this configuration. ",
    )
    settings: list[PropertySetting] = Field(
        default_factory=list,
        description=(
            "List of settings to apply to the configuration. "
            "Settings will be applied in the order they are listed."
        ),
    )


class ConfigGroup(_Base):
    """A group of configuration presets."""

    name: str = Field(
        default=...,
        description="The name of the configuration group.",
    )
    configurations: list[Configuration] = Field(
        default_factory=list, description=("Configuration settings for the group. ")
    )


class PixelSizeConfiguration(Configuration):
    """Configuration of a pixel size."""

    pixel_size_um: float = Field(
        default=...,
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


class MMConfigFile(_Base):
    """Micro-Manager configuration file schema."""

    # ----------------------  FIELDS  ----------------------

    schema_version: Literal["1.0"] = Field(
        default="1.0",
        description=(
            "The version of the schema used to create this file. "
            "This is used to determine how to parse the file."
        ),
    )
    devices: list[Device | CoreDevice] = Field(
        default_factory=list,
        description=(
            "List of devices to load. "
            "Devices will be loaded in the order they are listed."
        ),
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

    # ----------------------  MODEL_CONFIG  ----------------------

    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "additionalProperties": False,
            "$id": f"{SCHEMA_URL_BASE}/schemas/mmconfig/1.0/mmconfig.schema.json",
        },
    )

    def model_post_init(self, context: Any) -> None:
        """Called after the model is initialized."""
        # always consider the schema version to be set,
        # so it will be included in the model_dump even with exclude_unset=True
        self.model_fields_set.add("schema_version")
