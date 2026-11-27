# Beyond Frequent Co-Purchases — poster V04.3

This English, single-page 800 × 1000 mm poster accompanies the team's three-minute presentation. The blue callout under the right-column heatmap explains how the test retention estimate changes when large baskets are excluded and why it needs separate validation in settings where most baskets are small. The poster uses the original three-column layout. Its footer identifies the contributions of GPT, Claude, Gemini and Grok.

## Print and editable files

The print PDF, editable vector SVG, screen preview and self-contained source ZIP are in `artifacts/V04.3/`. Print the PDF at 100% on 800 × 1000 mm stock. The original university mark comes from the course poster template. All other artwork is drawn as vectors. For rehearsal, use `poster/Presentation_Script_EN_ZH.md`.

## Rebuild

From the project root or the top of the extracted source package, run the following commands using Python 3.11. The renderer uses the Windows fonts Arial (regular and bold), Consolas and Microsoft YaHei (regular and bold). It reads `arial.ttf`, `arialbd.ttf`, `consola.ttf`, `msyh.ttc` and `msyhbd.ttc` from `C:\Windows\Fonts` by default. Set `POSTER_FONT_DIR` to use another font directory.

```powershell
python -m pip install -r poster/requirements-render.txt
python poster/v04_3/build_poster.py
```

The English copy for the callout, legend and footer is in `poster/v04_3/copy.json`. The builder fits the heading and three body lines inside the existing blue box. It reads the frozen cohort and the two rates from `poster/poster_data.json` and `results/tables/basket_size_sensitivity.csv`.

Both evaluations check the same 71 rules over the same four test months using identical thresholds. Across all 7,096 test orders the rules passed 225 of 284 monthly checks (79.2%). Excluding the 263 orders that contained more than 100 distinct products left 6,833 orders and 177 of 284 passes (62.3%). The latter estimate describes that particular subset of the retailer's orders. Applying the headline rate in a setting dominated by small baskets requires separate validation.

## Contributions to the poster

GPT wrote the analysis code using MLxtend. Claude designed the layout. Gemini revised the text. GPT and Grok reviewed the poster.
