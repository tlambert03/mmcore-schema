"""Write the JSON schema for the MMConfigFile model to a file."""

import json
from pathlib import Path
from typing import Any

import pydantic_core
from pydantic import json_schema
from pydantic_core.core_schema import NullableSchema

import mmcore_schema


class _Generator(json_schema.GenerateJsonSchema):
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


def main() -> None:
    """Write the JSON schema for the MMConfigFile model to a file."""
    extra = mmcore_schema.MMConfigFile.model_config.get("json_schema_extra")
    assert isinstance(extra, dict) and "$id" in extra
    # example id_: /schemas/mmconfig/1.0/mmconfig.schema.json
    id_ = str(extra["$id"]).replace(mmcore_schema.SCHEMA_URL_BASE, "")

    # mirror the directory structure of the schema URL
    dest = Path(Path(__file__).parent.absolute(), *id_.split("/"))
    dest.parent.mkdir(parents=True, exist_ok=True)

    # write the schema to the file, only if it has changed
    schema = mmcore_schema.MMConfigFile.model_json_schema(schema_generator=_Generator)
    content = json.dumps(schema, indent=2) + "\n"
    if dest.exists() and dest.read_text(encoding="utf-8") == content:
        return
    dest.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
