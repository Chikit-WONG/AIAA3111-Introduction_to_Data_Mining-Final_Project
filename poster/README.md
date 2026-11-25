# Current poster source – V03.2

The selected poster is **800 x 1000 mm, portrait**. All diagrams, charts, tables and text are drawn from code. There are **no external image assets** to download or preserve. The PDF embeds fonts; the SVG retains editable text and vector geometry.

## Rebuild

From the repository root (or the extracted `Poster_source.zip` root):

```powershell
python -m pip install -r poster/requirements-render.txt
python scripts/build_poster.py
```

The V03.2 print build was checked on Windows with Python 3.11.7. Install the separate rendering requirements even if the experiment dependencies are already installed.

The fonts are Arial Regular/Bold, Consolas, and Microsoft YaHei Regular/Bold: `arial.ttf`, `arialbd.ttf`, `consola.ttf`, `msyh.ttc`, `msyhbd.ttc`. By default they are read from `C:\Windows\Fonts`. Fonts are not distributed in this repository. On another system, provide the same files in a local directory and set `POSTER_FONT_DIR` to that directory before building. This preserves the intended text metrics.

```powershell
$env:POSTER_FONT_DIR = 'D:\my-poster-fonts'
python scripts/build_poster.py
```

The command publishes:

- `artifacts/Poster.pdf`: print PDF at the exact physical dimensions.
- `artifacts/Poster.svg`: editable vector source output.
- `artifacts/Poster_preview.png`: screen preview of this version.
- `artifacts/Poster_source.zip`: only the current source, data snapshot, reference speaking notes and the three outputs above.

Intermediate render checks, detail crops and scene JSON go into ignored `poster/build/`. They are not included in the source archive. Rebuilding does not rerun mining or call any AI/model service.

## Files

- `build_poster.py`: current layout and all drawing geometry.
- `scene_engine.py`: common SVG/PDF rendering and physical-size/text checks.
- `poster_data.json`: saved experimental values used in the poster.
- `requirements-render.txt`: rendering dependencies.
- `海报讲解稿_中文_参考.md`: latest user-edited Chinese speaking notes, copied without revising their content. This is a reference draft: its legacy five-minute heading and timing have not been reconciled with the confirmed three-minute presentation limit.

The four past-order receipts illustrate baskets containing both A and B. The caption defines confidence over all orders containing A. In the nine-cell test grid, the vertical discovery-confidence label sits beside the three row percentages, and discovery support labels the columns. For printing, use `artifacts/Poster.pdf` at 100% scale. The build verifies the page dimensions, embedded fonts and absence of raster images.

## Result definitions

The 71 rules were selected on June-July validation among candidate groups with at least 20 rules. They are frozen for August-November testing. Common monthly gates are support >=0.5%, confidence >=50%, lift >=1.2, at least 20 antecedent orders, and an observed consequent. Every rule stays in each month's denominator, including insufficient-evidence cases. The grid shows mean **test** retention and original group sizes. The 14-rule group's 100% does not make it eligible for validation selection.

No abandoned poster versions, generated-image candidates, API call records, before/after comparisons, local source-history snapshots or font files are included in this package.
