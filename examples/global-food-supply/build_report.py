"""Build report.html, the interactive one-pager, from the same validated data as deck.html."""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path

import pandas as pd

ROOT: Path = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "skills" / "make-deck" / "template"))

from charts import to_svg
from spec import Num
from theme import HOUSE

from build_deck import (
    CALORIC_SRC,
    DATA_DIR,
    PULL_DATE,
    REFERENCES,
    UNDER_SRC,
    build_charts,
    compute_figures,
    kcal_at,
    load_validated_datasets,
    undernourish_at,
)

REPORT_TEMPLATE_PATH: Path = ROOT / "report.html.tmpl"
REPORT_OUTPUT_PATH: Path = ROOT / "report.html"
CHART_W: int = 858
CHART_H: int = 395
PLACEHOLDER: re.Pattern[str] = re.compile(r"\{\{(num|chart|table):(\w+)\}\}")
CITATIONS: dict[str, str] = {
    "c1": "<sup>1</sup>",
    "c2": "<sup>2</sup>",
    "c3": "<sup>3</sup>",
    "c4": "<sup>4</sup>",
    "c12": "<sup>1,2</sup>",
}
REGION_ORDER: tuple[tuple[str, str], ...] = (
    ("Africa", "Africa (FAO)"),
    ("World", "World"),
    ("Asia", "Asia (FAO)"),
    ("Americas", "Americas (FAO)"),
    ("Europe", "Europe (FAO)"),
    ("Oceania", "Oceania (FAO)"),
)


def _fill(
    template: str,
    nums: dict[str, Num],
    svgs: dict[str, str],
    tables: dict[str, str],
) -> str:
    """Replace each {{num:key}}, {{chart:key}} and {{table:key}}; an unknown key raises KeyError."""
    values: dict[str, dict[str, str]] = {
        "num": {key: num.text() for key, num in nums.items()},
        "chart": svgs,
        "table": tables,
    }

    def replace(match: re.Match[str]) -> str:
        return values[match.group(1)][match.group(2)]

    return PLACEHOLDER.sub(replace, template)


def _html_table(headers: tuple[str, ...], rows: list[list[str]]) -> str:
    """Return an HTML table with escaped headers and cells."""
    head: str = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body: str = "".join(
        "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def _two_cols(
    left: tuple[str, list[str]], right: tuple[str, list[str]]
) -> str:
    """Return the two-column thesis block: a heading and a bullet list per column."""
    def column(title: str, items: list[str]) -> str:
        lis: str = "".join(f"<li>{escape(item)}</li>" for item in items)
        return f"<div><h3>{escape(title)}</h3><ul>{lis}</ul></div>"

    return f'<div class="cols">{column(*left)}{column(*right)}</div>'


def _capital_html(nums: dict[str, Num]) -> str:
    """Return the deprioritize and fund thesis columns for section 4."""
    return _two_cols(
        ("Aggregate volume thesis (deprioritize)", [
            f"Global cereal output already grew {nums['cereal_prod_growth_pct'].text()} since 1961 (slide 3).",
            f"Global supply reached {nums['world_kcal_2023'].text()} kcal/person/day, above human metabolic need (slide 4).",
            "New acreage expansion yields low marginal caloric security.",
        ]),
        ("Regional yield & access thesis (fund)", [
            f"Africa trails the world mean by {nums['africa_kcal_gap'].text()} kcal/person/day (slide 4).",
            f"Sub-Saharan Africa faces {nums['ssa_undernourish_2024'].text()} undernourishment (slide 5).",
            "Yield-gap inputs and post-harvest storage directly convert output into local supply.",
        ]),
    )


def _decision_html(nums: dict[str, Num]) -> str:
    """Return the 2027–2030 investment decision table."""
    return _html_table(
        ("Investment lever", "Target region", "Primary evidence", "2027–2030 action"),
        [
            [
                "Drought-tolerant seed & soil fertility",
                "Sub-Saharan Africa",
                f"{nums['yield_share_pct'].text()} of historical cereal growth came from yield (slide 3)",
                "Shift R&D budget from land clearing to regional yield trials",
            ],
            [
                "Hermetic storage & cold-chain hubs",
                "Africa (all)",
                f"{nums['africa_undernourish_2024'].text()} undernourishment despite global surplus (slide 5)",
                "Co-finance post-harvest loss reduction near smallholder corridors",
            ],
            [
                "Broad-acre commodity expansion",
                "Global / mature exporters",
                f"Global supply already at {nums['world_kcal_2023'].text()} kcal/day (slide 4)",
                "Cap greenfield acreage capital; hold maintenance only",
            ],
        ],
    )


def _references_html() -> str:
    """Return the numbered reference list, shared with the deck's references slide."""
    items: str = "".join(f"<li>{escape(ref)}</li>" for ref in REFERENCES)
    return f'<ol style="font-size:15px;line-height:1.5;padding-left:22px;margin:8px 0">{items}</ol>'


def _sources_html(nums: dict[str, Num]) -> str:
    """Return the provenance table: every figure, its value and its source."""
    return _html_table(
        ("Key", "Value", "Source"),
        [[key, num.text(), num.source] for key, num in nums.items()],
    )


def _region_json(caloric_df: pd.DataFrame, under_df: pd.DataFrame) -> str:
    """Serialize 2023 kcal, the 1961–2023 gain and 2024 undernourishment for each region."""
    payload: dict[str, dict[str, str]] = {}
    for label, entity in REGION_ORDER:
        k_23: float = kcal_at(caloric_df, entity, 2023)
        gain: float = k_23 - kcal_at(caloric_df, entity, 1961)
        u_24: float = undernourish_at(under_df, entity, 2024) / 100.0
        payload[label] = {
            "kcal_2023": Num(k_23, ",.0f", CALORIC_SRC).text(),
            "kcal_gain": Num(gain, "+,.0f", CALORIC_SRC).text(),
            "undernourish_2024": Num(u_24, ".1%", UNDER_SRC).text(),
        }
    return json.dumps(payload)


def build_food_supply_report(
    data_dir: Path = DATA_DIR,
    template_path: Path = REPORT_TEMPLATE_PATH,
    output_path: Path = REPORT_OUTPUT_PATH,
) -> str:
    """Fill report.html.tmpl with the same figures and chart specs that build deck.html."""
    cereal_df, caloric_df, under_df = load_validated_datasets(data_dir)
    nums: dict[str, Num] = compute_figures(cereal_df, caloric_df, under_df)
    nums["num_count"] = Num(
        float(len(nums) + 1), ",.0f", f"Computed from 3 OWID CSVs, pulled {PULL_DATE}"
    )
    svgs: dict[str, str] = {
        key: to_svg(chart, CHART_W, CHART_H, HOUSE)
        for key, chart in build_charts(cereal_df, caloric_df, under_df).items()
    }
    tables: dict[str, str] = {
        **CITATIONS,
        "capital_cols": _capital_html(nums),
        "decision_matrix": _decision_html(nums),
        "references_list": _references_html(),
        "region_json": _region_json(caloric_df, under_df),
        "sources_table": _sources_html(nums),
    }
    template: str = template_path.read_text(encoding="utf-8")
    html_out: str = _fill(template, nums, svgs, tables)
    output_path.write_text(html_out, encoding="utf-8")
    return html_out


if __name__ == "__main__":
    build_food_supply_report()
