# Logging Guide

Standards for structured, actionable logging across Python data and ML pipelines.

## 1. Key Rules

- Use one shared project logger, created once and imported where needed; do not call `logging.getLogger` in each module.
- Never log secrets, passwords, API keys, tokens, or PII.
- Only log what your orchestrator does not already emit.

## 2. What Orchestrators Already Log (Do Not Duplicate)

Pipeline orchestrators (such as Kedro, Dagster, Prefect, or Airflow) automatically emit:

- **Step start and finish:** `Running step: ...` / `Completed step: ...`
- **Dataset loading and saving:** `Loading data from ...` / `Saving data to ...`
- **Task progress:** `Completed N out of M tasks`
- **Pipeline completion time:** `Pipeline execution completed successfully in ...`

Do not add `logger.info("Starting step X")` or `logger.info("Saving output")`.

## 3. Mandatory Log Context

Every `WARNING` and `ERROR` log must tell an on-call engineer what happened without opening a debugger:

- **Entity:** dataset, step, or group identifier (`company_id`, `shuttle_type`)
- **Time window:** date range or period affected (formatted as `YYYY-MM-DD`)
- **Volume:** how many rows or groups the problem touched

```python
# Good — identifies entity, clean dates, and row count with a capped sample
logger.warning(
    "Missing %d week(s) in %s between %s and %s (sample: %s)",
    len(missing_dates),
    group_id,
    start_date.strftime("%Y-%m-%d"),
    end_date.strftime("%Y-%m-%d"),
    ", ".join(day.strftime("%Y-%m-%d") for day in missing_dates[:5]),
)
```

Log `merged.shape` at `DEBUG` after `pd.merge` to catch unintended Cartesian explosions early:

```python
merged = pd.merge(left_df, right_df, how="left", on=keys, validate="many_to_one")
logger.debug("Shape after merge: %s", merged.shape)
```

## 4. Log Levels & Exception Logging

| Level      | When to use                                                                       |
| ---------- | --------------------------------------------------------------------------------- |
| `DEBUG`    | Diagnostic details (shapes, intermediate counts) needed only when troubleshooting |
| `INFO`     | Meaningful pipeline milestones not already emitted by the orchestrator            |
| `WARNING`  | Unexpected condition or expected data deviation where execution continues         |
| `ERROR`    | Operation failed or data contract violated; include input context and exception   |
| `CRITICAL` | Fatal error preventing the program from continuing                                |

Never swallow exceptions with bare `except:` or log a vague message without input context:

```python
# Bad — bare except, deprecated warn(), no inputs or error details
try:
    compute_metrics(df, threshold)
except:
    logger.warn("compute_metrics failed")

# Good — specific exception, inputs and error included
try:
    compute_metrics(df, threshold)
except ValueError as err:
    logger.error(
        "compute_metrics failed for threshold=%s (rows=%d): %s",
        threshold,
        len(df),
        err,
    )
    raise
```

## 5. String Formatting & Anti-Patterns

| Context              | Format                                      | Reason                                                |
| -------------------- | ------------------------------------------- | ----------------------------------------------------- |
| `logger.*()` calls   | Lazy `%`: `logger.info("val: %s", val)`     | Avoids formatting when disabled; groups log templates |
| `raise` / exceptions | f-string: `raise ValueError(f"bad: {val}")` | Ruff `UP031` enforces f-strings outside logging       |
| General strings      | f-string                                    | Readability; Ruff `UP031`                             |

- **No f-strings in log calls** — always use lazy `%` formatting.
- **Never log raw `Timestamp` objects** — convert dates to `YYYY-MM-DD` strings first.
- **Never log unbounded lists** — limit each collection to 5–10 items and end with an `(and N more)` suffix.
- **No "I am here" logs** — never write `logger.info("Step 1")`.
- For data warnings, log the source and affected-row count while keeping credentials, tokens, URLs with query strings and personal data out of messages.
- Log milestones and useful shapes, not function-entry breadcrumbs.
