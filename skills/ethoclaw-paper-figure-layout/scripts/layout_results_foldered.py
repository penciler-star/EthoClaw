#!/usr/bin/env python3
r"""Auto-layout images into a Nature Communications-ish PDF using the TypeTex LaTeX compiler.

This script started as a simple "one image per page" foldered layout.
It has been upgraded to support a compact Nature-style *multi-panel figure* layout:
- Tight, compact page usage (no "one page per image" by default)
- Subpanel letters (a, b, c, ...) aligned and consistent
- One figure caption containing: a short title + per-panel descriptions
- Sensible defaults: if the user doesn't specify, pick **1 representative image per type**
  ("type" = subfolder under the input root) instead of dumping everything.

Usage
  python3 layout_results_foldered.py \
    --input "/path/to/2_results" \
    --output "/path/to/out.pdf" \
    --title "Results"

Modes
- compact (default): multi-panel figures; representative images per folder.
- foldered: legacy behavior (all images, one per block, page breaks per folder).

Notes
- The TypeTex LaTeX environment defaults to latexmk+xelatex, but xelatex is not installed.
  We provide a .latexmkrc to force pdflatex.
"""

from __future__ import annotations

import argparse
import base64
import math
import re
from pathlib import Path
from typing import Iterable

import requests

API_URL = "https://studio-intrinsic--typetex-compile-app.modal.run/public/compile/latex"


def b64_file(p: Path) -> str:
    return base64.b64encode(p.read_bytes()).decode("utf-8")


def is_image(p: Path) -> bool:
    return p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}


def natural_key(s: str):
    # sort "img2" before "img10"
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def caption_from_filename(name: str) -> str:
    stem = Path(name).stem
    # make it readable: underscores/dashes -> spaces
    stem = re.sub(r"[_-]+", " ", stem).strip()
    return stem


def nice_title(s: str) -> str:
    # folder names like heatmap_velocity -> Heatmap velocity
    # nested names like radar/group_means -> Radar / group means
    s = s.replace("/", " / ")
    s = s.replace("_", " ").replace("-", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s[:1].upper() + s[1:] if s else s


def find_groups(root: Path) -> list[tuple[str, list[Path]]]:
    """Return [(group_name, [images...])]. group_name is folder name relative to root.

    We recurse to include nested result folders like:
      2_results/radar/group_means

    Also include images directly under root as a group (root.name).
    """

    groups: list[tuple[str, list[Path]]] = []

    # include any directory (including nested) that contains at least 1 image
    for d in sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda p: natural_key(str(p.relative_to(root)))):
        imgs = sorted([p for p in d.iterdir() if p.is_file() and is_image(p)], key=lambda p: natural_key(p.name))
        if imgs:
            rel = str(d.relative_to(root))
            groups.append((rel, imgs))

    # root images
    root_imgs = sorted([p for p in root.iterdir() if p.is_file() and is_image(p)], key=lambda p: natural_key(p.name))
    if root_imgs:
        groups.insert(0, (root.name, root_imgs))

    return groups


def pick_representatives(imgs: list[Path], k: int) -> list[Path]:
    """Pick up to k representative images from a folder.

    Heuristics (in priority order):
    - group/summary images ("group", "mean", "avg", "summary")
    - then control-like
    - then model-like
    - then natural sort order
    """

    if k <= 0 or not imgs:
        return []

    def score(p: Path) -> tuple[int, list]:
        n = p.name.lower()
        bonus = 0
        if any(t in n for t in ["group", "mean", "avg", "summary"]):
            bonus -= 50
        if "control" in n or n.startswith("con"):
            bonus -= 10
        if "model" in n:
            bonus -= 5
        return (bonus, natural_key(p.name))

    ranked = sorted(imgs, key=score)
    picked: list[Path] = []
    seen: set[str] = set()

    for p in ranked:
        if p.name in seen:
            continue
        picked.append(p)
        seen.add(p.name)
        if len(picked) >= k:
            break

    return picked


