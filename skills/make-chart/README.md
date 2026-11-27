# Chart Palette

[`palette.css`](palette.css) holds the house "fall" palette. A person picked the colors by hand. The hue roles follow the Okabe-Ito color-universal-design palette, and tests check that the series colors stay apart for readers with color-vision deficiency.

## Where the colors come from

Okabe and Ito (2008) published eight colors chosen to stay distinct for people with the common types of color-vision deficiency. Wong (2011) reprinted them in _Nature Methods_. Only `--yellow` and `--black` are Okabe-Ito values. Every other series color is a darker, muted fall color in the same hue family.

ΔE is the CIE 1976 color difference in CIELAB. A larger number means two colors look more different.

| Okabe-Ito color | Hex       | House token                     | ΔE   |
| --------------- | --------- | ------------------------------- | ---- |
| orange          | `#e69f00` | `--orange` (ochre)              | 13.9 |
| sky blue        | `#56b4e9` | `--sky`                         | 16.7 |
| bluish green    | `#009e73` | `--green` (sage)                | 33.4 |
| blue            | `#0072b2` | `--blue` (indigo)               | 28.4 |
| vermillion      | `#d55e00` | `--red` (rust)                  | 33.2 |
| reddish purple  | `#cc79a7` | none: `--purple` is a red-brown | -    |
| yellow, black   |           | `--yellow`, `--black`           | 0    |

## What was checked

`simulate_vision` shows each color as a viewer with one deficiency sees it. The closest pair of the five series colors (`CATEGORICAL`) is ink and burnt sienna, two dark red-browns.

| Vision       | Closest pair, ΔE |
| ------------ | ---------------- |
| normal       | 19.9             |
| deuteranopia | 17.0             |
| protanopia   | 12.7             |
| tritanopia   | 22.2             |

Ink and burnt sienna are hard to tell apart on thin lines and small markers under protanopia. Give the fifth series a second cue: a line style, a marker shape or a direct label.

## Change the colors

1. Edit the hex values in `palette.css`. Keep the token names, because `chart_style.py` and the deck theme read them. To try a variant, copy the file and set `CHART_STYLE_PALETTE` to its path before you import `chart_style`.
2. Keep each token's role. The comment on each line says what the color is for.
3. Change the same colors in `Theme` in [`skills/make-deck/template/theme.py`](../make-deck/template/theme.py). The deck and the charts share one palette.
4. Run the tests from `skills/make-chart/`. A test fails when two series colors come closer than ΔE 10 under any vision type.

   ```bash
   uv run --python 3.12 --with matplotlib==3.9.2 --with numpy==2.1.3 --with seaborn --with pytest pytest -q test_chart_style.py
   ```

5. Call `show_all_palettes()` and look at the three simulated rows.
6. Regenerate the pictures in [`examples/make-chart/`](../../examples/make-chart/) with the command in its README.
7. Add one line to `CHANGELOG.md` under Unreleased.

## Sources

- Okabe, M. and Ito, K. "Color Universal Design (CUD): How to make figures and presentations that are friendly to colorblind people" (2008). https://jfly.uni-koeln.de/color/
- Wong, B. "Points of view: Color blindness." _Nature Methods_ 8, 441 (2011). https://doi.org/10.1038/nmeth.1618
