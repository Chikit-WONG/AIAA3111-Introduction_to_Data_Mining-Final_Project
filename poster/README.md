# Current poster source – V03.3

The selected poster is **800 x 1000 mm, portrait**. All diagrams, charts, tables and text are drawn from code. There are **no external image assets** to download or preserve. The PDF embeds fonts; the SVG retains editable text and vector geometry.

## Rebuild

From the repository root (or the extracted `Poster_source.zip` root):

```powershell
python -m pip install -r poster/requirements-render.txt
python scripts/build_poster.py
```

The V03.3 print build was checked on Windows with Python 3.11.7. Install the separate rendering requirements even if the experiment dependencies are already installed.

The fonts are Arial Regular/Bold, Consolas, and Microsoft YaHei Regular/Bold: `arial.ttf`, `arialbd.ttf`, `consola.ttf`, `msyh.ttc`, `msyhbd.ttc`. By default they are read from `C:\Windows\Fonts`. Fonts are not distributed in this repository. On another system, provide the same files in a local directory and set `POSTER_FONT_DIR` to that directory before building. This preserves the intended text metrics.

```powershell
$env:POSTER_FONT_DIR = 'D:\my-poster-fonts'
python scripts/build_poster.py
```

The command publishes:

- `artifacts/Poster.pdf`: print PDF at the exact physical dimensions.
- `artifacts/Poster.svg`: editable vector source output.
- `artifacts/Poster_preview.png`: screen preview of this version.
- `artifacts/Poster_source.zip` contains the current source, data snapshot, bilingual speaking notes and the three outputs above.

Intermediate render checks, detail crops and scene JSON go into ignored `poster/build/`. They are not included in the source archive. Rebuilding does not rerun mining or call any AI/model service.

## Files

- `build_poster.py`: current layout and all drawing geometry.
- `scene_engine.py`: common SVG/PDF rendering and physical-size/text checks.
- `poster_data.json`: saved experimental values used in the poster.
- `requirements-render.txt`: rendering dependencies.
- [Presentation script and Q&A](Presentation_Script_EN_ZH.md) pairs the three-minute English talk with Chinese rehearsal text. A two-minute Q&A follows. This is the speaking file included in the source archive.

The four past-order receipts illustrate baskets containing both A and B. The caption defines confidence over all orders containing A. In the nine-cell test grid, the vertical discovery-confidence label sits beside the three row percentages, and discovery support labels the columns. For printing, use `artifacts/Poster.pdf` at 100% scale. The build verifies the page dimensions, embedded fonts and absence of raster images.

## Result definitions

One rule-month is one rule checked in one month. The group of 71 rules ranked first in June-July validation among groups with at least 20 rules. It passed 111 of 142 rule-months (78.2%). The same 71 rules were frozen before August-November testing. They passed 225 of 284 rule-months (79.2%), and 46 passed in all four test months. A pass requires monthly support of at least 0.5%, confidence of at least 50%, lift of at least 1.2, at least 20 orders containing the antecedent and an observed consequent. All 71 rules count toward each month's denominator. The grid reports test retention for each original group.

Of the 17,901 study orders, 17,157 enter discovery (7,365), validation (2,696) or testing (7,096). The other 744 orders come from December 1-9, 2011 and enter a separate supplementary analysis.

No abandoned poster versions, generated-image candidates, API call records, before/after comparisons, local source-history snapshots or font files are included in this package.