def chunked(seq: list, n: int) -> list[list]:
    return [seq[i : i + n] for i in range(0, len(seq), n)]


def tex_sanitize_filename(name: str) -> str:
    """Generate a LaTeX-friendly filename.

    Rationale: panel overlay (overpic) + some LaTeX setups can behave badly with
    spaces / non-ascii in filenames. We always map input images to safe names
    inside the compilation sandbox.
    """

    # keep extension
    p = Path(name)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", p.stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    ext = p.suffix.lower() if p.suffix else ".png"
    if not stem:
        stem = "img"
    return f"{stem}{ext}"


def build_tex_compact(
    title: str,
    panels: list[tuple[str, Path]],
    fig_title: str,
    cols: int = 2,
    panels_per_figure: int = 6,
) -> str:
    """Build a compact, Nature-like multi-panel layout.

    Important differences vs LaTeX floats:
    - We avoid figure/figure* floats entirely to prevent "blank first page" issues.
    - We render a manual "Fig. X | Title" line ABOVE the panels.
    - Panel letters are overlaid INSIDE images (via overpic) to avoid getting clipped/covered.
    - Panel descriptions are printed BELOW as a compact paragraph.
    """

    preamble_path = Path(__file__).resolve().parents[1] / "assets" / "naturecomm_figures.tex"
    preamble = preamble_path.read_text(encoding="utf-8")

    # Use 1-column for stable compact layout; keep NatureComm-ish header/geometry.
    preamble = preamble.replace("\\documentclass[9pt,twocolumn]{article}", "\\documentclass[9pt]{article}")

    # We avoid in-image overlays (overpic) for panel letters because overlays
    # can get clipped/lost near the top edge depending on PDF renderer/cropping.
    # Panel letters are rendered as normal text ABOVE each image instead.

    parts: list[str] = [preamble, "\\begin{document}\n"]

    # Tighten vertical whitespace globally.
    parts.append(
        "\\setlength{\\parindent}{0pt}\n"
        "\\setlength{\\parskip}{0pt}\n"
        "\\setlength{\\textfloatsep}{2.5mm}\n"
        "\\setlength{\\intextsep}{2.5mm}\n"
        "\\setlength{\\floatsep}{2.0mm}\n"
        "\\captionsetup[figure]{skip=1.2mm}\n"
        "% panel label box padding\n"
        "\\setlength{\\fboxsep}{1.2pt}\n\n"
    )

    # Title as a simple heading (kept, but should not create blank pages since we use no floats).
    if title:
        parts.append("\\section*{" + title.replace("_", "\\_") + "}\n")

    parts.append("% Auto-generated: compact multi-panel figure layout\n\n")

    cols = max(1, min(4, int(cols)))
    panels_per_figure = max(1, int(panels_per_figure))

    # panel width per column
    if cols == 1:
        w = 0.94
    elif cols == 2:
        w = 0.485
    elif cols == 3:
        w = 0.322
    else:
        w = 0.24

    # Figure chunks
    for fig_idx, chunk in enumerate(chunked(panels, panels_per_figure), start=1):
        cap_title = fig_title.strip() or title.strip() or "Results"
        cap_title_tex = cap_title.replace("_", "\\_")

        # --- Fig title ABOVE ---
        parts.append("\\vspace{1mm}\n")
        parts.append(f"\\textbf{{Fig. {fig_idx} | {cap_title_tex}}}\\\\[1.5mm]\n")

        # --- Panels grid ---
        parts.append("\\begin{center}\n")

        rows = int(math.ceil(len(chunk) / cols))
        for r in range(rows):
            for c in range(cols):
                i = r * cols + c
                if i >= len(chunk):
                    break

                group_name, img = chunk[i]
                letter = chr(ord("a") + i)

                parts.append(f"\\begin{{minipage}}[t]{{{w}\\textwidth}}\\vspace{{0pt}}\n")
                # Panel label: add a white box so it won't be visually "covered" by dark plot backgrounds.
                parts.append("\\raggedright\\fcolorbox{black}{white}{\\textbf{" + letter + "}}\\\\[-1.0mm]\n")
                parts.append("\\centering\n")
                parts.append(f"\\includegraphics[width=\\linewidth]{{{img.name}}}\n")
                parts.append("\\end{minipage}")

                if c != cols - 1 and (i + 1) < len(chunk):
                    parts.append("\\hfill\n")

            parts.append("\\\\[2.2mm]\n")

        parts.append("\\end{center}\n")

        # --- Panel descriptions BELOW ---
        panel_descs: list[str] = []
        for i, (group_name, img) in enumerate(chunk):
            letter = chr(ord("a") + i)
            desc = caption_from_filename(img.name)
            g = nice_title(group_name)
            panel_descs.append(f"\\textbf{{{letter}}} {g}: {desc}")

        desc_line = "; ".join(panel_descs).replace("_", "\\_") + "."
        parts.append("{\\fontsize{8}{9}\\selectfont " + desc_line + "}\\par\n")

        # Spacing between figures; allow more than one figure per page when small.
        parts.append("\\vspace{3.0mm}\n\n")

    parts.append("\\end{document}\n")
    return "".join(parts)


