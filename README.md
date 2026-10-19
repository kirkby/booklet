# booklet

Rearrange the pages of a PDF so it can be printed and folded as a booklet.

## Context

A booklet is made from sheets of paper (typically A3 for an A4-sized booklet)
printed on both sides with two pages per side, then stacked and folded down
the middle. For the pages to read in order after folding, they must be printed
in a special sequence — not 1, 2, 3, 4…

Some print software has a "booklet" option that does this automatically. When
yours doesn't, `booklet` produces a new PDF with the pages already rearranged,
so you can print it with ordinary settings.

### Page order

Each sheet carries four pages. The page count is rounded up to a multiple of 4
with blank pages added at the end. For an 8-page document:

| Sheet | Front (left \| right) | Back (left \| right) |
|-------|-----------------------|----------------------|
| 1     | 8 \| 1                | 2 \| 7               |
| 2     | 6 \| 3                | 4 \| 5               |

## Prerequisites

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [pypdf](https://pypi.org/project/pypdf/), installed automatically as a dependency

## Installation

Run straight from the project folder with uv, with no separate install step:

```bash
uv run booklet --help
```

Or install it as a command available everywhere:

```bash
uv tool install .
```

With pip instead:

```bash
pip install .
```

## Usage

```bash
booklet INPUT.pdf [-o OUTPUT.pdf] [--imposed] [--rotate-back]
```

| Option            | Description                                                      |
|-------------------|------------------------------------------------------------------|
| `INPUT.pdf`       | The PDF to rearrange                                             |
| `-o`, `--output`  | Output file. Default: `INPUT-booklet.pdf` next to the input      |
| `--imposed`       | Place two pages side by side on each output page (see below)     |
| `--rotate-back`   | Rotate back sides 180°, for printers that print them upside down |

You can also run it as a module: `python -m booklet INPUT.pdf`.

### Two output modes

**Default — reordered pages.** The output has the same page size as the input,
with pages in booklet order. Print it with:

- Paper: A3
- Pages per sheet: 2, layout direction left-to-right
- Duplex (two-sided), flip on **long edge** (on macOS: Long-Edge binding)

This looks wrong but isn't: the print dialog measures the edge against the
original portrait page, and its long edge is the A3 sheet's short edge.

```bash
booklet report.pdf -o report-booklet.pdf
```

**`--imposed` — pages already placed side by side.** Each output page holds two
input pages next to each other, so an A4 document becomes A3 landscape pages.
Use this if your print software can't do "2 pages per sheet". Print it with:

- Paper: A3
- Duplex (two-sided), flip on **short edge**

```bash
booklet report.pdf -o report-booklet.pdf --imposed
```

### Back side upside down?

The page order is fine; the printer is flipping the paper over the wrong edge.
If your print dialog has a duplex edge setting, switch it to the other edge
(long ↔ short) and print again.

Some printers (for example via PaperCut Mobility Print on macOS) offer only
"double-sided" with no edge setting. Then let `booklet` turn the back sides
upside down in the PDF instead, so the printer's flip turns them right way up:

```bash
booklet report.pdf -o report-booklet.pdf --rotate-back
```

For 8 pages the output is then 8, 1, 7↻, 2↻, 6, 3, 5↻, 4↻ (↻ = rotated 180°).
Either way, do a test print of a single sheet first.

### After printing

Keep the sheets in the order they came out of the printer, fold the stack down
the middle, and staple along the fold if you want.

### Limitations

- The page size is taken from the first page, so a PDF with mixed page sizes
  may not line up well, especially with `--imposed`.
- Large documents give a thick stack that is hard to fold neatly. For more than
  about 40–60 pages, consider splitting it into several booklets.

## Project layout

```
booklet/
├── pyproject.toml        # project metadata, dependencies, `booklet` command
├── README.md
└── src/booklet/
    ├── __init__.py       # package exports
    ├── __main__.py       # enables `python -m booklet`
    └── cli.py            # page ordering, PDF writing, command-line interface
```

## Creation

Created in October 2026 by MKM with help from Claude Code (Anthropic). The
project was set up with `uv init --package` and uses
[pypdf](https://pypdf.readthedocs.io/) to read, reorder and combine pages.

## License

MIT. See [LICENSE](LICENSE).
