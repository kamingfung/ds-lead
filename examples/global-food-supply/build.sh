#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p data
if [[ "${1:-}" == "--refresh" ]] || [[ ! -f data/cereal_index.csv ]]; then
  curl -fsSL "https://ourworldindata.org/grapher/index-of-cereal-production-yield-and-land-use.csv?v=1&csvType=full&useColumnShortNames=true" -o data/cereal_index.csv
  curl -fsSL "https://ourworldindata.org/grapher/daily-per-capita-caloric-supply.csv?v=1&csvType=full&useColumnShortNames=true" -o data/caloric_supply.csv
  curl -fsSL "https://ourworldindata.org/grapher/prevalence-of-undernourishment.csv?v=1&csvType=full&useColumnShortNames=true" -o data/undernourishment.csv
fi

uv sync --quiet
uv run ruff check .
uv run pytest -q
uv run python build_deck.py
uv run python build_report.py
echo "Built examples/global-food-supply/deck.html, deck.pptx and report.html"
