"""Schema for Micro-Manager configuration files."""

from collections.abc import Container
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Callable, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from pydantic.main import IncEx
    from typing_extensions import Self, TypedDict, Unpack

    from .pymmcore import _CoreProtocol

    class DumpKwargs(TypedDict, total=False):
        """Keyword arguments for model_dump_json/yaml."""

        include: IncEx | None
        exclude: IncEx | None
        context: Any | None
        by_alias: bool | None
        exclude_unset: bool
        exclude_defaults: bool
        exclude_none: bool
        round_trip: bool
        warnings: bool | Literal["none", "warn", "error"]
        fallback: Callable[[Any], Any] | None
        serialize_as_any: bool


SCHEMA_URL_BASE = "https://micro-manager.org"


class _BaseModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        extra="forbid", coerce_numbers_to_str=True
    )


class PropertyValue(_BaseModel):
    """A value associated with a property.

    Note that `device` is not specified here, as this object is always a member
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
            "A user-determined label, assigned when loading a device."
            "Must have at least one character, no commas, and cannot be 'Core'."
        ),
        pattern="^[^,]+$",
        min_length=1,
        json_schema_extra={"not": {"pattern": "^(?i)core$"}},
    ),
]


class Device(_BaseModel):
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
    state_labels: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "A dictionary mapping state numbers to labels (only applicable for State "
            "Devices, ignored otherwise). Provides a human-readable label for each "
            "state of the device.  NOTE: Keys are integers, but are stored as strings "
            "in the JSON file.  This is a workaround for the fact that JSON does not "
            "support integer keys in dictionaries."
        ),
    )
    children: list[DeviceLabel] = Field(
        default_factory=list,
        description=("List of child device labels (only applicable for Hub Devices)."),
    )

    model_config: ClassVar[ConfigDict] = ConfigDict(
        json_schema_extra={
            "additionalProperties": False,
            "not": {
                "anyOf": [
                    {"required": ["focus_direction", "state_labels"]},
                    {"required": ["focus_direction", "children"]},
                    {"required": ["state_labels", "children"]},
                ]
            },
        },
    )

    @model_validator(mode="before")
    @classmethod
    def _model_validate_before(cls, value: Any) -> Any:
        """Allow a sequence of 3 items to be passed as (label, library, name)."""
        if isinstance(value, (list, tuple)) and len(value) == 3:
            return {"label": value[0], "library": value[1], "name": value[2]}
        return value

    @model_validator(mode="after")
    def _model_validate_after(self) -> "Self":
        """Allow a sequence of 3 items to be passed as (label, library, name)."""
        # ensure that no two mutually exclusive fields are set
        modified = 0
        exclusive_fields = ("focus_direction", "state_labels", "children")
        for field_name in exclusive_fields:
            field = type(self).model_fields[field_name]
            default = field.get_default(call_default_factory=True, validated_data={})
            modified += int(getattr(self, field_name) != default)
        if modified > 1:
            raise ValueError(
                "Only one of the following fields may be set: "
                f"{', '.join(exclusive_fields)}"
            )
        return self

    @field_validator("label", mode="after")
    def _check_label(cls, v: str) -> str:
        if v.lower() == "core":
            raise ValueError(
                "The label 'Core' is reserved for the Micro-Manager Core device."
            )
        return v


class PropertySetting(_BaseModel):
    """A single device property setting."""

    device: str = Field(
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

    def as_tuple(self) -> tuple[str, str, str]:
        """Return the setting as a tuple of (device, property, value)."""
        return self.device, self.property, self.value

    @model_validator(mode="before")
    @classmethod
    def _cast_sequence(cls, value: Any) -> Any:
        """Allow a sequence of 3 items to be passed as (dev_label, prop_name, value)."""
        if isinstance(value, (list, tuple)) and len(value) == 3:
            return {"device": value[0], "property": value[1], "value": value[2]}
        return value


class Configuration(_BaseModel):
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


class ConfigGroup(_BaseModel):
    """A group of configuration presets."""

    name: str = Field(
        default=...,
        description="The name of the configuration group. May NOT be 'System'.",
    )
    configurations: list[Configuration] = Field(
        default_factory=list, description=("Configuration settings for the group. ")
    )

    def get_configuration(self, name: str) -> Configuration | None:
        """Return the configuration with the given name, if it exists."""
        for config in self.configurations:
            if config.name == name:
                return config
        return None


class PixelSizeConfiguration(Configuration):
    """Configuration of a pixel size."""

    pixel_size_um: float = Field(
        default=0.0,
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


class MMConfig(_BaseModel):
    """Micro-Manager configuration file schema."""

    # ----------------------  FIELDS  ----------------------

    schema_version: Literal["1.0"] = Field(
        default=None,  # type: ignore  # (See model_post_init)
        description=(
            "The version of the schema used to create this file. "
            "This is used to determine how to parse the file."
        ),
        init=False,
        frozen=True,
    )
    enable_parallel_device_initialization: bool | None = Field(
        default=None,
        description=(
            "If True, devices will be initialized in parallel. "
            "This is useful for speeding up the initialization of large systems."
            "Note that this may cause issues with some devices that are not "
            "thread-safe. (None implies no decision has been made yet.)"
        ),
    )
    devices: list[Device] = Field(
        default_factory=list,
        description=(
            "List of devices to load. "
            "Devices will be loaded in the order they are listed."
        ),
    )
    startup_configuration: list[PropertySetting] = Field(
        default_factory=list,
        description=(
            "List of properties to set on the device after device initialization. "
            "Properties will be set in the order they are listed."
        ),
    )
    shutdown_configuration: list[PropertySetting] = Field(
        default_factory=list,
        description=(
            "List of properties to set on the device after device initialization. "
            "Properties will be set in the order they are listed."
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

    # -----------------  Special Values and Conveniences  ----------------------

    def get_device(self, label: str) -> Device | None:
        """Return the device with the given label, if it exists."""
        for device in self.devices:
            if device.label == label:
                return device
        return None

    def get_configuration_group(self, name: str) -> ConfigGroup | None:
        """Return the configuration group with the given name, if it exists."""
        for group in self.configuration_groups:
            if group.name == name:
                return group
        return None

    # ----------------------  VALIDATORS  ----------------------

    def model_post_init(self, context: Any) -> None:
        """Called after the model is initialized."""
        # this is a little hack to ensure that schema_version is considered "set"
        # and also considered not the default, so that it is included in the JSON output
        # even when exclude_defaults or exclude_unset are set to True.
        # there might be a better way to do this.
        object.__setattr__(self, "schema_version", "1.0")
        self.model_fields_set.add("schema_version")

    @model_validator(mode="after")
    def _validate_model(self) -> "Self":
        """Perform post-validation checks on the model."""
        # Check for duplicate device labels
        device_names = [d.label for d in self.devices]
        if len(device_names) != len(set(device_names)):
            duplicates = {name for name in device_names if device_names.count(name) > 1}
            raise ValueError(f"Duplicate device labels found: {', '.join(duplicates)}")

        # move System/Start and System/Shutdown from configuration_groups
        # to startup_configuration and shutdown_configuration
        for group in self.configuration_groups:
            if group.name == "System":
                for config in list(group.configurations):
                    if config.name == "Startup":
                        self.startup_configuration = _merge_settings(
                            self.startup_configuration, config.settings
                        )
                        group.configurations.remove(config)
                    elif config.name == "Shutdown":
                        self.shutdown_configuration = _merge_settings(
                            self.shutdown_configuration, config.settings
                        )
                        group.configurations.remove(config)
                # if we're left with no configurations, remove the group entirely
                if not group.configurations:
                    self.configuration_groups.remove(group)

        return self

    # ----------------------  I/O  ----------------------

    def model_dump_yaml(
        self, *, indent: int | None = None, **dump_kwargs: "Unpack[DumpKwargs]"
    ) -> str:
        """Dump the model to a YAML string."""
        import yaml

        data = self.model_dump(mode="json", **dump_kwargs)
        return yaml.safe_dump(data, indent=indent, sort_keys=False)

    def model_dump_cfg(self) -> str:
        """Dump the model to a legacy Micro-Manager configuration string."""
        from .conversion import iter_mm_cfg_lines

        return "\n".join(iter_mm_cfg_lines(self))

    def write_file(
        self,
        filename: str | Path,
        indent: int | None = None,
        **dump_kwargs: "Unpack[DumpKwargs]",
    ) -> None:
        """Write the configuration to a file.

        Filename extension determines the format:
        - .json: JSON
        - .yaml or .yml: YAML
        - .cfg: Micro-Manager legacy configuration format

        Parameters
        ----------
        filename : str | Path
            The name of the file to write to (see note above: .ext determines format)
        indent : int | None
            The number of spaces to use for indentation (only used for JSON and YAML).
            If None, no indentation is used.
        **dump_kwargs : Unpack[DumpKwargs]
            Additional keyword arguments to pass to the model_dump_json or
            model_dump_yaml methods.
        """
        output = Path(filename)
        if output.suffix == ".json":
            string = self.model_dump_json(indent=indent, **dump_kwargs)
            output.write_text(string)
        elif output.suffix in {".yaml", ".yml"}:
            string = self.model_dump_yaml(indent=indent, **dump_kwargs)
            output.write_text(string)
        elif output.suffix == ".cfg":
            string = self.model_dump_cfg()
            output.write_text(string)
        else:
            raise NotImplementedError(
                f"Unsupported output file format: {output.suffix}"
            )

    @classmethod
    def from_file(cls, filename: str | Path) -> "MMConfig":
        """Load a configuration file from disk.

        File must be in JSON, YAML, or legacy Micro-Manager format.
        """
        fpath = Path(filename)
        if fpath.suffix == ".cfg":
            from .conversion import read_mm_cfg_file

            return read_mm_cfg_file(fpath)
        if fpath.suffix == ".json":
            return MMConfig.model_validate_json(fpath.read_text())
        if fpath.suffix in {".yaml", ".yml"}:
            import yaml

            data = yaml.safe_load(fpath.read_text())
            return MMConfig.model_validate(data)
        raise NotImplementedError(f"Unsupported input file format: {fpath.suffix}")

    def load_in_pymmcore(
        self, core: "_CoreProtocol", *, exclude_devices: Container[str] = ()
    ) -> None:
        """Apply the configuration to a Micro-Manager core instance."""
        from .pymmcore import load_system_configuration

        load_system_configuration(core, self, exclude_devices=exclude_devices)


def _merge_settings(
    target: list[PropertySetting], source: list[PropertySetting]
) -> list[PropertySetting]:
    """Merge settings from source into target, avoiding duplicates.

    In case of duplicates, the source setting will overwrite the target setting.
    """
    output = {setting.as_tuple()[:2]: setting for setting in target}
    for setting in source:
        output[setting.as_tuple()[:2]] = setting
    return list(output.values())
