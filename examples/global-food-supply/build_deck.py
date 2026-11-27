"""Build the global food supply readout as deck.html and deck.pptx from validated OWID CSVs."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd

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

ROOT: Path = Path(__file__).resolve().parent
KIT_DIR: Path = ROOT.parents[1] / "skills" / "make-deck" / "template"
sys.path.insert(0, str(KIT_DIR))

from charts import ChartData
from render_html import render_html
from render_pptx import render_pptx
from spec import (
    Bullet,
    Bullets,
    Card,
    Chart,
    Deck,
    Num,
    Para,
    Run,
    Slide,
    Table,
    Text,
    validate,
)
from theme import HOUSE

DATA_DIR: Path = ROOT / "data"
PULL_DATE: str = "2026-11-21"
CEREAL_SRC: str = f"OWID cereal index, pulled {PULL_DATE}"
CALORIC_SRC: str = f"OWID daily caloric supply, pulled {PULL_DATE}"
UNDER_SRC: str = f"OWID undernourishment, pulled {PULL_DATE}"
DECK_TITLE: str = "Global food supply readout (1961–2024)"
READOUT_TITLE: str = "Global food production outpaced population, yet Africa remains undernourished"
READOUT_SUBTITLE: str = (
    "Capital allocation readout for 2027–2030 ag-tech and food-security investment: "
    "aggregate volume vs. regional yield-gap closure and distribution."
)
FAO_REGIONS: tuple[str, ...] = (
    "World",
    "Africa (FAO)",
    "Asia (FAO)",
    "Americas (FAO)",
    "Europe (FAO)",
    "Oceania (FAO)",
)
UNDERNOURISH_REGIONS: tuple[str, ...] = (
    "Sub-Saharan Africa (FAO)",
    "Africa (FAO)",
    "World",
    "Oceania (FAO)",
    "Asia (FAO)",
    "Americas (FAO)",
    "Europe (FAO)",
)
CALORIC_LINES: tuple[tuple[str, str], ...] = (
    ("World", "World"),
    ("Asia", "Asia (FAO)"),
    ("Africa", "Africa (FAO)"),
)
TABLE_ROWS: tuple[tuple[str, str], ...] = (
    ("Africa", "Africa (FAO)"),
    ("World", "World"),
    ("Asia", "Asia (FAO)"),
    ("Americas", "Americas (FAO)"),
    ("Europe", "Europe (FAO)"),
    ("Oceania", "Oceania (FAO)"),
)
REFERENCES: tuple[str, ...] = (
    (
        "FAO, FAOSTAT Crops and Livestock Products (cereal production, yield and harvested area, "
        "1961–2024); UN DESA, World Population Prospects 2024 (population). Via Our World in Data, "
        f"cereal_index.csv, pulled {PULL_DATE}. "
        "https://ourworldindata.org/grapher/index-of-cereal-production-yield-and-land-use"
    ),
    (
        "FAO, FAOSTAT Food Balance Sheets (daily per capita caloric supply, 1961–2023). Via Our World "
        f"in Data, caloric_supply.csv, pulled {PULL_DATE}. "
        "https://ourworldindata.org/grapher/daily-per-capita-caloric-supply"
    ),
    (
        "FAO, IFAD, UNICEF, WFP and WHO, SOFI report, SDG indicator 2.1.1 prevalence of "
        f"undernourishment (2000–2024). Via Our World in Data, undernourishment.csv, pulled {PULL_DATE}. "
        "https://ourworldindata.org/grapher/prevalence-of-undernourishment"
    ),
)


def load_validated_datasets(
    data_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read raw OWID CSVs and validate required columns and domains via Pandera."""
    cereal_raw = pd.read_csv(data_dir / "cereal_index.csv")
    cereal_world = cereal_raw.loc[
        (cereal_raw["entity"] == "World") & (cereal_raw["year"].between(1961, 2023))
    ].copy()
    cereal_df = CEREAL_INDEX_SCHEMA.validate(cereal_world)

    caloric_raw = pd.read_csv(data_dir / "caloric_supply.csv")
    caloric_sub = caloric_raw.loc[
        caloric_raw["entity"].isin(FAO_REGIONS)
        & (caloric_raw["year"].between(1961, 2023))
    ].copy()
    caloric_df = CALORIC_SUPPLY_SCHEMA.validate(caloric_sub)

    under_raw = pd.read_csv(data_dir / "undernourishment.csv")
    under_sub = under_raw.loc[
        under_raw["entity"].isin(UNDERNOURISH_REGIONS)
        & (under_raw["year"].between(2000, 2024))
    ].copy()
    under_df = UNDERNOURISHMENT_SCHEMA.validate(under_sub)

    return cereal_df, caloric_df, under_df


