"""Write the JSON schema for the MMConfigFile model to a file."""

import json
import sys
from pathlib import Path
from typing import Any

import pydantic_core
from pydantic import json_schema

import mmcore_schema


class _GenerateJsonSchemaWithDialect(json_schema.GenerateJsonSchema):
    def generate(
        self,
        schema: pydantic_core.CoreSchema,
        mode: json_schema.JsonSchemaMode = "validation",
    ) -> dict[str, Any]:
        """Generate a JSON schema with a custom dialect."""
        return {"$schema": self.schema_dialect, **super().generate(schema, mode)}


if len(sys.argv) > 1:
    dest = Path(sys.argv[1])
else:
    dest = Path(mmcore_schema.__file__).parent / "mmconfig.schema.json"
content = (
    json.dumps(
        mmcore_schema.MMConfigFile.model_json_schema(
            schema_generator=_GenerateJsonSchemaWithDialect
        ),
        indent=2,
    )
    + "\n"
)
if dest.read_text(encoding="utf-8") != content:
    dest.write_text(content, encoding="utf-8")
