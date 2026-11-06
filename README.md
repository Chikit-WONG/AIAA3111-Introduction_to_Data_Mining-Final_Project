# Beyond Frequent Co-Purchases

A reproducible AIAA3111 Group 11 project on temporal stability of retail association rules.

**Team:** Chi Kit WONG (50012338), Yuxuan OUYANG (50013526), Zhicheng SUN (50012546).

The selected 71-rule cohort has **79.2% mean monthly retention** in August-November 2011; **46 rules persist in all four months**. These are descriptive results under declared thresholds, not a prediction of retail revenue or a causal claim. Restricting the evaluation population to orders with a recorded CustomerID reduces retention to 64.8%; excluding baskets above 100 products reduces it to 62.3%.

## Run locally

Python 3.11 was used. The computations run on CPU; no GPU, server or paid API is required. In PowerShell, from this repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe run.py all
```

On Linux/macOS use `.venv/bin/python` for the equivalent commands. The source download requires internet access the first time. Subsequent runs verify the existing workbook's SHA-256. Pickle files are **local generated caches**; never replace them with untrusted downloaded pickle files.

The individual stages are available as `download`, `prepare`, `pilot`, `experiment`, `supplement`, `figures`, and `verify`. `all` rebuilds the analysis from the verified raw workbook, including the supplements, figures and verification. The optional `pilot` uses the first 2,000 discovery invoices solely as a feasibility check and is not the reported benchmark. Run it after `prepare`.

```powershell
.\.venv\Scripts\python.exe run.py prepare
.\.venv\Scripts\python.exe run.py pilot
.\.venv\Scripts\python.exe run.py experiment
.\.venv\Scripts\python.exe run.py supplement
.\.venv\Scripts\python.exe run.py figures
.\.venv\Scripts\python.exe run.py verify
```

The measured benchmark workers used under 160 MiB each; mining took approximately 0.3-5.7 seconds per run in the recorded experiment. This is **worker-process memory**, not a measurement of the entire cleaning pipeline. The core experiment took about 71 seconds on the local Ryzen 9 7940H. Timings will vary. The runner enforces a 12 GiB worker limit and a 600-second per-run timeout. Lower support or longer itemsets can be substantially more expensive.

## Data and methodology

- Source: [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), Daqing Chen (2015), DOI [10.24432/C5BW33](https://doi.org/10.24432/C5BW33), CC BY 4.0.
- The official download contains 541,909 line items, not that many independent orders. The workbook and its checksum are preserved locally; `data/source_manifest.json` records provenance.
- Sequential cleaning produces 522,537 positive-sales lines and 19,773 baskets across all countries; the primary UK population has 17,901 baskets. Cancellation/return rows are removed, but purchases are not netted against later returns.
- Missing CustomerID does not invalidate an order-level basket. Codes, rather than descriptions, identify products. Valid alphanumeric codes and singleton baskets are preserved.
- Discovery: December 2010-May 2011 (7,365 UK orders). Validation: June-July (2,696). Test: August-November (7,096). December 2011 is incomplete and kept only as a supplement.
- Apriori (`low_memory=True`) and FP-Growth use identical Boolean inputs and maximum itemset length 3. Only single-item consequents are generated. Exact bounded itemsets and integer support counts must agree.
- Discovery grid: support 0.5%, 1%, 2%; confidence 30%, 50%, 70%; lift at least 1.2.
- Common monthly evaluation: support at least 0.5%, confidence at least 50%, lift at least 1.2, antecedent count at least 20.
- Selection: maximum mean validation retention, requiring at least 20 discovery rules. Tie-breaks are documented in `configs/experiment.json`. The selected setting is support 2%, confidence 50%.
- A fixed rule cohort is evaluated in every month. Missing and underpowered rules remain in the retention denominator; coverage and conditional retention are reported separately.
- The 14-rule configuration has 100% observed test retention but fails the primary rule-count floor. This trade-off is disclosed, not hidden. Post-hoc diagnostics are labeled in `results/supplemental_protocol.json`.

The detailed experimental definitions and limitations are in [docs/EXPERIMENT_PROTOCOL.md](docs/EXPERIMENT_PROTOCOL.md).

## Repository contents

| Path | Purpose |
|---|---|
| `retail_rules/` | Download, cleaning, mining, evaluation, benchmarks, figures and verification |
| `configs/` | Experiment and team metadata |
| `tests/` | Independent toy-data and boundary-case tests |
| `data/source_manifest.json` | Source URL, attribution and checksum |
| `data/raw/`, `data/processed/` | Locally generated, ignored data and caches |
| `results/tables/` | Inspectable calculations and per-rule evidence |
| `results/figures/` | PNG and editable SVG figures |
| `results/protocol.json`, `results/selection.json` | Configuration and pre-test selection records |
| `results/verification.json` | Scope and result of independent numerical checks |
| `docs/PRESENTATION_NOTES.md` | Chinese explanation, English pitch and defense questions |
| `artifacts/Poster.pdf` | Vector research poster; provisional A1 landscape layout |
| `artifacts/Poster_preview.png` | Screen preview of the current poster |
| `scripts/` | Optional document build and submission packaging tools |

## Collaborative report in Overleaf

The report has its own [GitHub/Overleaf repository](https://github.com/Chikit-WONG/AIAA3111-Introduction_to_Data_Mining-Final_Project-Report), cloned beside this repository with the suffix `-Report`.

```powershell
.\.venv\Scripts\python.exe run.py export-report
```

This refreshes the report's `generated/`, `figures/` and `evidence/` files, preserving `main.tex` and `sections/` for collaboration. For another location pass `--report-dir "path"`. The report must be re-read after an experimental change: automated export updates values and figures, not interpretation in prose.

Compile `main.tex` in Overleaf with pdfLaTeX or XeLaTeX. For optional local Windows preview, `scripts/bootstrap_tex.py` downloads a SHA-256-verified portable Tectonic to ignored `tools/bin/`; `scripts/build_report.ps1` compiles to the report's `Report.pdf`. Its initial run downloads TeX packages into ignored `tools/cache/`. No manuscript is sent to a remote compilation service.

## Deliverables and team review

After building the report, run scripts/check_report_layout.py with the project Python environment to verify the 10-page main text and detect large unused areas at page bottoms, including disclosures, references and appendices. It writes the measured page baselines to the report repository's build/layout_check.json. This automated check complements visual page review.

The figure stage also writes vector PDFs for the manuscript, including a method overview and a threshold/observability comparison. The paper_figures module records additional descriptive diagnostics in results/report_diagnostics.json; it asserts that the original confidence gate reproduces every primary retained indicator. No test result triggers new parameter selection. The revised report has 10 main-text pages and 13 pages in total.

The course requires `Report.pdf` (6-10 main-text pages; references, disclosures and appendix excluded), code, README and data/download instructions inside `Group_11_Project.zip`. `Poster.pdf` is submitted separately. `scripts/package_submission.py` assembles this layout after the report and poster are built. Full public data are reproducible using the supplied download command; the ZIP excludes raw data, virtual environments, caches and tool binaries.

After reviewing the manuscript, rebuild the local deliverables in PowerShell:

```powershell
.\.venv\Scripts\python.exe run.py export-report
.\.venv\Scripts\python.exe scripts/bootstrap_tex.py
.\scripts\build_report.ps1
.\.venv\Scripts\python.exe scripts/build_poster.py
.\.venv\Scripts\python.exe scripts/package_submission.py
```

The outputs are `Report.pdf` in the adjacent report repository, `artifacts/Poster.pdf`, and `dist/Group_11_Project.zip` here. After the first successful TeX build, `build_report.ps1 -Offline` uses only cached packages. In an extracted submission ZIP, the manuscript is in `report_source/`; pass `-ReportDirectory .\report_source` to the PowerShell builder and `--report-dir report_source` to the exporter or packager. Both Git repositories are managed separately; edit and synchronize the report repository through the team's normal GitHub/Overleaf workflow.

The final deadline and poster dimensions have not been announced in the supplied materials; the user confirmed the presentation is in week 12. The current poster is **A1 landscape provisionally**, not a claim about the required format.

The redesigned poster uses a three-column narrative, a chronological method diagram, directly labeled monthly outcomes, a 71-rule persistence display, population sensitivity and a threshold grid. Every chart and the repository QR code are vector graphics; DejaVu font subsets are embedded for printing. The editable source is `scripts/build_poster.py`, which reads the archived CSV/JSON evidence without rerunning mining. See [poster design and reproduction notes](docs/POSTER_DESIGN.md) for the content map, preview command and sizing options.

The course prohibits directly submitting AI-generated work and requires AIGC disclosure. Codex generated the initial code, experiments, analysis and draft materials; the report discloses that assistance. Team members must understand, verify and revise the work before submission. Human contributions and peer-assessment scores are not invented. See [docs/TEAM_REVIEW.md](docs/TEAM_REVIEW.md).