def _row_by_year(df: pd.DataFrame, entity: str, year: int) -> pd.Series:
    """Return the unique row for an entity and year, failing loudly if missing."""
    sub = df.loc[(df["entity"] == entity) & (df["year"] == year)]
    if len(sub) != 1:
        raise ValueError(
            f"Expected 1 row for entity={entity!r}, year={year}, got {len(sub)}"
        )
    return sub.iloc[0]


def kcal_at(df: pd.DataFrame, entity: str, year: int) -> float:
    """Return daily kcal per person for one entity and year."""
    return float(_row_by_year(df, entity, year)[CALORIC_COL])


def undernourish_at(df: pd.DataFrame, entity: str, year: int) -> float:
    """Return undernourishment prevalence in percent for one entity and year."""
    return float(_row_by_year(df, entity, year)[UNDERNOURISH_COL])


def _cereal_figures(df: pd.DataFrame) -> dict[str, Num]:
    """Return cereal output, yield, land and population figures, 1961 against 2023."""
    c61 = _row_by_year(df, "World", 1961)
    c23 = _row_by_year(df, "World", 2023)
    prod: float = float(c23[CEREAL_PROD_COL] / c61[CEREAL_PROD_COL])
    yld: float = float(c23[CEREAL_YIELD_COL] / c61[CEREAL_YIELD_COL])
    pop: float = float(c23[POP_COL] / c61[POP_COL])
    area: float = float(c23[CEREAL_AREA_COL] / c61[CEREAL_AREA_COL])
    share: float = math.log(yld) / math.log(prod)
    return {
        "cereal_prod_idx": Num(prod * 100.0, ".0f", CEREAL_SRC),
        "pop_idx": Num(pop * 100.0, ".0f", CEREAL_SRC),
        "yield_share_pct": Num(share, ".0%", CEREAL_SRC),
        "cereal_prod_growth_pct": Num(prod - 1.0, ".0%", CEREAL_SRC),
        "pop_growth_pct": Num(pop - 1.0, ".0%", CEREAL_SRC),
        "land_growth_pct": Num(area - 1.0, ".0%", CEREAL_SRC),
        "yield_growth_pct": Num(yld - 1.0, ".0%", CEREAL_SRC),
        "world_yield_2023": Num(float(c23[CEREAL_YIELD_COL]) * 1000.0, ",.0f kg/ha", CEREAL_SRC),
    }


def _supply_figures(df: pd.DataFrame) -> dict[str, Num]:
    """Return caloric supply for the world, Africa and Asia, with the Africa gap."""
    world: float = kcal_at(df, "World", 2023)
    africa_23: float = kcal_at(df, "Africa (FAO)", 2023)
    africa_61: float = kcal_at(df, "Africa (FAO)", 1961)
    asia_23: float = kcal_at(df, "Asia (FAO)", 2023)
    asia_61: float = kcal_at(df, "Asia (FAO)", 1961)
    return {
        "world_kcal_2023": Num(world, ",.0f", CALORIC_SRC),
        "africa_kcal_2023": Num(africa_23, ",.0f", CALORIC_SRC),
        "africa_kcal_gain": Num(africa_23 - africa_61, ",.0f", CALORIC_SRC),
        "africa_kcal_gap": Num(world - africa_23, ",.0f", CALORIC_SRC),
        "asia_kcal_2023": Num(asia_23, ",.0f", CALORIC_SRC),
        "asia_kcal_gain": Num(asia_23 - asia_61, ",.0f", CALORIC_SRC),
    }


