"""Tests that chart.schema.json, the chart grammar contract, matches ChartData and both renderers."""

import json
from dataclasses import MISSING, fields
from pathlib import Path

from charts import KIND_LABELS, RENDERERS, ChartData

SCHEMA: dict = json.loads(
    (Path(__file__).resolve().parents[1] / "chart.schema.json").read_text()
)
KINDS: dict[str, str] = {
    entry["const"]: entry["title"] for entry in SCHEMA["properties"]["kind"]["oneOf"]
}


def test_schema_kinds_match_the_svg_renderers_and_their_labels() -> None:
    assert set(KINDS) == set(RENDERERS)
    assert KINDS == KIND_LABELS


def test_schema_chart_data_matches_the_dataclass_fields_and_defaults() -> None:
    data: dict = SCHEMA["$defs"]["ChartData"]
    required: set[str] = {f.name for f in fields(ChartData) if f.default is MISSING}
    defaults: dict[str, object] = {
        f.name: f.default for f in fields(ChartData) if f.default is not MISSING
    }

    assert list(data["properties"]) == [f.name for f in fields(ChartData)]
    assert set(data["required"]) == required
    assert {name: data["properties"][name]["default"] for name in defaults} == defaults
