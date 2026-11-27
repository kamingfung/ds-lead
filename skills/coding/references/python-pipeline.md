# Code Style Guide

Practical Python coding standards for data and ML pipelines.

## Before You Write

Stop at the first rung that holds. Only descend when the rung above genuinely does not fit:

1. **Does this need to exist at all?** Speculative need -> skip it (YAGNI).
2. **Does stdlib cover it?** Use it instead of hand-rolling.
3. **Does an already-installed dependency cover it?** Use it; never add a dependency for what a few lines can do.
4. **Can it be one line?** Write one line.
5. **Only then:** write the minimum code that works — no scaffolding, no "for later".

If you consciously stop above a full implementation because a simpler form holds for now, leave a plain-words comment naming the limit (with a number) and the upgrade path (no tag word; mention "deliberate simplification" in the PR description):

```python
# Linear scan; fine below ~10k rows. Switch to an index lookup above that.
match = next((r for r in records if r["id"] == target_id), None)
```

## 1. Functional & Pure Style

- **Pure functions:** same inputs produce the same outputs; never mutate arguments or globals in place. Always `.copy()` mutable DataFrames, dicts, or lists before modifying.
- **Avoid `inplace=True`:** return a new object (`df_sorted = df.sort_values("a")`); `inplace` mutates callers and gives no speed benefit in pandas.
- **Avoid mutable default arguments:** default to `None` and initialize inside the function (`quantiles: list[float] | None = None`).
- **Split the decision from the action:** write a pure predicate/decision function and a separate function that executes side effects so the decision is unit-testable with a tiny DataFrame and no mocks.
- **Keep functions small:** aim for ~30 body lines or fewer (excluding signature, docstring, comments, and blank lines; longer is fine with a stated reason).
- **Readable pandas:** one or two related operations per line; break long chains into named intermediate variables.

```python
# Bad — mutates input in place and uses mutable default
def filter_shuttles(df: pd.DataFrame, types: list[str] = ["Type A"]) -> pd.DataFrame:
    df.dropna(subset=["price"], inplace=True)
    return df[df["shuttle_type"].isin(types)]


# Good — pure function, safe default
def filter_shuttles(df: pd.DataFrame, types: list[str] | None = None) -> pd.DataFrame:
    if types is None:
        types = ["Type A"]
    valid = df.dropna(subset=["price"])
    return valid[valid["shuttle_type"].isin(types)].copy()
```

## 2. Readability & Signatures

- **Descriptive, pronounceable names:** `current_date` instead of `ymdstr`; `company` instead of `item` in loops; `locations` instead of `location_tuple`.
- **One concept, one name:** do not mix `client`, `customer`, and `account` for the same entity.
- **One English variant for all artifacts:** identifiers, docstrings, comments, commit messages, YAML keys, and logs follow the repository's variant (see `SKILL.md`, Consistent Language Style).
- **Keep signatures small (`≤5` arguments):** group related parameters into a `dict` or dataclass when larger.
- **Keyword arguments for `>2` arguments:** use keyword arguments in both `src/` and `tests/` so signature reordering cannot silently swap values.
- **No boolean flag parameters:** split `f(x, flag=True)` into two clearly named functions.
- **Google-style docstrings** on every public function, and on any private function whose purpose is not clear from its name and signature: start the summary on a new line after `"""`, include types in the signature, and list output DataFrame columns in `Returns:` separated by `|`.

## 3. Top-Down Function Ordering

Arrange functions so readers encounter callers before callees:

1. **Node function first** (the public function registered in `pipeline.py`).
2. **Its helpers immediately after**, ordered by first appearance in the node body.
3. **Helpers of helpers** follow their parent helper.
4. **Shared helpers** belong under their first consumer (by `pipeline.py` registration order); do not duplicate or repeat them below later callers.

## 4. Fail Loud, Guard Clauses & Data Integrity

- **Guard clauses first:** validate preconditions and return or raise at the top so the happy path is never nested.
- **Strict config reads:** read required config with `params["key"]`, never `.get(key, default)`.
- **Three-tier error handling:**
  1. Anticipated + auto-fixable -> `try`/`except` with a specific exception type (never bare `except`).
  2. Anticipated + unfixable -> `raise ValueError(...)` naming the dataset, columns wanted, and columns/values present.
  3. Expected deviation -> `logger.warning(...)` with entity, window, and row count (see [logging.md](logging.md)).