def _under_figures(df: pd.DataFrame) -> dict[str, Num]:
    """Return SDG 2.1.1 undernourishment for the world, Africa, Sub-Saharan Africa and Europe."""
    world_00: float = undernourish_at(df, "World", 2000) / 100.0
    world_24: float = undernourish_at(df, "World", 2024) / 100.0
    africa_24: float = undernourish_at(df, "Africa (FAO)", 2024) / 100.0
    ssa_24: float = undernourish_at(df, "Sub-Saharan Africa (FAO)", 2024) / 100.0
    europe_24: float = undernourish_at(df, "Europe (FAO)", 2024) / 100.0
    return {
        "world_undernourish_2000": Num(world_00, ".1%", UNDER_SRC),
        "world_undernourish_2024": Num(world_24, ".1%", UNDER_SRC),
        "world_undernourish_drop_pp": Num((world_00 - world_24) * 100.0, ".1f pp", UNDER_SRC),
        "africa_undernourish_2024": Num(africa_24, ".1%", UNDER_SRC),
        "ssa_undernourish_2024": Num(ssa_24, ".1%", UNDER_SRC),
        "fao_floor_pct": Num(europe_24, ".1%", UNDER_SRC),
    }


def compute_figures(
    cereal_df: pd.DataFrame, caloric_df: pd.DataFrame, under_df: pd.DataFrame
) -> dict[str, Num]:
    """Return every figure the readout cites, each with its dataset and pull date."""
    return {
        **_cereal_figures(cereal_df),
        **_supply_figures(caloric_df),
        **_under_figures(under_df),
    }


def _sample_years(df: pd.DataFrame) -> pd.DataFrame:
    """Keep every second year from 1961, so 2023 stays in. The line chart takes at most 40 points."""
    return df.loc[(df["year"] - 1961) % 2 == 0]


def _years(df: pd.DataFrame) -> tuple[str, ...]:
    """Return the distinct years in a frame as strings, in order."""
    return tuple(str(int(year)) for year in sorted(df["year"].unique()))


def _cereal_chart(df: pd.DataFrame) -> Chart:
    """Return indexed (1961 = 100) world cereal production, yield and population."""
    world: pd.DataFrame = _sample_years(df.sort_values("year"))
    base: pd.Series = world.iloc[0]

    def index(col: str) -> tuple[float, ...]:
        return tuple(float(value / base[col] * 100.0) for value in world[col])

    data: ChartData = ChartData(
        categories=_years(world),
        series=(
            ("Production", index(CEREAL_PROD_COL)),
            ("Yield", index(CEREAL_YIELD_COL)),
            ("Population", index(POP_COL)),
        ),
        unit="Index (1961 = 100)",
        source=CEREAL_SRC,
    )
    return Chart("line", data)


def _caloric_chart(df: pd.DataFrame) -> Chart:
    """Return daily per-capita caloric supply for the world, Asia and Africa, 1961 to 2023."""
    sampled: pd.DataFrame = _sample_years(df)
    series: tuple[tuple[str, tuple[float, ...]], ...] = tuple(
        (label, tuple(float(v) for v in sampled.loc[sampled["entity"] == entity].sort_values("year")[CALORIC_COL]))
        for label, entity in CALORIC_LINES
    )
    data: ChartData = ChartData(
        categories=_years(sampled),
        series=series,
        unit="kcal / person / day",
        source=CALORIC_SRC,
    )
    return Chart("line", data)


def _access_chart(df: pd.DataFrame) -> Chart:
    """Return undernourishment prevalence for the world and Africa, 2000 to 2024."""
    def prevalence(entity: str) -> tuple[float, ...]:
        sub: pd.DataFrame = df.loc[df["entity"] == entity].sort_values("year")
        return tuple(float(v) for v in sub[UNDERNOURISH_COL])

    data: ChartData = ChartData(
        categories=tuple(str(year) for year in range(2000, 2025)),
        series=(("World", prevalence("World")), ("Africa", prevalence("Africa (FAO)"))),
        unit="percent of population",
        source=UNDER_SRC,
    )
    return Chart("line", data)


def build_charts(
    cereal_df: pd.DataFrame, caloric_df: pd.DataFrame, under_df: pd.DataFrame
) -> dict[str, Chart]:
    """Return the three chart specs, keyed by the placeholder names the report uses."""
    return {
        "cereal_index": _cereal_chart(cereal_df),
        "caloric_supply": _caloric_chart(caloric_df),
        "undernourishment": _access_chart(under_df),
    }


def build_caloric_table(df: pd.DataFrame) -> Table:
    """Return 2023 caloric supply and the change since 1961 for each region."""
    rows: list[tuple[str | Num, ...]] = []
    for label, entity in TABLE_ROWS:
        k_23: float = kcal_at(df, entity, 2023)
        gain: float = k_23 - kcal_at(df, entity, 1961)
        rows.append((label, Num(k_23, ",.0f kcal", CALORIC_SRC), Num(gain, "+,.0f kcal", CALORIC_SRC)))
    return Table(("Region", "2023 supply", "Change since 1961"), tuple(rows), ("left", "right", "right"))


