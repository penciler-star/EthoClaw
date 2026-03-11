#!/usr/bin/env python3
r"""Auto-layout images into a Nature Communications-ish PDF using the TypeTex LaTeX compiler.

Design goals
- Group by folder (subdirectories).
- Auto caption from filename.
- Stable output (avoid 2-column float weirdness): use 1-column LaTeX + \captionof.

Usage
  python3 layout_results_foldered.py \
    --input "/home/max/下载/results" \
    --output "/home/max/.openclaw/workspace/tmp_results/results_auto.pdf"

Options
- --input: root directory containing subfolders with images
- --output: output PDF path
- --title: optional document title
- --glob: optional file pattern (default: *.png,*.jpg,*.jpeg,*.webp)

Notes
- The TypeTex LaTeX environment defaults to latexmk+xelatex, but xelatex is not installed.
  We provide a .latexmkrc to force pdflatex.
"""

from __future__ import annotations

import argparse
import base64
import os
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


def find_groups(root: Path) -> list[tuple[str, list[Path]]]:
    groups: list[tuple[str, list[Path]]] = []
    for d in sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: natural_key(p.name)):
        imgs = sorted([p for p in d.iterdir() if p.is_file() and is_image(p)], key=lambda p: natural_key(p.name))
        if imgs:
            groups.append((d.name, imgs))
    # also include images directly under root as a group
    root_imgs = sorted([p for p in root.iterdir() if p.is_file() and is_image(p)], key=lambda p: natural_key(p.name))
    if root_imgs:
        groups.insert(0, (root.name, root_imgs))
    return groups


def build_tex(title: str, groups: list[tuple[str, list[Path]]]) -> str:
    # Keep this minimal and robust. We reuse the NatureComm-ish preamble file by inlining it.
    # (No \begin{document} in the template; we append it here.)
    preamble_path = Path(__file__).resolve().parents[1] / "templates" / "naturecomm_figures.tex"
    preamble = preamble_path.read_text(encoding="utf-8")
    # Force one-column: avoid float placement oddities.
    preamble = preamble.replace("\\documentclass[9pt,twocolumn]{article}", "\\documentclass[9pt]{article}")

    parts: list[str] = [preamble, "\\begin{document}\n"]

    if title:
        parts.append("\\section*{" + title.replace("_", "\\_") + "}\n")

    parts.append("% Auto-generated: folder-grouped image layout\n")

    for group_name, imgs in groups:
        safe_group = group_name.replace("_", "\\_")
        parts.append("\\subsection*{" + safe_group + "}\n")

        # Special-case: heatmap folders with a shared colorbar.
        # If the folder contains a colorbar image and at least 3 other images,
        # place 3 heatmaps + colorbar on ONE row.
        colorbars = [p for p in imgs if "colorbar" in p.name.lower()]
        if colorbars and len(imgs) >= 4:
            cb = colorbars[0]
            others = [p for p in imgs if p != cb]
            others = sorted(others, key=lambda p: natural_key(p.name))[:3]

            parts.append(
                "\\begin{center}\n"
                "\\setlength{\\tabcolsep}{2pt}\n"
                "\\renewcommand{\\arraystretch}{0}\n"
                "\\begin{tabular}{@{}ccc c@{}}\n"
                f"  \\includegraphics[width=0.27\\textwidth]{{{others[0].name}}} &\n"
                f"  \\includegraphics[width=0.27\\textwidth]{{{others[1].name}}} &\n"
                f"  \\includegraphics[width=0.27\\textwidth]{{{others[2].name}}} &\n"
                f"  \\includegraphics[width=0.08\\textwidth]{{{cb.name}}} \\\\ \n"
                "\\end{tabular}\n"
                f"\\captionof{{figure}}{{{safe_group}}}\n"
                "\\end{center}\n\n"
            )

            parts.append("\\clearpage\n")
            continue

        # Default: one image per block, caption from filename.
        for img in imgs:
            cap = caption_from_filename(img.name).replace("_", "\\_")
            # Centered block; \\captionof works without floats.
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
    ap.add_argument("--title", default="Results", help="Top-level title")
    args = ap.parse_args()

    root = Path(args.input).expanduser().resolve()
    if not root.exists():
        raise SystemExit(f"Input does not exist: {root}")

    groups = find_groups(root)
    if not groups:
        raise SystemExit(f"No images found under: {root}")

    # Collect aux files: images at root of LaTeX project need unique names.
    # If filenames collide across folders, we disambiguate by prefixing the folder name.
    aux: dict[str, str] = {}
    renamed: list[tuple[Path, str]] = []
    used: set[str] = set()

    for group_name, imgs in groups:
        for img in imgs:
            name = img.name
            if name in used:
                name = f"{group_name}__{name}"
            used.add(name)
            aux[name] = b64_file(img)
            renamed.append((img, name))

    # Rewrite groups to use the potentially renamed filenames.
    name_map = {orig: new for orig, new in renamed}
    groups2: list[tuple[str, list[Path]]] = []
    for group_name, imgs in groups:
        # fake Path objects with replaced .name for templating purposes
        imgs2 = [Path(name_map[p]) for p in imgs]
        groups2.append((group_name, imgs2))

    tex = build_tex(args.title, groups2)
    pdf_bytes = compile_latex(tex, aux)

    out = Path(args.output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pdf_bytes)
    print(f"Wrote: {out} ({len(pdf_bytes)} bytes)")


if __name__ == "__main__":
    main()