def build_tex_foldered(title: str, groups: list[tuple[str, list[Path]]]) -> str:
    """Legacy mode: folder-by-folder, one image per block, page breaks."""

    preamble_path = Path(__file__).resolve().parents[1] / "assets" / "naturecomm_figures.tex"
    preamble = preamble_path.read_text(encoding="utf-8")

    # Force one-column (legacy behavior), avoid float placement oddities.
    preamble = preamble.replace("\\documentclass[9pt,twocolumn]{article}", "\\documentclass[9pt]{article}")

    parts: list[str] = [preamble, "\\begin{document}\n"]

    if title:
        parts.append("\\section*{" + title.replace("_", "\\_") + "}\n")

    parts.append("% Auto-generated: folder-grouped image layout (legacy)\n")

    for group_name, imgs in groups:
        safe_group = group_name.replace("_", "\\_")
        parts.append("\\subsection*{" + safe_group + "}\n")

        for img in imgs:
            cap = caption_from_filename(img.name).replace("_", "\\_")
            parts.append(
                "\\begin{center}\n"
                f"\\includegraphics[width=0.92\\textwidth]{{{img.name}}}\\\\[1mm]\n"
                f"\\captionof{{figure}}{{{cap}}}\n"
                "\\end{center}\n\n"
            )

        parts.append("\\clearpage\n")

    parts.append("\\end{document}\n")
    return "".join(parts)


