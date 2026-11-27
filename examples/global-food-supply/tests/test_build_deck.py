"""Unit and integration tests for the global food supply readout."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pandera.errors
import pytest
from pptx import Presentation
from spec import Deck, Num, all_nums, validate

from build_deck import _row_by_year, build_food_supply_deck
from build_report import _fill, build_food_supply_report
from schemas import (
    CALORIC_COL,
    CALORIC_SUPPLY_SCHEMA,
    CEREAL_AREA_COL,
    CEREAL_INDEX_SCHEMA,
    CEREAL_PROD_COL,
    CEREAL_YIELD_COL,
    POP_COL,
    UNDERNOURISH_COL,
    UNDERNOURISHMENT_SCHEMA,
)

EXPECTED_LAYOUTS: list[str] = [
    "cover",
    "cards3",
    "chart_3to1",
    "chart_table",
    "chart_3to1",
    "options3",
    "references",
]
SHARED_TOKENS: tuple[str, ...] = ("357", "90%", "3,006", "450", "8.2%", "20.2%", "22.3%")
PULL_TOKEN = "pulled 2026-11-21"
EXTERNAL_URL = re.compile(r'src="http|href="http|<img|@import|url\(http')


@pytest.fixture(scope="module")
def built(tmp_path_factory: pytest.TempPathFactory) -> tuple[Deck, Path]:
    """Build deck.html and deck.pptx once into a temporary folder for the module."""
    out_dir: Path = tmp_path_factory.mktemp("deck")
    return build_food_supply_deck(out_dir=out_dir), out_dir


def test_cereal_schema_rejects_non_positive_yield() -> None:
    """Arrange invalid non-positive yield, act with validate, assert SchemaError."""
    bad = pd.DataFrame(
        {
            "entity": ["World"],
            "year": [2023],
            CEREAL_AREA_COL: [700_000_000.0],
            CEREAL_PROD_COL: [3_000_000_000.0],
            CEREAL_YIELD_COL: [0.0],
            POP_COL: [8_000_000_000.0],
        }
    )
    with pytest.raises(pandera.errors.SchemaError):
        CEREAL_INDEX_SCHEMA.validate(bad)


def test_caloric_schema_rejects_nan_and_out_of_range() -> None:
    """Arrange NaN and out-of-bounds calories, act with validate, assert SchemaError."""
    nan_df = pd.DataFrame(
        {"entity": ["World"], "year": [2023], CALORIC_COL: [float("nan")]}
    )
    with pytest.raises(pandera.errors.SchemaError):
        CALORIC_SUPPLY_SCHEMA.validate(nan_df)

    low_df = pd.DataFrame({"entity": ["World"], "year": [2023], CALORIC_COL: [100.0]})
    with pytest.raises(pandera.errors.SchemaError):
        CALORIC_SUPPLY_SCHEMA.validate(low_df)


def test_undernourishment_schema_rejects_over_100_percent() -> None:
    """Arrange >100% prevalence, act with validate, assert SchemaError."""
    bad = pd.DataFrame({"entity": ["World"], "year": [2024], UNDERNOURISH_COL: [105.0]})
    with pytest.raises(pandera.errors.SchemaError):
        UNDERNOURISHMENT_SCHEMA.validate(bad)


def test_row_by_year_raises_on_empty_or_missing() -> None:
    """Arrange empty dataframe, act with _row_by_year, assert ValueError."""
    empty = pd.DataFrame({"entity": pd.Series(dtype=str), "year": pd.Series(dtype=int)})
    with pytest.raises(ValueError, match="Expected 1 row"):
        _row_by_year(empty, "World", 2023)


def test_fill_replaces_each_placeholder_kind() -> None:
    """Arrange one num and one table placeholder, act with _fill, assert both are replaced."""
    filled = _fill(
        "{{num:a}}|{{table:b}}|{{chart:c}}",
        {"a": Num(0.5, ".1%", "src")},
        {"c": "<svg/>"},
        {"b": "<table/>"},
    )
    assert filled == "50.0%|<table/>|<svg/>"


def test_fill_raises_on_unknown_placeholder() -> None:
    """Arrange a placeholder with no value, act with _fill, assert KeyError."""
    with pytest.raises(KeyError):
        _fill("{{num:missing}}", {}, {}, {})


def test_deck_validates(built: tuple[Deck, Path]) -> None:
    """Arrange the built deck, act with validate, assert no layout or region error."""
    deck, _ = built
    validate(deck)


def test_deck_has_expected_slides(built: tuple[Deck, Path]) -> None:
    """Arrange the built deck, act by reading its layouts, assert the seven readout slides."""
    deck, _ = built
    assert [slide.layout for slide in deck.slides] == EXPECTED_LAYOUTS


def test_every_num_has_a_source(built: tuple[Deck, Path]) -> None:
    """Arrange the built deck, act by walking every Num, assert each has a dataset and pull date."""
    deck, _ = built
    nums = all_nums(deck)
    assert nums
    for slide_number, path, num in nums:
        assert num.source, f"slide {slide_number} {path} has no source"
        assert PULL_TOKEN in num.source



def test_deck_html_is_self_contained(built: tuple[Deck, Path]) -> None:
    """Arrange deck.html, act by reading it, assert the sources slides and no external assets."""
    _, out_dir = built
    html_text = (out_dir / "deck.html").read_text(encoding="utf-8")
    assert "Backup · Sources" in html_text
    assert "{{" not in html_text
    assert not EXTERNAL_URL.search(html_text)


def test_deck_pptx_opens(built: tuple[Deck, Path]) -> None:
    """Arrange deck.pptx, act by opening it with python-pptx, assert it has every deck slide."""
    deck, out_dir = built
    presentation = Presentation(str(out_dir / "deck.pptx"))
    assert len(presentation.slides) >= len(deck.slides)


def test_report_matches_deck_numbers(
    built: tuple[Deck, Path], tmp_path: Path
) -> None:
    """Arrange both outputs, act by building the report, assert no placeholder and shared figures."""
    _, out_dir = built
    deck_html = (out_dir / "deck.html").read_text(encoding="utf-8")
    report_html = build_food_supply_report(output_path=tmp_path / "report.html")

    assert "{{" not in report_html
    assert not EXTERNAL_URL.search(report_html)
    for token in SHARED_TOKENS:
        assert token in deck_html
        assert token in report_html
