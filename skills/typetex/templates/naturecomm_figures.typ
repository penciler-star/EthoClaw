// naturecomm_figures.typ
// A Nature Communications–style 2-column template tuned for figure-heavy docs.
// Reference PDF: /home/max/下载/demo.pdf (Nature Communications | (2021)12:2784 | doi:10.1038/s41467-021-22970-y)
//
// Key traits we emulate:
// - A4-ish page with 2 columns and ~6mm gutter
// - Grey running header line with journal/doi/url and page number
// - Figures centered, captions below, small caption text
// - Compact spacing between figure and caption

#let naturecomm_setup(
  journal: "NATURE COMMUNICATIONS",
  year: "2021",
  vol: "12",
  article: "2784",
  doi: "https://doi.org/10.1038/s41467-021-22970-y",
  url: "www.nature.com/naturecommunications",

  // geometry (tuned by eye; adjust as needed)
  paper: "a4",
  height: 276mm,
  margin: (top: 16mm, bottom: 16mm, left: 16.5mm, right: 16.5mm),

  // columns
  columns: 2,
  column_gutter: 6mm,

  // text
  body_font: "Libertinus Serif",
  body_size: 9pt,
  caption_size: 8pt,
) = {
  // Use a 2-column layout wrapper because this Typst build doesn't support
  // setting column gutter directly on `page(..)`.
  set page(
    paper: paper,
    height: height,
    margin: margin,
    header: context [
      grid(
        columns: (1fr, auto),
        align: (left, right),
        inset: (bottom: 2mm),
      )[
        text(size: 8pt, fill: luma(45%))[
          journal
          + " | (" + year + ")"
          + (if vol == "" { "" } else { vol })
          + (if article == "" { "" } else { ":" + article })
          + " | " + doi + " | " + url
        ],
        text(size: 8pt, fill: luma(45%))[counter(page).display()],
      ]
      rule(length: 100%, stroke: (paint: luma(75%), thickness: 0.3pt))
    ],
    footer: none,
  )

  set text(font: body_font, size: body_size)
  set par(justify: true, leading: 1.16em)

  // Figure rendering: centered body + left-aligned caption below.
  show figure: it => {
    let n = context counter(figure).display()
    block(above: 4mm, below: 4mm)[
      align(center)[it.body]
      if it.caption != none {
        v(2mm)
        align(left)[
          set text(size: caption_size)
          set par(justify: false, leading: 1.12em)
          strong([Fig. ]) + strong(n) + h(2mm) + it.caption
        ]
      }
    ]
  }
}

// Wrap a whole document body in two columns with a chosen gutter.
#let naturecomm_doc(body, gutter: 6mm) = {
  columns(2, gutter: gutter)[
    body
  ]
}

// Convenience: a column-width figure from an image path.
// Note: this Typst build doesn't support `label:` as a named argument on figure;
// you attach a label by writing `<label>` after the element.
#let fig(path, caption: none, width: 100%, label: none) = {
  if label == none {
    figure(
      image(path, width: width),
      caption: caption,
    )
  } else {
    // attach label in markup mode
    [#figure(
      image(path, width: width),
      caption: caption,
    ) <label>]
  }
}

// Convenience: panel grid for multi-subfigure layouts.
#let panel_grid(cols: 2, gap: 3mm, ..items) = {
  grid(columns: cols, gutter: gap, align: center)[..items]
}

// "Wide" figure: robust approach—render on its own 1-column page.
// (Cross-column floats are fragile in Typst; this is stable.)
#let widefig(body, caption: none, label: none) = {
  pagebreak()
  // Temporarily turn off columns by entering a single-column wrapper.
  if label == none {
    columns(1)[
      figure(body, caption: caption)
    ]
  } else {
    columns(1)[
      [#figure(body, caption: caption) <label>]
    ]
  }
  pagebreak()
}
