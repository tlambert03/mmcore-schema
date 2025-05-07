"""Write the JSON schema for the MMConfigFile model to a file."""

import json
import sys
from pathlib import Path
from typing import Any

import pydantic_core
from pydantic import json_schema
from pydantic_core.core_schema import NullableSchema

import mmcore_schema


def _sort_schema(d: dict) -> dict:
    custom_order = [
        "$schema",
        "$id",
        "title",
        "description",
        "type",
        "properties",
        "required",
        "additionalProperties",
        "$defs",
    ]

    def sort_key(k: str) -> int:
        return custom_order.index(k) if k in custom_order else len(custom_order)

    return dict(sorted(d.items(), key=lambda item: sort_key(item[0])))


class _GenerateJsonSchemaWithDialect(json_schema.GenerateJsonSchema):
    def nullable_schema(self, schema: NullableSchema) -> dict[str, Any]:
        inner_json_schema = self.generate_inner(schema["schema"])
        return {"type": [inner_json_schema["type"], "null"]}

    def generate(
        self,
        schema: pydantic_core.CoreSchema,
        mode: json_schema.JsonSchemaMode = "validation",
    ) -> dict[str, Any]:
        """Generate a JSON schema with a custom dialect."""
        out = super().generate(schema, mode)
        return {"$schema": self.schema_dialect, **_sort_schema(out)}


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
