"""Rearrange the pages of a PDF so it can be printed and folded as a booklet.

A booklet sheet holds four pages: two on the front and two on the back.
Pages are reordered so that when printed duplex, two pages per side,
and the stack is folded in the middle, the pages read in the correct order.

Example for an 8-page document:
    sheet 1 front: 8 | 1     sheet 1 back: 2 | 7
    sheet 2 front: 6 | 3     sheet 2 back: 4 | 5

By default the output contains the reordered single pages, ready to be
printed with "2 pages per sheet" in your print dialog. Use --imposed to
instead place the two pages side by side on one output page.

Some printers turn the back side upside down when printing duplex and offer
no setting to change it. Use --rotate-back to rotate every back side 180
degrees in the output, which cancels this out.
"""

import argparse
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation


def booklet_order(page_count: int) -> list[int | None]:
    """Return 0-based page indices in booklet order. None means a blank page."""
    total = -(-page_count // 4) * 4  # round up to a multiple of 4
    order = []
    for i in range(total // 4):
        order += [
            total - 1 - 2 * i, 2 * i,      # front: last, first
            2 * i + 1, total - 2 - 2 * i,  # back: second, second-to-last
        ]
    return [p if p < page_count else None for p in order]


def page_size(reader: PdfReader) -> tuple[float, float]:
    box = reader.pages[0].mediabox
    return float(box.width), float(box.height)


def write_reordered(reader: PdfReader, order: list[int | None],
                    rotate_back: bool = False) -> PdfWriter:
    writer = PdfWriter()
    width, height = page_size(reader)
    for side, pair in enumerate(zip(order[0::2], order[1::2])):
        flip = rotate_back and side % 2 == 1
        # Rotating a whole side 180 degrees swaps its two pages and turns each one.
        for index in reversed(pair) if flip else pair:
            if index is None:
                writer.add_blank_page(width, height)
            else:
                page = writer.add_page(reader.pages[index])
                if flip:
                    page.rotate(180)
    return writer


def write_imposed(reader: PdfReader, order: list[int | None],
                  rotate_back: bool = False) -> PdfWriter:
    writer = PdfWriter()
    width, height = page_size(reader)
    for side, (left, right) in enumerate(zip(order[0::2], order[1::2])):
        sheet = writer.add_blank_page(2 * width, height)
        for offset, index in ((0, left), (width, right)):
            if index is None:
                continue
            page = reader.pages[index]
            page.transfer_rotation_to_content()
            box = page.mediabox
            sheet.merge_transformed_page(
                page,
                Transformation().translate(offset - float(box.left), -float(box.bottom)),
            )
        if rotate_back and side % 2 == 1:
            sheet.rotate(180)
    return writer


def main() -> int:
    parser = argparse.ArgumentParser(description="Rearrange PDF pages for booklet printing.")
    parser.add_argument("input", type=Path, help="PDF file to rearrange")
    parser.add_argument("-o", "--output", type=Path,
                        help="output file (default: <input>-booklet.pdf)")
    parser.add_argument("--imposed", action="store_true",
                        help="place two pages side by side on each output page")
    parser.add_argument("--rotate-back", action="store_true",
                        help="rotate back sides 180 degrees, for printers that print them upside down")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"file not found: {args.input}")
    output = args.output or args.input.with_name(f"{args.input.stem}-booklet.pdf")

    reader = PdfReader(args.input)
    page_count = len(reader.pages)
    if page_count == 0:
        parser.error("input PDF has no pages")

    order = booklet_order(page_count)
    write = write_imposed if args.imposed else write_reordered
    writer = write(reader, order, args.rotate_back)
    with open(output, "wb") as f:
        writer.write(f)

    blanks = order.count(None)
    print(f"Wrote {output}: {page_count} pages + {blanks} blank -> {len(order) // 4} sheets")
    if args.rotate_back:
        print("Print on A3, " + ("" if args.imposed else "2 pages per sheet, ") +
              "duplex with your printer's default flip.")
    elif args.imposed:
        print("Print on A3, duplex, flip on short edge.")
    else:
        print("Print on A3, 2 pages per sheet, duplex, flip on long edge.")
    if not args.rotate_back:
        print("If the back side comes out upside down, switch to the other flip edge "
              "or run again with --rotate-back.")
    return 0

