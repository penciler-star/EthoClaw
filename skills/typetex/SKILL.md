---
name: typetex
description: Compile Typst (.typ) and LaTeX (.tex) documents to PDF via the TypeTex compilation API, including multi-file projects and images. Use for generating PDFs, testing templates, and automated figure-heavy layouts.
---

# Typst & LaTeX Compiler

Compile Typst (.typ) and LaTeX (.tex) documents to PDF using the TypeTex compilation API.

## API Endpoint

**Base URL:** `https://studio-intrinsic--typetex-compile-app.modal.run`

## Endpoints

### Compile Typst

```
POST /public/compile/typst
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "#set page(paper: \"a4\")\n\n= Hello World\n\nThis is a Typst document.",
  "main_filename": "main.typ",
  "auxiliary_files": {}
}
```

**Response (Success):**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQK..."
}
```

**Response (Failure):**
```json
{
  "success": false,
  "error": "error: file not found: missing.typ"
}
```

### Compile LaTeX

```
POST /public/compile/latex
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}",
  "main_filename": "main.tex",
  "auxiliary_files": {}
}
```

**Response (Success):**
```json
{
  "success": true,
  "pdf_base64": "JVBERi0xLjQK..."
}
```

**Response (Failure):**
```json
{
  "success": false,
  "error": "! LaTeX Error: Missing \\begin{document}.",
  "log_output": "This is pdfTeX..."
}
```

### Health Check

```
GET /public/compile/health
```

Returns `{"status": "ok", "service": "public-compile"}` if the service is running.

## Usage Examples

### Simple Typst Document

```python
import requests
import base64

response = requests.post(
    "https://studio-intrinsic--typetex-compile-app.modal.run/public/compile/typst",
    json={
        "content": """
#set page(paper: "a4", margin: 2cm)
#set text(font: "New Computer Modern", size: 11pt)

= My Document

This is a paragraph with *bold* and _italic_ text.

== Section 1

- Item 1
- Item 2
- Item 3
""",
        "main_filename": "main.typ"
    }
)

result = response.json()
if result["success"]:
    pdf_bytes = base64.b64decode(result["pdf_base64"])
    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF saved to output.pdf")
else:
    print(f"Compilation failed: {result['error']}")
```

### Simple LaTeX Document

```python
import requests
import base64

response = requests.post(
    "https://studio-intrinsic--typetex-compile-app.modal.run/public/compile/latex",
    json={
        "content": r"""
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}

\title{My Document}
\author{Author Name}

\begin{document}
\maketitle

\section{Introduction}

This is a LaTeX document with math: $E = mc^2$

\end{document}
""",
        "main_filename": "main.tex"
    }
)

result = response.json()
if result["success"]:
    pdf_bytes = base64.b64decode(result["pdf_base64"])
    with open("output.pdf", "wb") as f:
        f.write(pdf_bytes)
else:
    print(f"Compilation failed: {result['error']}")
    if result.get("log_output"):
        print(f"Log: {result['log_output']}")
```

### Multi-File Project (Typst)

```python
import requests
import base64

response = requests.post(
    "https://studio-intrinsic--typetex-compile-app.modal.run/public/compile/typst",
    json={
        "content": """
#import "template.typ": *

#show: project.with(title: "My Report")

= Introduction

#include "chapter1.typ"
""",
        "main_filename": "main.typ",
        "auxiliary_files": {
            "template.typ": """
#let project(title: none, body) = {
  set page(paper: "a4")
  set text(font: "New Computer Modern")

  align(center)[
    #text(size: 24pt, weight: "bold")[#title]
  ]

  body
}
""",
            "chapter1.typ": """
== Chapter 1

This is the first chapter.
"""
        }
    }
)

result = response.json()
if result["success"]:
    pdf_bytes = base64.b64decode(result["pdf_base64"])
    with open("report.pdf", "wb") as f:
        f.write(pdf_bytes)
```

### Including Images

For binary files like images, base64-encode them:

```python
import requests
import base64

# Read and encode an image
with open("figure.png", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

response = requests.post(
    "https://studio-intrinsic--typetex-compile-app.modal.run/public/compile/typst",
    json={
        "content": """
#set page(paper: "a4")

= Document with Image

#figure(
  image("figure.png", width: 80%),
  caption: [A sample figure]
)
""",
        "main_filename": "main.typ",
        "auxiliary_files": {
            "figure.png": image_base64
        }
    }
)
```

### Using curl

```bash
# Typst compilation
curl -X POST https://studio-intrinsic--typetex-compile-app.modal.run/public/compile/typst \
  -H "Content-Type: application/json" \
  -d '{
    "content": "#set page(paper: \"a4\")\n\n= Hello World\n\nThis is Typst.",
    "main_filename": "main.typ"
  }' | jq -r '.pdf_base64' | base64 -d > output.pdf

# LaTeX compilation
curl -X POST https://studio-intrinsic--typetex-compile-app.modal.run/public/compile/latex \
  -H "Content-Type: application/json" \
  -d '{
    "content": "\\documentclass{article}\n\\begin{document}\nHello World\n\\end{document}",
    "main_filename": "main.tex"
  }' | jq -r '.pdf_base64' | base64 -d > output.pdf