- **Errors a caller branches on:** use a plain `ValueError` with a clear message when nothing branches on the failure; subclass `ValueError` only when a caller catches that specific failure to recover. Never match on exception message text or pack error codes into `args[0]`.
- **Own the ingestion boundary:** map external/raw column names to internal names once in the ingestion node; downstream nodes use internal names only.
- **Model state honestly:** use separate schemas (Pandera, for example) for raw vs. cleaned data rather than reusing one schema with `nullable=True` columns that are guaranteed non-null after cleaning.
- **No silent fallbacks:** avoid `fillna`, `drop(..., errors="ignore")`, `dropna`, truncating `.astype(int)`, inner joins that drop rows, or last-write-wins dedup without counting and logging affected rows; a deliberate fallback logs that count or carries an indicator column.
- **Empty in, empty out:** return an empty schema-compliant DataFrame (`Schema.empty()`) for empty inputs.

```python
def weighted_mean_price(
    df: pd.DataFrame, weight_col: str = "passenger_capacity"
) -> float:
    """
    Compute capacity-weighted mean shuttle price.

    Args:
        df: Shuttle records containing price and weight_col.
        weight_col: Column carrying positive weights.
    Returns:
        float: Weighted mean price, or nan when no scoreable rows exist.
    Raises:
        ValueError: Required columns are missing.
    """
    missing = {"price", weight_col} - set(df.columns)
    if missing:
        raise ValueError(
            f"weighted_mean_price requires {sorted(missing)}; got {sorted(df.columns)}"
        )
    usable = df.dropna(subset=["price", weight_col])
    if usable.empty:
        return float("nan")
    return float(
        (usable["price"] * usable[weight_col]).sum() / usable[weight_col].sum()
    )
```

## 5. Pandas & Time-Series Best Practices

- **Always name `pd.merge()` arguments:** explicitly pass `left`, `right`, `on`, `how`, and `validate` (`"one_to_one"`, `"many_to_one"`).
- **Sort before `groupby` on floats:** floating-point addition is not associative; sort by grouping + aggregation keys first (`df.sort_values(["group", "val"]).groupby("group")["val"].sum()`) for bitwise reproducibility.
- **Time operations inside `groupby`:** run `ffill`, `bfill`, `shift`, and rolling windows inside `groupby` on entity keys so values never leak across entities.
- **Time-based rolling windows:** sort by the timestamp column, set it as index, and use time-based window strings (`f"{n_weeks * 7}D"`) rather than integer row counts (`window=3`), which break when dates are missing.
- **Avoid `iloc` for temporal slicing:** filter with explicit date comparisons (`df[df["date"] >= cutoff]`) instead of `df.iloc[-3:]`.
- **Sort before position-based selection:** sort by the time or key column before selecting by position; prefer label or boolean filtering when order is not part of the contract.
- **Pair ISO week with ISO year:** always pair `isocalendar().week` with `isocalendar().year`, never with calendar `.dt.year`.
- **Keep units consistent:** convert units once at the ingestion boundary and keep internal tables in one unit.
- **Keep source and internal columns distinct:** rename source columns once at ingestion, then use internal names downstream.
- **Use timezone-aware timestamps:** make timezone expectations explicit when data crosses system or regional boundaries.

## 6. Constants & Scalability

- Keep a constant local to its function until a second function reads it; then move it to module top or a shared constants module annotated `Final` (`MAX_CAPACITY: Final[int] = 1_000`).
- Group related constants in one immutable container (namedtuple, frozen dataclass or `Enum`); use an `Enum` when the set of values is closed and callers must handle every member.
- Profile before optimizing (use `ProfileHook`); optimize in order: vectorized pandas/NumPy operations -> parallel execution -> targeted algorithmic changes. Never iterate row-by-row with `.iterrows()`.
- Add type hints to public functions and document input and output contracts when the types do not make them obvious.
- Keep functions short enough to read in one screen; split a function when it mixes orchestration, transformation and I/O.

## Where explanation belongs

When a name alone is not enough, follow the cascade and stop at the first level that suffices:

1. **Descriptive name** — rename the variable or function; no comment needed.
2. **Concise inline comment** — one short phrase if the name still leaves ambiguity.
3. **Docstring** — when the _why_ behind a function needs a paragraph.
4. **External doc** — when detail exceeds the scope of a single function. Route by stability:

| Content type                                         | Reproducible & stable? | Where it goes                   |
| ---------------------------------------------------- | ---------------------- | ------------------------------- |
| Design decisions, parameter semantics, architecture  | Yes                    | `docs/`                         |
| Experiment tables, backtest numbers, arm comparisons | No (branch-specific)   | `changelogs/` or PR description |
| Branch rationale that may change before merge        | No                     | `changelogs/` or PR description |
