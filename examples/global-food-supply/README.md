# Global Food Supply Readout (1961–2024)

An end-to-end, reproducible example built with [`ds-lead`](../../README.md) answering: **Does global food production satisfy population growth, and where should 2027–2030 ag-tech capital go?**

## What it demonstrates

- **Structured problem solving:** Avoids the aggregate trap ("global calories rose, so yes") by decomposing into aggregate yield vs. land growth, regional caloric divergence, and human undernourishment.
- **Production engineering:** Validates three public [Our World in Data](https://ourworldindata.org/) / FAOSTAT / UN WPP CSVs with [Pandera](schemas.py) schemas and unit tests (`tests/test_build_deck.py`).
- **Deck and report from one set of figures:** `build_deck.py` builds a `spec.Deck` on the make-deck kit in `skills/make-deck/template/` and writes:
  - [`deck.html`](deck.html): a self-contained 1280x720 readout with a `Backup · Sources` table.
  - [`deck.pptx`](deck.pptx): an editable PowerPoint copy of the same slides.
  - [`report.html`](report.html): an interactive one-pager (section filters, a regional inspector, a capital reallocation explorer), filled from the same `Num` values and chart specs.

## Build

```bash
./build.sh            # validate, test, and build deck.html, deck.pptx and report.html from cached data/
./build.sh --refresh  # re-download public OWID CSVs first
```

To print the deck to PDF:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=deck.pdf deck.html
```
