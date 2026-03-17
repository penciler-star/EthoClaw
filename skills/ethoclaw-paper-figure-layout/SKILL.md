---
name: paper-figure-layout
description: "Auto-layout folders of result images into a paper-like PDF (LaTeX) with captions derived from filenames and optional heatmap+colorbar grouping. Use when the user says: use images in this folder to help with layout/generate paper figures/arrange figures into PDF by folder grouping; or when there are many PNG/JPG figures that need consistent captions and pagination."
---

# Paper Figure Layout

Auto-generate a paper-like PDF from a directory of images.

## What it does

- **Groups by subfolder**: each subfolder becomes a section.
- **Captions from filenames**: underscores/dashes become spaces.
- **Stable pagination**: uses one-column LaTeX blocks (no fragile two-column floats).
- **Heatmap special-case**: if a folder contains `*colorBar*` and ≥3 other images, it lays out **3 heatmaps + 1 shared colorbar** on one row.

## Quick start

Run the script:

```bash
python3 scripts/layout_results_foldered.py \
  --input "/path/to/results" \
  --output "/path/to/out.pdf" \
  --title "Results"
```

## Outputs

- A single PDF at `--output`.

## Notes

- The TypeTex LaTeX compiler environment often defaults to `xelatex` via latexmk, but `xelatex` may be missing.
  The script supplies a `.latexmkrc` that forces `pdflatex`.

## Resources

- `scripts/layout_results_foldered.py` — the generator.
- `assets/naturecomm_figures.tex` — the Nature-Communications-ish preamble used by the generator.
