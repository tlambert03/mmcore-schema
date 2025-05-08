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

## CLI

After installing, you will have an `mmconfig` command line tool available.

```bash
pip install mmcore-schema
```

```bash
mmconfig --help
```

Convert a Micro-Manager .cfg file to JSON (or YAML):

```bash
mmconfig MMConfig_demo.cfg new_format.json
```

## Python usage

The schema is implemented in Python using [Pydantic](https://docs.pydantic.dev/),
and the main class is `mmcore_schema.MMConfig`.

```python
from mmcore_schema import MMConfig

mmconfig = MMConfig.from_file("path/to/MMConfig.cfg")
```

### Applying to a python Core

The mmcore_schema.pymmcore module provides a way to apply an MMConfig object to
a (python) Micro-Manager core object, (i.e.
[pymmcore](https://github.com/micro-manager/pymmcore),
[pymmcore-plus](https://github.com/pymmcore-plus/pymmcore-plus), or
[pymmcore-nano](https://github.com/pymmcore-plus/pymmcore-nano)):

```python
from mmcore_schema import MMConfig
import pymmcore

# or pymmcore_plus.CMMCorePlus()
# or pymmcore_nano.CMMCore()
core = pymmcore.CMMCore() 

mmconfig = MMConfig.from_file("path/to/MMConfig.cfg")
mmconfig.load_in_pymmcore(core)
```
