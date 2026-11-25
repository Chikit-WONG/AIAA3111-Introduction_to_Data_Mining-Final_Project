# Current poster design and reproduction – V03.2

The print poster is **800 x 1000 mm, portrait**. V03.2 builds on the team's three-column design. Python draws the charts, diagrams, tables and text as vectors.

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
- Four receipts illustrate co-purchases, each showing both A and B. The caption defines confidence as the fraction of orders containing A that also contain B.
- In the retention grid, the vertical discovery-confidence title runs beside the 30%, 50% and 70% row labels. Discovery support sits above the columns. Each cell reports mean test retention and the original rule count.
- The builder checks page size, embedded fonts, the absence of raster images, required text, text widths, page boundaries and overlaps. PDF previews and detail crops are in `poster/build/qa/`.

## Saved evidence

`poster/poster_data.json` is the compact snapshot used for drawing: benchmark medians, nine candidate-group sizes/test retention and four monthly selected-cohort outcomes. Original experimental evidence remains under `results/` and the full protocol under [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md). The 14-rule group is below the 20-rule selection floor despite its observed 100% test retention.

The uploaded [Chinese reference notes](../poster/海报讲解稿_中文_参考.md) preserve the latest user-edited draft; their legacy heading/timing has not yet been retimed for the confirmed three-minute presentation.
