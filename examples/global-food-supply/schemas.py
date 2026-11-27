"""Pandera schemas for public Our World in Data / FAOSTAT food-supply CSVs."""

import pandera.pandas as pa

CEREAL_AREA_COL = "cereals__00001717__area_harvested__005312__hectares"
CEREAL_PROD_COL = "cereals__00001717__production__005510__tonnes"
CEREAL_YIELD_COL = "cereals__00001717__yield__005412__tonnes_per_hectare"
POP_COL = "population_historical"
CALORIC_COL = "daily_calories"
UNDERNOURISH_COL = (
    "_2_1_1_prevalence_of_undernourishment__000000000024000__value__006121__percent"
)

CEREAL_INDEX_SCHEMA = pa.DataFrameSchema(
    columns={
        "entity": pa.Column(str, nullable=False),
        "year": pa.Column(int, pa.Check.ge(1961), nullable=False),
        CEREAL_AREA_COL: pa.Column(float, pa.Check.gt(0), nullable=False),
        CEREAL_PROD_COL: pa.Column(float, pa.Check.gt(0), nullable=False),
        CEREAL_YIELD_COL: pa.Column(float, pa.Check.gt(0), nullable=False),
        POP_COL: pa.Column(float, pa.Check.gt(0), nullable=False),
    },
    strict=False,
    coerce=True,
)

CALORIC_SUPPLY_SCHEMA = pa.DataFrameSchema(
    columns={
        "entity": pa.Column(str, nullable=False),
        "year": pa.Column(int, pa.Check.ge(1961), nullable=False),
        CALORIC_COL: pa.Column(float, pa.Check.between(500.0, 6000.0), nullable=False),
    },
    strict=False,
    coerce=True,
)

UNDERNOURISHMENT_SCHEMA = pa.DataFrameSchema(
    columns={
        "entity": pa.Column(str, nullable=False),
        "year": pa.Column(int, pa.Check.ge(2000), nullable=False),
        UNDERNOURISH_COL: pa.Column(
            float, pa.Check.between(0.0, 100.0), nullable=False
        ),
    },
    strict=False,
    coerce=True,
)
