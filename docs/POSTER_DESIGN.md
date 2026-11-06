# Poster design and reproduction

The current design is a one-page A1 landscape poster (841 × 594 mm), provisionally retained until the course specifies the final dimensions. The PDF is generated from the project's saved experimental evidence. The report and experiment results are unchanged.

## Reading order

1. The title and finding strip establish the question and the primary result: 225 of 284 held-out rule-months pass all gates, 46 of 71 rules persist in all four months, and 99.3% of rule-months are evaluable.
2. The left column explains chronological discovery, validation and testing, the four common evaluation gates, and the data audit. Its lower section and the conclusion band complete the page instead of leaving an unused lower-left area.
3. The center column shows four monthly outcomes, one square per frozen rule, and population sensitivity. Percentages use the declared frozen-rule denominator.
4. The right column distinguishes rule quantity from retention and observability, marks the validation-selected cohort, and compares the two mining implementations. The 14-rule cohort remains visibly outside the declared selection floor.
5. The conclusion band states the practical interpretation and limitations. Sources, AIGC disclosure and a clickable repository QR code remain visible in the footer.

## Visual system

- Navy establishes the heading hierarchy, teal marks retained rules, pale gray marks failed criteria, and amber marks insufficient evidence or the selected grid cell.
- Title: 72 pt; section headings: 31 pt; main explanatory text: 22–28 pt; chart annotations: 18–25 pt. Footnotes are 16–17.5 pt at A1 size.
- All charts, rule markers and the QR code are vector paths. The PDF contains no raster chart images.
- The two embedded DejaVu Sans font weights come from Matplotlib's bundled fonts, avoiding a dependency on fonts installed on one team member's computer.
- Layout helpers check text bounds, and the builder verifies key count and algorithm-signature relationships before writing the poster. Re-render and visually inspect after editing prose or layout.

## Reproduce

From the code repository with its dependencies installed:

```powershell
.\.venv\Scripts\python.exe scripts/build_poster.py
```

This writes `artifacts/Poster.pdf` and a temporary text-bound record in `tmp/poster_qa/poster_layout.json`. No new mining or statistical analysis runs.

To regenerate the screen preview with Poppler available on PATH:

```powershell
pdftoppm -singlefile -scale-to 2400 -png artifacts/Poster.pdf artifacts/Poster_preview
```

The same design can be scaled to A0 with `--size A0 --output artifacts/Poster_A0.pdf`. This is an optional print-size setting; A1 remains the current deliverable. A different board aspect ratio requires a layout review rather than stretching a preview image.

## Evidence map

| Poster element | Saved evidence |
|---|---|
| Main findings | `results/summary.json` |
| Data size | `results/data_profile.json` |
| Timeline counts | `results/tables/splits.csv` |
| Monthly outcomes | `results/tables/monthly_retention.csv` |
| Persistence squares | `results/tables/stability_distribution.csv` |
| Population sensitivity | `customer_sensitivity.csv`, `basket_size_sensitivity.csv` under `results/tables/` |
| Threshold grid and observability | `threshold_sensitivity.csv`, `threshold_evaluability.csv` under `results/tables/` |
| Selected policy and common gates | `results/selection.json` |
| Timing and output equivalence | `results/tables/benchmark.csv` |

## Design references

The result-first hierarchy, concise text, readable type and directly labeled figures follow the scientific-poster principles in [APS's poster design advice](https://www.aps.org/careers/advice/designing-poster-presentation). The [NeurIPS 2026 poster instructions](https://neurips.cc/Conferences/2026/PosterInstructions) and [ICML 2026 poster instructions](https://icml.cc/Conferences/2026/PosterInstructions) specify venue-dependent print dimensions and delivery requirements. The course's eventual dimensions govern this submission.