```

## Supported Features

### Typst
- Full Typst language support
- Multi-file projects with imports
- Images (PNG, JPG, SVG)
- Custom fonts (New Computer Modern, etc.)
- Math equations
- Tables and figures
- Bibliography (using Hayagriva format)

### LaTeX
- Full TeX Live distribution via Tectonic
- Multi-file projects (\input, \include)
- BibTeX/BibLaTeX bibliography
- Custom style files (.sty, .cls)
- All standard packages (amsmath, graphicx, etc.)
- TikZ/PGFPlots graphics
- Images (PNG, JPG, PDF, EPS)

## Error Handling

When compilation fails, the response includes:
- `success: false`
- `error`: Human-readable error message
- `log_output` (LaTeX only): Full compilation log for debugging

Common errors:
- **Syntax errors**: Check your source code for typos
- **Missing files**: Ensure all imported/included files are in `auxiliary_files`
- **Package not found**: Most common packages are available; contact support for additions
- **Timeout**: Complex documents may timeout after 60 seconds

## Rate Limits

- No authentication required
- Please be respectful of shared resources
- For high-volume usage, contact support

## Default Template (Nature Communications-style figures)

This OpenClaw workspace includes a **default figure-heavy Typst template** based on the layout conventions in:
- `/home/max/下载/demo.pdf` (Nature Communications | (2021)12:2784 | doi:10.1038/s41467-021-22970-y)

Template file:
- `skills/typetex/templates/naturecomm_figures.typ`

What it sets up:
- A4 page + margins
- Running header line (journal/doi/url + page number)
- Figure styling (centered figure body, small left-aligned caption, compact spacing)
- Helpers: `naturecomm_doc`, `fig`, `panel_grid`, `widefig`

### How to use it in a compile request

Pass the template in `auxiliary_files` and import it from `main.typ`:

```typst
#import "naturecomm_figures.typ": naturecomm_setup, naturecomm_doc, fig, panel_grid, widefig

#naturecomm_setup()
#show: naturecomm_doc

= Results

#fig(
  "fig1.png",
  caption: [Caption text...],
)
```

Notes:
- The Typst build behind this API does **not** support setting column gutter directly on `page(..)`. The 2-column layout is applied via `#show: naturecomm_doc` (which uses `columns(2, gutter: ..)[..]`).
- Cross-column floating figures are fragile; `widefig` renders a wide figure on its own 1-column page for stability.

## Auto Layout Tool (folder-grouped)

If you have many images and want an automatic paper-like PDF, grouped by folders and captioned from filenames, use:

- Script: `skills/typetex/tools/layout_results_foldered.py`
- Example:

```bash
python3 skills/typetex/tools/layout_results_foldered.py \
  --input "/home/max/下载/results" \
  --output "/home/max/.openclaw/workspace/tmp_results/results_foldered_auto.pdf" \
  --title "Results"
```

Behavior:
- Each subfolder becomes a `\subsection*{...}`.
- Each image becomes a centered block with `\captionof{figure}{<filename>}`.
- Uses a `.latexmkrc` to force `pdflatex` (since `xelatex` is not available in this TypeTex environment).

## Default Templates (workspace-local)

This workspace includes reusable templates (Typst + LaTeX) that mimic the figure/caption layout from:
`/home/max/下载/demo.pdf` (Nature Communications | (2021)12:2784).

- Typst: `skills/typetex/templates/naturecomm_figures.typ`
- LaTeX: `skills/typetex/templates/naturecomm_figures.tex`

Typical Typst usage:

```typst
#import "naturecomm_figures.typ": naturecomm_setup, naturecomm_doc, fig, panel_grid, widefig

#naturecomm_setup()
#show: naturecomm_doc

= Results
Text...

#fig(
  "fig1.png",
  caption: [Your caption...],
  label: <fig:one>,
)

#widefig(
  panel_grid(
    cols: 2,
    gap: 4mm,
    image("a.png", width: 100%),
    image("b.png", width: 100%),
  ),
  caption: [Wide figure caption...],
  label: <fig:wide>,
)
```

LaTeX usage: start from `naturecomm_figures.tex`, then add your own `\begin{document} ...` content.

Notes (Typst 0.13.1 API build quirks observed via this skill):
- `#set page(columns: 2, column-gutter: ...)` is not supported; use `#show: naturecomm_doc` (wrap with `columns(2, gutter: ...)`).
- `figure(label: <x>)` named argument is not supported; attach labels in markup with `<label>`.

## Tips for Agents

1. **Always check `success`** before accessing `pdf_base64`
2. **Parse errors** to provide helpful feedback to users
3. **Use minimal documents** when testing - complex documents take longer
4. **Cache results** if compiling the same content multiple times
5. **Include all dependencies** in `auxiliary_files` for multi-file projects
6. **Default**: when the user asks for image/figure-heavy Typst output without specifying a house style, use `skills/typetex/templates/naturecomm_figures.typ`.

## Related Resources

- [Typst Documentation](https://typst.app/docs/)
- [LaTeX Wikibook](https://en.wikibooks.org/wiki/LaTeX)
- [TypeTex](https://typetex.app) - Full document editor with AI assistance