def _para(*texts: str) -> Text:
    """Build a text block with one paragraph per argument."""
    return Text(tuple(Para((Run(t),)) for t in texts))


def _cover() -> Slide:
    """Return the cover with the readout title, subtitle and meta line."""
    return Slide(
        layout="cover",
        title=READOUT_TITLE,
        regions={
            "subtitle": _para(READOUT_SUBTITLE),
            "meta": _para(
                f"Audience: Investment Committee · Data: FAOSTAT & UN WPP via Our World in Data · As of {PULL_DATE}"
            ),
        },
    )


def _synthesis(f: dict[str, Num]) -> Slide:
    """Return the executive synthesis: three findings, each with its key number."""
    cards: tuple[Card, ...] = (
        Card(
            "Aggregate supply",
            "Yields drove growth",
            f"Share of cereal growth from yields, 1961–2023. Output index "
            f"{f['cereal_prod_idx'].text()} vs. population {f['pop_idx'].text()}.",
            metric=f["yield_share_pct"],
        ),
        Card(
            "Regional divergence",
            "Africa lags the world mean",
            f"Kcal per person per day below the world mean in 2023. Africa "
            f"{f['africa_kcal_2023'].text()} vs. world {f['world_kcal_2023'].text()}.",
            metric=f["africa_kcal_gap"],
        ),
        Card(
            "The access gap",
            "Undernourishment persists in Africa",
            f"World {f['world_undernourish_2024'].text()} in 2024; Sub-Saharan Africa "
            f"{f['ssa_undernourish_2024'].text()}.",
            metric=f["africa_undernourish_2024"],
        ),
    )
    return Slide(
        layout="cards3",
        title="Shift capital from global volume expansion to closing regional yield and access gaps",
        kicker="Executive synthesis",
        lead="Three findings, each with its key number",
        regions={"cards": cards},
    )


def _cereal_slide(f: dict[str, Num], chart: Chart) -> Slide:
    """Return slide 1: aggregate cereal output against population, with takeaways."""
    takeaways: Bullets = Bullets(
        (
            Bullet(
                "Beat population",
                f"Output grew {f['cereal_prod_growth_pct'].text()} vs. "
                f"{f['pop_growth_pct'].text()} population (1961–2023).",
            ),
            Bullet(
                "Land spared",
                f"Cereal area rose {f['land_growth_pct'].text()}; yield rose "
                f"{f['yield_growth_pct'].text()} to {f['world_yield_2023'].text()}.",
            ),
            Bullet(
                "Method",
                "Yield share is ln(yield ratio) / ln(production ratio), 1961–2023. "
                "Cereals proxy staple calories.",
            ),
        ),
        heading="Key takeaways",
    )
    return Slide(
        layout="chart_3to1",
        kicker="1 · Aggregate supply",
        title=f"Global cereal output grew {f['cereal_prod_growth_pct'].text()} since 1961, driven "
        f"{f['yield_share_pct'].text()} by yields rather than land",
        lead="World cereal production, yield, harvested area and population, index 1961 = 100",
        regions={"chart": chart, "takeaways": takeaways},
        notes="Regional check: global averages mask wide regional gaps in per-capita calories.",
    )


def _caloric_slide(f: dict[str, Num], chart: Chart, table: Table) -> Slide:
    """Return slide 2: caloric supply by region, with the Africa gap in the table and title."""
    return Slide(
        layout="chart_table",
        kicker="2 · Regional divergence",
        title=f"Per-capita caloric supply rose everywhere, yet Africa sits "
        f"{f['africa_kcal_gap'].text()} kcal/day below the global average",
        lead="Daily per-capita dietary energy supply by FAO region, kcal per person per day, 1961–2023",
        regions={
            "chart": chart,
            "table": table,
            "note": _para("Supply at retail, not intake."),
        },
    )


