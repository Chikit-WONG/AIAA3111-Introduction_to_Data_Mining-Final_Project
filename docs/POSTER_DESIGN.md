# Current poster design and reproduction – V04.0

The English print poster is **800 x 1000 mm, portrait**. V04.0 keeps the content, numbers and three-column reading order of V03.3 and restyles the page after the course poster templates. Python draws the charts, diagrams, tables and text as vectors.

## Reading order

1. The header identifies the course and reports mean monthly test retention (225/284), rules passing all four months (46/71) and agreement between the two mining algorithms.
2. The left column traces a co-purchase from a raw invoice to a basket, then accounts for the 17,157 main-study orders and 744 supplementary orders.
3. The middle column reports validation retention (111/142) beside the selected group and shows where the 71 rules were frozen. A rule-month is one rule checked in one month.
4. The right column shows benchmark costs, the nine groups' test retention and monthly outcomes. The selected group's aggregate test result sits directly below the grid.
5. Footer: data/method sources, AIGC disclosure and code link. There is no separate conclusion/limitations panel.

## Rebuild

```powershell
python -m pip install -r poster/requirements-render.txt
python scripts/build_poster.py
```

See [poster/README.md](../poster/README.md) for font requirements and the bilingual speaking file. This command creates `artifacts/Poster.pdf`, `Poster.svg`, `Poster_preview.png` and `Poster_source.zip` from the saved results. The archive includes the build files, the three poster formats and the current talk with Q&A.

## Visual system and checks

- Navy header and footer bands with the HKUST(GZ) mark; three white column cards with navy title bars; large readable type.
- Colour roles: navy for structure and headings, blue for data and emphasis, gold only for the selected 71-rule group (and header trim). In the benchmark charts Apriori is blue and FP-Growth is teal; the pair was checked for colour-vision separation and contrast.
- Headline cards carry ring gauges for 225/284 and 46/71. A split bar under the left column shows how the 17,901 orders divide into discovery, validation, test and the December 1-9 supplement.
- Main body about 27-31 pt; auxiliary labels at least 24 pt; key grid values about 42.5 pt. Source footer is about 20 pt. SVG text and geometry stay editable; PDF embeds the installed font subsets.
- Four receipts illustrate co-purchases, each showing both A and B. The caption defines confidence as the fraction of orders containing A that also contain B.
- In the retention grid, the vertical discovery-confidence title runs beside the 30%, 50% and 70% row labels. Discovery support sits above the columns. Each cell reports mean test retention and the original rule count. Cells darken with retention; the selected group has a gold outline and the ineligible 14-rule group is grey with a dashed edge.
- The builder checks page size, embedded fonts, required text, missing glyphs, text widths, page boundaries and overlaps. The logo must be the only raster image and print at 300 dpi or more. PDF previews and detail crops are in `poster/build/qa/`.

## Saved evidence

`poster/poster_data.json` stores benchmark medians, candidate-group sizes and retention, the two validation months, the four test months and the order counts. The underlying monthly counts are in [monthly_retention.csv](../results/tables/monthly_retention.csv) and [splits.csv](../results/tables/splits.csv). The 14-rule group falls below the 20-rule selection floor. See the [experiment protocol](EXPERIMENT_PROTOCOL.md).

The [bilingual script](../poster/Presentation_Script_EN_ZH.md) gives each speaker a pointing cue and a timed English passage, with Chinese alongside. The two-minute Q&A starts after the three-minute talk.
