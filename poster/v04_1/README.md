# Beyond Frequent Co-Purchases — poster V04.1

This English, single-page 800 × 1000 mm poster is a companion to the team's three-minute presentation. In the right column, the heatmap legend explains the gray cell and gold selection outline. The blue callout gives a recommendation and the basket-size sensitivity result. The original three-column V04.0 design is the visual template.

## Print and editable files

The print PDF, editable vector SVG, screen preview and self-contained source ZIP are in `artifacts/V04.1/`. Print the PDF at 100% on 800 × 1000 mm stock. The original university mark comes from the course poster template. All other artwork is drawn as vectors. For rehearsal, use `poster/Presentation_Script_EN_ZH.md`.

## Rebuild

From the project root or the top of the extracted source package, run the following commands using Python 3.11. The renderer uses the Windows fonts Arial (regular and bold), Consolas and Microsoft YaHei (regular and bold). It reads `arial.ttf`, `arialbd.ttf`, `consola.ttf`, `msyh.ttc` and `msyhbd.ttc` from `C:\Windows\Fonts` by default. Set `POSTER_FONT_DIR` to use another font directory.

```powershell
python -m pip install -r poster/requirements-render.txt
python poster/v04_1/build_poster.py
```

Edit `poster/v04_1/copy.json` to revise the six English text lines. The build uses the original scene from `poster/build_poster.py` and the experiment outputs from `poster/poster_data.json` and `results/tables/basket_size_sensitivity.csv`. The main and restricted percentages in the copy are populated at build time. Both use all 71 frozen rules in each of the four test months. The main cohort passed 225 of 284 rule-months. The same cohort passed 177 of 284 when evaluation excluded baskets containing over 100 distinct products.

## Contributions to the poster

Claude Code created the visual redesign in V04.0. OpenAI Codex supported the project implementation and analysis. Antigravity Orchestrator (Neon) authored the revised English text for V04.1. Codex applied it to the original layout and checked the data, print rendering and source package. Orchestrator (Neon) and Cursor Grok 4.7 Extra High reviewed the rendered revision.