def compile_latex(tex: str, aux_files: dict[str, str]) -> bytes:
    latexmkrc = (
        "$pdf_mode = 1;\n"
        "$pdflatex = 'pdflatex -interaction=nonstopmode -file-line-error %O %S';\n"
        "$latex = 'latex -interaction=nonstopmode -file-line-error %O %S';\n"
        "$xelatex = 'pdflatex -interaction=nonstopmode -file-line-error %O %S';\n"
    )

    payload = {
        "content": tex,
        "main_filename": "main.tex",
        "auxiliary_files": {".latexmkrc": latexmkrc, **aux_files},
    }

    r = requests.post(API_URL, json=payload, timeout=180)
    r.raise_for_status()
    j = r.json()
    if not j.get("success"):
        raise RuntimeError((j.get("error") or "LaTeX compilation failed") + "\n" + (j.get("log_output") or ""))
    return base64.b64decode(j["pdf_base64"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Root folder containing subfolders of images")
    ap.add_argument("--output", required=True, help="Output PDF path")
    ap.add_argument("--title", default="Results", help="Top-level document title")

    ap.add_argument(
        "--mode",
        choices=["compact", "foldered"],
        default="compact",
        help="compact: Nature-style multi-panel figures (default). foldered: legacy layout.",
    )
    ap.add_argument(
        "--max-per-type",
        type=int,
        default=1,
        help="In compact mode: max images picked per type (type=subfolder). Default: 1.",
    )
    ap.add_argument(
        "--panels-per-figure",
        type=int,
        default=6,
        help="In compact mode: number of subpanels per figure*. Default: 6.",
    )
    ap.add_argument(
        "--cols",
        type=int,
        default=2,
        help="In compact mode: columns per figure*. Default: 2.",
    )
    ap.add_argument(
        "--fig-title",
        default="",
        help="In compact mode: figure caption title (bold). If empty, uses --title.",
    )

    args = ap.parse_args()

    root = Path(args.input).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Input does not exist: {root}")

    groups = find_groups(root)
    if not groups:
        raise SystemExit(f"No images found under: {root}")

    # Build selection (compact) or keep all (foldered)
    if args.mode == "compact":
        selected: list[tuple[str, Path]] = []
        for group_name, imgs in groups:
            reps = pick_representatives(imgs, args.max_per_type)
            for p in reps:
                selected.append((group_name, p))

        if not selected:
            raise SystemExit(f"No images selected under: {root}")

    # Collect aux files: images at root of LaTeX project need unique, LaTeX-friendly names.
    # We always sanitize filenames to avoid issues with spaces / non-ascii.
    aux: dict[str, str] = {}
    renamed: list[tuple[Path, str]] = []
    used: set[str] = set()

    def unique_safe_name(group_name: str, img: Path) -> str:
        base = tex_sanitize_filename(img.name)
        # ensure uniqueness across all aux files
        if base not in used:
            return base
        # prefix with group
        pref = tex_sanitize_filename(f"{group_name}__{img.name}")
        if pref not in used:
            return pref
        # final fallback: add numeric suffix
        i = 2
        while True:
            cand = f"{Path(base).stem}_{i}{Path(base).suffix}"
            if cand not in used:
                return cand
            i += 1

    if args.mode == "compact":
        for group_name, img in selected:
            name = unique_safe_name(group_name, img)
            used.add(name)
            aux[name] = b64_file(img)
            renamed.append((img, name))

        name_map = {orig: new for orig, new in renamed}
        selected2 = [(g, Path(name_map[p])) for (g, p) in selected]

        # Sort panels by a preferred type order to stabilize a/b/c...
        preferred = {
            "heatmap_trajectory": 10,
            "heatmap_velocity": 20,
            "radar": 30,
            "violin": 40,
        }

        def panel_sort_key(item: tuple[str, Path]):
            g, p = item
            gl = g.lower()
            k = 999
            for key, pri in preferred.items():
                if gl.startswith(key):
                    k = pri
                    break
            # keep deterministic order within a type
            return (k, natural_key(gl), natural_key(p.name))

        selected2 = sorted(selected2, key=panel_sort_key)

        tex = build_tex_compact(
            title=args.title,
            panels=selected2,
            fig_title=args.fig_title,
            cols=args.cols,
            panels_per_figure=args.panels_per_figure,
        )

    else:
        for group_name, imgs in groups:
            for img in imgs:
                name = unique_safe_name(group_name, img)
                used.add(name)
                aux[name] = b64_file(img)
                renamed.append((img, name))

        name_map = {orig: new for orig, new in renamed}
        groups2: list[tuple[str, list[Path]]] = []
        for group_name, imgs in groups:
            imgs2 = [Path(name_map[p]) for p in imgs]
            groups2.append((group_name, imgs2))

        tex = build_tex_foldered(args.title, groups2)

    pdf_bytes = compile_latex(tex, aux)

    out = Path(args.output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pdf_bytes)
    print(f"Wrote: {out} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    main()
