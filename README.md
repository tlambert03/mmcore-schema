# mmcore-schema

[![License](https://img.shields.io/pypi/l/mmcore-schema.svg?color=green)](https://github.com/tlambert03/mmcore-schema/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mmcore-schema.svg?color=green)](https://pypi.org/project/mmcore-schema)
[![Python Version](https://img.shields.io/pypi/pyversions/mmcore-schema.svg?color=green)](https://python.org)
[![CI](https://github.com/tlambert03/mmcore-schema/actions/workflows/ci.yml/badge.svg)](https://github.com/tlambert03/mmcore-schema/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tlambert03/mmcore-schema/branch/main/graph/badge.svg)](https://codecov.io/gh/tlambert03/mmcore-schema)

Schema for mmCoreAndDevices

```sh
python -c "import mmcore_schema; mmcore_schema.print_schema()"
```

```json
{
  "$defs": {
    "ConfigGroup": {
      "description": "A group of configuration presets.",
      "properties": {
        "name": {
          "description": "The name of the configuration group.",
          "title": "Name",
          "type": "string"
        },
        "configurations": {
          "description": "Configuration settings for the group. ",
          "items": {
            "$ref": "#/$defs/Configuration"
          },
          "title": "Configurations",
          "type": "array"
        }
      },
      "required": [
        "name"
      ],
      "title": "ConfigGroup",
      "type": "object"
    },
    "Configuration": {
      "description": "A group of device property settings.",
      "properties": {
        "name": {
          "description": "A name for this configuration. ",
          "title": "Name",
          "type": "string"
        },
        "settings": {
          "description": "List of settings to apply to the configuration. Settings will be applied in the order they are listed.",
          "items": {
            "$ref": "#/$defs/PropertySetting"
          },
          "title": "Settings",
          "type": "array"
        }
      },
      "required": [
        "name"
      ],
      "title": "Configuration",
      "type": "object"
    },
    "CoreProperties": {
      "properties": {
        "camera_device": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The label of the device to use as the camera.",
          "title": "Camera Device"
        },
        "xy_stage_device": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The label of the device to use as the XY stage.",
          "title": "Xy Stage Device"
        },
        "focus_device": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The label of the device to use as the focus device.",
          "title": "Focus Device"
        },
        "auto_focus_device": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The label of the device to use as the auto focus device.",
          "title": "Auto Focus Device"
        },
        "shutter_device": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The label of the device to use as the shutter device.",
          "title": "Shutter Device"
        },
        "image_processor_device": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The label of the device to use as the image processor device.",
          "title": "Image Processor Device"
        },
        "slm_device": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The label of the device to use as the SLM device.",
          "title": "Slm Device"
        },
        "galvo_device": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The label of the device to use as the galvo device.",
          "title": "Galvo Device"
        },
        "channel_group": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Name of the configuration group that contains optical configuration (i.e. channel group) settings.",
          "title": "Channel Group"
        },
        "auto_shutter": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Whether to enable the auto shutter feature.",
          "title": "Auto Shutter"
        },
        "timeout_ms": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Default timeout for device actions, in milliseconds.",
          "title": "Timeout Ms"
        }
      },
      "title": "CoreProperties",
      "type": "object"
    },
    "Device": {
      "properties": {
        "label": {
          "description": "The user-determined label to assign to the device",
          "title": "Label",
          "type": "string"
        },
        "library": {
          "description": "The adapter library that provides the device.",
          "title": "Library",
          "type": "string"
        },
        "name": {
          "description": "The name of the device to load from the library",
          "title": "Name",
          "type": "string"
        },
        "delay_ms": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Delay, in milliseconds, for device acitons. (note: Some devices ignore this setting.)",
          "title": "Delay Ms"
        },
        "focus_direction": {
          "anyOf": [
            {
              "enum": [
                -1,
                0,
                1
              ],
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Focus direction (only applicable for Stage Devices, ignored otherwise). -1 = increasing position moves objective away from sample.  0 | None = unknown.  1 = increasing position moves objective towards sample. ",
          "title": "Focus Direction"
        },
        "state_labels": {
          "anyOf": [
            {
              "additionalProperties": {
                "type": "string"
              },
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "A dictionary mapping state numbers to labels (only applicable for State Devices, ignored otherwise). Provides a human-readable label for each state of the device.",
          "title": "State Labels"
        }
      },
      "required": [
        "label",
        "library",
        "name"
      ],
      "title": "Device",
      "type": "object"
    },
    "DeviceProperty": {
      "properties": {
        "device_label": {
          "description": "The label of the device to set the property on",
          "title": "Device Label",
          "type": "string"
        },
        "property_name": {
          "description": "The name of the property to set on the device",
          "title": "Property Name",
          "type": "string"
        },
        "value": {
          "description": "The value to set for the property on the device",
          "title": "Value",
          "type": "string"
        }
      },
      "required": [
        "device_label",
        "property_name",
        "value"
      ],
      "title": "DeviceProperty",
      "type": "object"
    },
    "PixelSizeConfiguration": {
      "description": "Configuration of a pixel size.",
      "properties": {
        "name": {
          "description": "A name for this configuration. ",
          "title": "Name",
          "type": "string"
        },
        "settings": {
          "description": "List of settings to apply to the configuration. Settings will be applied in the order they are listed.",
          "items": {
            "$ref": "#/$defs/PropertySetting"
          },
          "title": "Settings",
          "type": "array"
        },
        "pixel_size_um": {
          "description": "Pixel size in micrometers. This is the size of a pixel in the image sensor of the camera.",
          "title": "Pixel Size Um",
          "type": "number"
        },
        "affine_matrix": {
          "anyOf": [
            {
              "maxItems": 6,
              "minItems": 6,
              "prefixItems": [
                {
                  "type": "number"
                },
                {
                  "type": "number"
                },
                {
                  "type": "number"
                },
                {
                  "type": "number"
                },
                {
                  "type": "number"
                },
                {
                  "type": "number"
                }
              ],
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Affine transformation matrix to apply to the configuration group. This is a 2x3 matrix represented as a tuple of 6 floats.",
          "title": "Affine Matrix"
        },
        "dxdz": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The angle between the camera's x axis and the axis (direction)of the z drive for the given pixel size configuration. This angle isdimensionless (i.e. the ratio of the translation in x caused by a translation in z, i.e. dx / dz).",
          "title": "Dxdz"
        },
        "dydz": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The angle between the camera's y axis and the axis (direction)of the z drive for the given pixel size configuration. This angle isdimensionless (i.e. the ratio of the translation in y caused by a translation in z, i.e. dy / dz).",
          "title": "Dydz"
        },
        "optimal_z_um": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "User-defined 'optimal' z step size for this pixel size configuration.",
          "title": "Optimal Z Um"
        }
      },
      "required": [
        "name",
        "pixel_size_um"
      ],
      "title": "PixelSizeConfiguration",
      "type": "object"
    },
    "PropertySetting": {
      "description": "A single device property setting.",
      "properties": {
        "device_label": {
          "description": "The label of the device to set the configuration on",
          "title": "Device Label",
          "type": "string"
        },
        "property_name": {
          "description": "The name of the property to set on the device",
          "title": "Property Name",
          "type": "string"
        },
        "value": {
          "description": "The value to set for the property on the device",
          "title": "Value",
          "type": "string"
        }
      },
      "required": [
        "device_label",
        "property_name",
        "value"
      ],
      "title": "PropertySetting",
      "type": "object"
    }
  },
  "properties": {
    "devices": {
      "description": "List of devices to load. Devices will be loaded in the order they are listed.",
      "items": {
        "$ref": "#/$defs/Device"
      },
      "title": "Devices",
      "type": "array"
    },
    "pre_init_properties": {
      "description": "List of properties to set on devices before device initialization. Properties will be set in the order they are listed.",
      "items": {
        "$ref": "#/$defs/DeviceProperty"
      },
      "title": "Pre Init Properties",
      "type": "array"
    },
    "post_init_properties": {
      "description": "List of properties to set on devices after device initialization. Properties will be set in the order they are listed.",
      "items": {
        "$ref": "#/$defs/DeviceProperty"
      },
      "title": "Post Init Properties",
      "type": "array"
    },
    "core_properties": {
      "$ref": "#/$defs/CoreProperties",
      "description": "Default properties to set on the Micro-Manager core."
    },
    "configuration_groups": {
      "description": "Configuration groups to create.",
      "items": {
        "$ref": "#/$defs/ConfigGroup"
      },
      "title": "Configuration Groups",
      "type": "array"
    },
    "pixel_size_configurations": {
      "description": "Pixel size configurations to create. These configurations will be used to set the pixel size of the camera.",
      "items": {
        "$ref": "#/$defs/PixelSizeConfiguration"
      },
      "title": "Pixel Size Configurations",
      "type": "array"
    },
    "extra": {
      "additionalProperties": true,
      "description": "User-defined extra properties. Not used by Micro-Manager.",
      "title": "Extra",
      "type": "object"
    }
  },
  "title": "MMConfigFile",
  "type": "object"
}
```