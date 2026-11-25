# Current poster design and reproduction - V03.1

The selected poster is **800 x 1000 mm, portrait**. It uses the user-approved all-vector V03 layout with local V03.1 corrections. All charts, diagrams, tables and text are generated from code; there are no external image assets. The report and experiment values are unchanged.

## Reading order

1. Header: title, course identifier, Group 11, members and three main results: 79.2% mean monthly retention, 46/71 passing all four test months, identical itemsets for Apriori and FP-Growth.
2. Left: research question, historical/future-order illustration, raw records, dataset information, preprocessing and invoice-level transaction aggregation.
3. Middle: discovery -> validation -> frozen-rule monthly testing; shared monthly criteria are stated once. The selected 71 rules remain in every month's denominator.
4. Right: mining time and peak process memory, the full test-retention grid, integrated interpretation and selected-cohort monthly outcomes.
5. Footer: data/method sources, AIGC disclosure and code link. There is no separate conclusion/limitations panel.

## Rebuild

```powershell
python -m pip install -r poster/requirements-render.txt
python scripts/build_poster.py
```

See [poster/README.md](../poster/README.md) for font requirements and the reference speaking notes. This command creates `artifacts/Poster.pdf`, `Poster.svg`, `Poster_preview.png` and `Poster_source.zip`, using saved poster values without re-running mining or calling AI services. The archive contains only this version's source, dependencies, output files and reference notes. Local QA crops and abandoned designs are excluded.

## Visual system and checks

- White background, black structural lines and blue emphasis; three columns and large readable type.
- Main body about 27-31 pt; auxiliary labels at least 24 pt; key grid values about 42.5 pt. Source footer is about 20 pt. SVG text and geometry stay editable; PDF embeds the installed font subsets.
- V03.1 uses a complete black grid plus a separate blue InvoiceNo frame, fixes calendar title/binding collisions, replaces the inline `->` with a proper arrow, branches the frozen-rule connector toward all four months, and gives every month card identical black borders.
- The builder checks one-page physical size, required identity text, text widths, page boundaries and text overlap. Actual PDF previews should also be inspected after layout changes. Intermediate checks are in ignored `poster/build/qa/`.

## Saved evidence

`poster/poster_data.json` is the compact snapshot used for drawing: benchmark medians, nine candidate-group sizes/test retention and four monthly selected-cohort outcomes. Original experimental evidence remains under `results/` and the full protocol under [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md). The 14-rule group is below the 20-rule selection floor despite its observed 100% test retention.

The uploaded [Chinese reference notes](../poster/海报讲解稿_中文_参考.md) preserve the latest user-edited draft; their legacy heading/timing has not yet been retimed for the confirmed three-minute presentation.