def _access_slide(f: dict[str, Num], chart: Chart) -> Slide:
    """Return slide 3: undernourishment, world against Africa, with takeaways."""
    takeaways: Bullets = Bullets(
        (
            Bullet(
                "Global drop",
                f"World rate fell {f['world_undernourish_drop_pp'].text()}, from "
                f"{f['world_undernourish_2000'].text()} in 2000 to "
                f"{f['world_undernourish_2024'].text()} in 2024.",
            ),
            Bullet(
                "Africa outlier",
                f"Sub-Saharan Africa is {f['ssa_undernourish_2024'].text()}, nearly triple the global rate.",
            ),
            Bullet("Capital implication", "Shift funding from acreage to African yield and storage."),
        ),
        heading="Key takeaways",
    )
    return Slide(
        layout="chart_3to1",
        kicker="3 · The access gap",
        title=f"Undernourishment fell globally to {f['world_undernourish_2024'].text()} in 2024, "
        f"while Africa stayed at {f['africa_undernourish_2024'].text()}",
        lead="Prevalence of undernourishment (SDG 2.1.1), percent of population, 2000–2024",
        regions={"chart": chart, "takeaways": takeaways},
    )


def _capital_slide(f: dict[str, Num]) -> Slide:
    """Return slide 4: three capital levers with the evidence for each, and a recommendation."""
    cards: tuple[Card, ...] = (
        Card(
            "Lever A",
            "Broad-acre commodity expansion",
            f"Target: global and mature exporters. Global supply already at "
            f"{f['world_kcal_2023'].text()} kcal/day.",
            metric=f["world_kcal_2023"],
            rows=(Bullet("Action", "Cap greenfield acreage capital; hold maintenance only."),),
        ),
        Card(
            "Lever B",
            "Drought-tolerant seed and soil fertility",
            "Target: Sub-Saharan Africa. Yield share of historical cereal growth, 1961–2023.",
            metric=f["yield_share_pct"],
            badge="Recommended",
            rows=(Bullet("Action", "Shift R&D budget from land clearing to regional yield trials."),),
        ),
        Card(
            "Lever C",
            "Hermetic storage and cold-chain hubs",
            f"Target: Africa. Undernourishment stands at {f['africa_undernourish_2024'].text()} "
            "despite a global surplus.",
            metric=f["africa_undernourish_2024"],
            rows=(Bullet("Action", "Co-finance post-harvest loss reduction near smallholder corridors."),),
        ),
    )
    return Slide(
        layout="options3",
        kicker="4 · Capital implication",
        title="Redirect 2027–2030 capital from aggregate acreage to African yield-gap closure and storage",
        lead="Three investment levers for 2027–2030, with the evidence behind each",
        regions={
            "cards": cards,
            "recommendation": _para(
                "Recommendation: cap greenfield cropland expansion; move 2027–2030 R&D and storage "
                "capital to African yield-gap closure."
            ),
        },
    )


def _references_slide() -> Slide:
    """Return the references slide: three data sources with URLs and the pull date."""
    return Slide(
        layout="references",
        kicker="References",
        title=f"Full source list: three public datasets, pulled {PULL_DATE}",
        regions={"body": _para(*REFERENCES)},
    )


def build_deck_spec(
    figs: dict[str, Num], charts: dict[str, Chart], caloric_table: Table
) -> Deck:
    """Assemble the seven-slide readout from figures, charts and the caloric table."""
    slides: tuple[Slide, ...] = (
        _cover(),
        _synthesis(figs),
        _cereal_slide(figs, charts["cereal_index"]),
        _caloric_slide(figs, charts["caloric_supply"], caloric_table),
        _access_slide(figs, charts["undernourishment"]),
        _capital_slide(figs),
        _references_slide(),
    )
    return Deck(title=DECK_TITLE, short_title="Global food supply", as_of=PULL_DATE, slides=slides)


def build_food_supply_deck(data_dir: Path = DATA_DIR, out_dir: Path = ROOT) -> Deck:
    """Validate the data, build the deck spec and write deck.html and deck.pptx to out_dir."""
    cereal_df, caloric_df, under_df = load_validated_datasets(data_dir)
    figs = compute_figures(cereal_df, caloric_df, under_df)
    charts = build_charts(cereal_df, caloric_df, under_df)
    deck = build_deck_spec(figs, charts, build_caloric_table(caloric_df))
    validate(deck)
    (out_dir / "deck.html").write_text(render_html(deck, HOUSE), encoding="utf-8")
    (out_dir / "deck.pptx").write_bytes(render_pptx(deck, HOUSE))
    return deck


if __name__ == "__main__":
    build_food_supply_deck()
