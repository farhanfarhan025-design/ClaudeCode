#!/usr/bin/env python3
"""
TNDK Cold Room Quotation Generator

Generates a customized quotation by doing precise find-and-replace on the master
template. Preserves all branding, images, fonts, and layout.

Usage:
    python3 generate.py --client "Mr. Suresh" --ref "QUT/DCTS/067/2026" \
        --date "26 April 2026" --total 59000 \
        --output /path/to/output.docx [other options]

Run with --help for full options.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MASTER = SKILL_DIR / "template" / "master.docx"


def unpack_docx(docx_path, output_dir):
    """Unpack docx to a directory."""
    with zipfile.ZipFile(docx_path, 'r') as z:
        z.extractall(output_dir)


def repack_docx(input_dir, output_path):
    """Repack a directory back into a docx."""
    if os.path.exists(output_path):
        os.remove(output_path)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(input_dir):
            for f in files:
                full = os.path.join(root, f)
                arc = os.path.relpath(full, input_dir)
                z.write(full, arc)


def strip_proof_errors(content):
    """
    Remove <w:proofErr .../> self-closing tags from XML.
    These are spell/grammar check markers that split otherwise contiguous text
    runs and prevent simple find-and-replace. Removing them is safe — Word will
    re-detect any actual issues when the document is opened.
    """
    return re.sub(r'<w:proofErr[^/]*/>', '', content)


def merge_adjacent_runs(content):
    """
    Merge adjacent <w:r>...<w:t>X</w:t></w:r><w:r>...<w:t>Y</w:t></w:r>
    where the two <w:rPr> blocks are identical. This makes find-and-replace
    work on text that was artificially split by Word.

    Returns content with merged runs where possible.
    """
    # Pattern: </w:t></w:r><w:r><w:rPr>...</w:rPr><w:t>
    # If the rPr blocks match, merge.
    pattern = re.compile(
        r'<w:r>(<w:rPr>.*?</w:rPr>)?<w:t(?:\s+xml:space="preserve")?>([^<]*)</w:t></w:r>'
        r'<w:r>(<w:rPr>.*?</w:rPr>)?<w:t(?:\s+xml:space="preserve")?>([^<]*)</w:t></w:r>',
        re.DOTALL
    )

    prev = None
    while prev != content:
        prev = content
        def merge(m):
            rpr1 = m.group(1) or ''
            text1 = m.group(2)
            rpr2 = m.group(3) or ''
            text2 = m.group(4)
            if rpr1 == rpr2:
                # Determine if we need xml:space=preserve
                merged_text = text1 + text2
                space_attr = ' xml:space="preserve"' if (
                    merged_text != merged_text.strip() or '  ' in merged_text
                ) else ''
                return f'<w:r>{rpr1}<w:t{space_attr}>{merged_text}</w:t></w:r>'
            else:
                return m.group(0)  # no change
        content = pattern.sub(merge, content)
    return content


def fill_empty_cell_by_paraid(content, paraid, text):
    """
    Fill an empty <w:p w14:paraId="X">...<w:pPr>...</w:pPr></w:p> with text.
    The cell paragraph has formatting in <w:pPr> but no <w:r>...<w:t>.
    We insert a new run with default Calibri styling matching the table.

    Returns (new_content, success: bool).
    """
    # Match the empty paragraph with this paraId. The paragraph ends with </w:pPr></w:p>
    # because there's no run inside.
    pattern = re.compile(
        r'(<w:p w14:paraId="' + paraid + r'"[^>]*>'
        r'\s*<w:pPr>.*?</w:pPr>)\s*</w:p>',
        re.DOTALL
    )
    m = pattern.search(content)
    if not m:
        return content, False

    # Build the run with text. Use Calibri/minorHAnsi to match other cells.
    # Match the styling pattern used elsewhere in the master.
    run = (
        '<w:r w:rsidRPr="00BE13B2">'
        '<w:rPr>'
        '<w:rFonts w:asciiTheme="minorHAnsi" w:eastAsia="Times New Roman" '
        'w:hAnsiTheme="minorHAnsi" w:cstheme="minorHAnsi"/>'
        '</w:rPr>'
        f'<w:t>{escape_xml(text)}</w:t>'
        '</w:r>'
    )

    new_paragraph = m.group(1) + run + '</w:p>'
    return content[:m.start()] + new_paragraph + content[m.end():], True


def fill_project_description_table(xml_path, room1_temp, room1_dims, room1_panel,
                                    room2_temp, room2_dims, room2_panel):
    """
    Fill the project description table on page 2:
    Freezer row gets room1 values, Chiller row gets room2 values.

    The 6 empty cells are identified by their stable paragraph IDs from the
    master template:
        Freezer row:  30870054 (Temp), 46246C16 (Dims), 7E53579A (Panel)
        Chiller row:  24C732FA (Temp), 08FB71E5 (Dims), 314D2633 (Panel)
    """
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fills = [
        ("30870054", room1_temp),
        ("46246C16", room1_dims),
        ("7E53579A", room1_panel),
        ("24C732FA", room2_temp),
        ("08FB71E5", room2_dims),
        ("314D2633", room2_panel),
    ]

    filled = 0
    for paraid, text in fills:
        if text:
            content, ok = fill_empty_cell_by_paraid(content, paraid, text)
            if ok:
                filled += 1

    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return filled


def replace_in_xml(xml_path, replacements):
    """
    Apply a list of (find, replace) tuples to an XML file.
    Strips proof errors and merges adjacent runs first to handle text that
    was artificially split across runs.
    """
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Strip proof errors and merge adjacent runs to make text contiguous
    content = strip_proof_errors(content)
    content = merge_adjacent_runs(content)

    not_found = []

    for find, replace in replacements:
        if find in content:
            content = content.replace(find, escape_xml(replace))
        else:
            not_found.append(find)

    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return not_found


def escape_xml(text):
    """Escape text for safe insertion into XML."""
    if text is None:
        return ""
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    # Use smart quotes for typography
    text = text.replace("'", '&#x2019;')
    text = text.replace('"', '&#x201C;')  # left double quote
    return text


def calc_panel_areas(L, W, H, with_floor=True):
    """Calculate wall, ceiling, floor, and total panel areas."""
    walls = 2 * (L * H) + 2 * (W * H)
    ceiling = L * W
    floor = L * W if with_floor else 0
    total = walls + ceiling + floor
    return {
        'walls': walls,
        'ceiling': ceiling,
        'floor': floor,
        'total': total,
        'volume': L * W * H,
    }


def parse_dims(dims_str):
    """Parse '4.0 × 5.0 × 2.5 m' or '4.0 x 5.0 x 2.5' into (L, W, H)."""
    if not dims_str:
        return None
    # Normalize separators
    cleaned = dims_str.replace('×', 'x').replace('X', 'x').replace('m', '').strip()
    parts = [p.strip() for p in cleaned.split('x')]
    if len(parts) != 3:
        return None
    try:
        return tuple(float(p) for p in parts)
    except ValueError:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate TNDK cold room quotation from master template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Required
    parser.add_argument('--output', required=True, help="Output .docx path")
    parser.add_argument('--client', required=True, help="Client name (e.g., 'Mr. Suresh')")
    parser.add_argument('--ref', required=True, help="Reference number (e.g., 'QUT/DCTS/067/2026')")
    parser.add_argument('--date', required=True, help="Date in 'DD Month YYYY' format")
    parser.add_argument('--total', type=float, required=True, help="Grand total in QAR")
    parser.add_argument('--total-words', required=True, help="Amount in words")

    # Client block
    parser.add_argument('--address', default='Doha, Qatar', help="Project / site address")
    parser.add_argument('--contact', default='', help="Contact person")
    parser.add_argument('--validity', default='15 Days from quote date', help="Validity period")

    # Subject / project
    parser.add_argument('--subject', default='Supply, Installation, Testing & Commissioning of cold room',
                        help="Quotation subject line")

    # Room 1 (Freezer in master)
    parser.add_argument('--room1-type', default='FREEZER ROOM')
    parser.add_argument('--room1-qty', type=int, default=1)
    parser.add_argument('--room1-temp', default='')
    parser.add_argument('--room1-dims', default='', help='External dims like "2.35 × 2.0 × 2.40 m"')
    parser.add_argument('--room1-panel', default='100 mm')

    # Room 2 (Chiller in master)
    parser.add_argument('--room2-type', default='CHILLER')
    parser.add_argument('--room2-qty', type=int, default=1)
    parser.add_argument('--room2-temp', default='')
    parser.add_argument('--room2-dims', default='', help='External dims like "4.5 × 3.5 × 3.5 m"')
    parser.add_argument('--room2-panel', default='100 mm')

    # Recalculation overrides — if user wants to override the calculated panel coverage in section 1
    parser.add_argument('--use-room2-for-section1', action='store_true',
                        help='Use room 2 (chiller) dimensions for section 1 panel calc, instead of master defaults')

    parser.add_argument('--keep-master-figures', action='store_true',
                        help="Don't modify section 1, 4, 6, 10 figures — only update header/client/total")
    
    # BOQ Item Prices
    parser.add_argument('--item1-price', type=float, help="Item 1 price (room construction)")
    parser.add_argument('--item2-price', type=float, help="Item 2 price (doors)")
    parser.add_argument('--item3-price', type=float, help="Item 3 price (floor)")
    parser.add_argument('--item4-price', type=float, help="Item 4 price (refrigeration)")
    parser.add_argument('--item5-price', type=float, help="Item 5 price (control panel)")
    parser.add_argument('--item6-price', type=float, help="Item 6 price (testing)")

    args = parser.parse_args()

    if not MASTER.exists():
        print(f"ERROR: Master template not found at {MASTER}", file=sys.stderr)
        sys.exit(1)

    # Work in a temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        unpacked = tmpdir / "unpacked"
        unpacked.mkdir()

        # Unpack
        unpack_docx(MASTER, unpacked)

        # === BUILD REPLACEMENT LIST ===
        replacements = []

        # --- Header block: Reference, Date, Validity ---
        # Master values: QUT/DCTS/068/2026 | 26 April 2026 | 15 Days from quote date
        replacements.append(("QUT/DCTS/068/2026", args.ref))
        replacements.append(("26 April 2026", args.date))
        # Validity may already match default; replace anyway (idempotent)
        if args.validity != "15 Days from quote date":
            replacements.append(("15 Days from quote date", args.validity))

    # Client / Address / Contact block.
    # Master TO block layout:
    #     M/s. [Client Name]
    #     [Project / Site Address]
    #     Doha, Qatar
    #     Attn: [Contact Person]
    # The address field substitutes into [Project / Site Address]. The
    # "Doha, Qatar" line below it is fixed in the master.
    # If the user supplied --address that already says "Doha, Qatar", clear it
    # to avoid duplication.
        address = args.address.strip()
        if address.lower() in ("doha, qatar", "doha qatar", "doha"):
            address = ""  # let the master's existing "Doha, Qatar" line do the work

        replacements.append(("[Client Name]", args.client))
        replacements.append(("[Project / Site Address]", address))
        replacements.append(("[Contact Person]", args.contact if args.contact else args.client))

        # --- Subject (only if explicitly changed from default) ---
        # The master subject is exactly the default. Skip replacement unless changed.

        # --- Project description table ---
        # Master has FREEZER ROOM and CHILLER rows. Update room types if changed.
        if args.room1_type != "FREEZER ROOM":
            replacements.append(("FREEZER ROOM", args.room1_type))
        if args.room2_type != "CHILLER":
            # Note: "CHILLER" appears multiple places — be careful
            # We'll do a targeted replace below
            pass

        # === SECTION 1 / 4 / 6 / 10 — recalculation ===
        if not args.keep_master_figures:
            # Parse both rooms' dimensions
            r1_dims = parse_dims(args.room1_dims) if args.room1_dims else None
            r2_dims = parse_dims(args.room2_dims) if args.room2_dims else None

            # Calculate panel areas for each room
            r1_areas = calc_panel_areas(*r1_dims, with_floor=True) if r1_dims else None
            r2_areas = calc_panel_areas(*r2_dims, with_floor=True) if r2_dims else None

            if r1_areas and r2_areas:
                # === TWO ROOMS — Show per-room breakdown + combined total ===
                r1L, r1W, r1H = r1_dims
                r2L, r2W, r2H = r2_dims
                r1_label = args.room1_type  # e.g., "FREEZER ROOM"
                r2_label = args.room2_type  # e.g., "CHILLER"

                # Section 1 - Combined panel coverage
                walls_text = (
                    f"{r2_label}: 2 × ({r2L} × {r2H}) + 2 × ({r2W} × {r2H}) = {r2_areas['walls']:.2f} sqm  |  "
                    f"{r1_label}: 2 × ({r1L} × {r1H}) + 2 × ({r1W} × {r1H}) = {r1_areas['walls']:.2f} sqm  |  "
                    f"Total: {r1_areas['walls'] + r2_areas['walls']:.2f} sqm"
                )
                ceiling_text = (
                    f"{r2_label}: {r2L} × {r2W} = {r2_areas['ceiling']:.2f} sqm  |  "
                    f"{r1_label}: {r1L} × {r1W} = {r1_areas['ceiling']:.2f} sqm  |  "
                    f"Total: {r1_areas['ceiling'] + r2_areas['ceiling']:.2f} sqm"
                )
                floor_text = (
                    f"{r2_label}: {r2L} × {r2W} = {r2_areas['floor']:.2f} sqm  |  "
                    f"{r1_label}: {r1L} × {r1W} = {r1_areas['floor']:.2f} sqm  |  "
                    f"Total: {r1_areas['floor'] + r2_areas['floor']:.2f} sqm"
                )
                grand_total_panels = r1_areas['total'] + r2_areas['total']
                total_panels_text = (
                    f"{r2_label}: {r2_areas['total']:.2f} sqm  |  "
                    f"{r1_label}: {r1_areas['total']:.2f} sqm  |  "
                    f"Grand Total: {grand_total_panels:.2f} sqm"
                )

                replacements.append(("2 × (4.0 × 2.5) + 2 × (5.0 × 2.5) = 45.00 sqm", walls_text))
                replacements.append(("4.0 × 5.0 = 20.00 sqm", ceiling_text))
                replacements.append(("85.00 sqm", total_panels_text))

                # Section 4 - Combined floor areas
                total_floor = r1_areas['floor'] + r2_areas['floor']
                floor_area_text = (
                    f"{r2_areas['floor']:.2f} sqm ({r2_label}) + {r1_areas['floor']:.2f} sqm ({r1_label}) = {total_floor:.2f} sqm"
                )
                replacements.append(("100 mm PUF panel, same specification as wall panels — 20.00 sqm",
                                     f"100 mm PUF panel, same specification as wall panels — {floor_area_text}"))
                replacements.append(("18 mm Marine-grade plywood laid over the floor panel — 20.00 sqm",
                                     f"18 mm Marine-grade plywood laid over the floor panel — {floor_area_text}"))
                replacements.append((" (Checkered) Plate, slip-resistant — 20.00 sqm",
                                     f" (Checkered) Plate, slip-resistant — {floor_area_text}"))

                # Section 6 - Internal volume (use chiller as primary, note freezer in text)
                replacements.append(("4.0 × 5.0 × 2.5 = 50 ",
                                     f"{r2L} × {r2W} × {r2H} = {r2_areas['volume']:.0f} "))

                # Section 10 - BOQ combined dimensions
                total_volume = r1_areas['volume'] + r2_areas['volume']
                boq_dims_text = (
                    f"{r2_label} {r2L} m × {r2W} m × {r2H} m ({r2_areas['volume']:.0f} m³) + "
                    f"{r1_label} {r1L} m × {r1W} m × {r1H} m ({r1_areas['volume']:.0f} m³)"
                )
                replacements.append(("internal size 4.0 m (L) × 5.0 m (W) × 2.5 m (H) — Internal Volume: 50 m³",
                                     f"internal sizes: {boq_dims_text} — Combined Volume: {total_volume:.0f} m³"))
                replacements.append(("(total panel area: 85.00 sqm)",
                                     f"(total panel area: {grand_total_panels:.2f} sqm)"))
                replacements.append(("chequered plate (20.00 sqm)",
                                     f"chequered plate ({total_floor:.2f} sqm)"))

            elif r1_areas or r2_areas:
                # === SINGLE ROOM — Use whichever is provided ===
                primary_areas = r2_areas if r2_areas else r1_areas
                primary_dims = r2_dims if r2_areas else r1_dims
                L, W, H = primary_dims

                replacements.append(("2 × (4.0 × 2.5) + 2 × (5.0 × 2.5) = 45.00 sqm",
                                     f"2 × ({L} × {H}) + 2 × ({W} × {H}) = {primary_areas['walls']:.2f} sqm"))
                replacements.append(("4.0 × 5.0 = 20.00 sqm",
                                     f"{L} × {W} = {primary_areas['ceiling']:.2f} sqm"))
                replacements.append(("85.00 sqm", f"{primary_areas['total']:.2f} sqm"))

                # Section 4
                floor_str = f"{primary_areas['floor']:.2f} sqm"
                replacements.append(("100 mm PUF panel, same specification as wall panels — 20.00 sqm",
                                     f"100 mm PUF panel, same specification as wall panels — {floor_str}"))
                replacements.append(("18 mm Marine-grade plywood laid over the floor panel — 20.00 sqm",
                                     f"18 mm Marine-grade plywood laid over the floor panel — {floor_str}"))
                replacements.append((" (Checkered) Plate, slip-resistant — 20.00 sqm",
                                     f" (Checkered) Plate, slip-resistant — {floor_str}"))

                # Section 6
                replacements.append(("4.0 × 5.0 × 2.5 = 50 ",
                                     f"{L} × {W} × {H} = {primary_areas['volume']:.0f} "))

                # Section 10
                replacements.append(("internal size 4.0 m (L) × 5.0 m (W) × 2.5 m (H) — Internal Volume: 50 m³",
                                     f"internal size {L} m (L) × {W} m (W) × {H} m (H) — Internal Volume: {primary_areas['volume']:.0f} m³"))
                replacements.append(("(total panel area: 85.00 sqm)",
                                     f"(total panel area: {primary_areas['total']:.2f} sqm)"))
                replacements.append(("chequered plate (20.00 sqm)",
                                     f"chequered plate ({primary_areas['floor']:.2f} sqm)"))

        # === GRAND TOTAL ===
        total_str = f"QAR {args.total:,.2f}"
        replacements.append(("QAR 51,450.00", total_str))

        # Amount in words. The master XML stores this in TWO runs with different
        # rPr blocks (bold vs bold+italic):
        #   <w:r>...<w:t>Qatari Riyals </w:t></w:r>            (bold)
        #   <w:r>...<w:t>Fifty One Thousand Four Hundred Fifty Only.</w:t></w:r>  (bold+italic)
        # Different rPr means they don't merge. We replace just the inner italic
        # run, preserving the "Qatari Riyals " label intact.
        old_words_inner = "Fifty One Thousand Four Hundred Fifty Only."
        # Strip any "Qatari Riyals" prefix the user supplied — the master already has it
        new_words = args.total_words.strip()
        # Remove leading "Qatari Riyals" (case-insensitive) if present
        if new_words.lower().startswith("qatari riyals"):
            new_words = new_words[len("qatari riyals"):].strip()
        new_words = new_words.rstrip('.') + "."
        replacements.append((old_words_inner, new_words))

        # === BOQ ITEM PRICES ===
        # Replace master's default prices with provided values
        # Master defaults: Item1=35K, Item2=3.6K, Item3=4K, Item4=6K, Item5=1.8K, Item6=1.05K
        if args.item1_price is not None:
            replacements.append(("35,000.00", f"{args.item1_price:,.2f}"))
        if args.item2_price is not None:
            replacements.append(("3,600.00", f"{args.item2_price:,.2f}"))
        if args.item3_price is not None:
            replacements.append(("4,000.00", f"{args.item3_price:,.2f}"))
        if args.item4_price is not None:
            replacements.append(("6,000.00", f"{args.item4_price:,.2f}"))
        if args.item5_price is not None:
            replacements.append(("1,800.00", f"{args.item5_price:,.2f}"))
        if args.item6_price is not None:
            replacements.append(("1,050.00", f"{args.item6_price:,.2f}"))

        # === APPLY REPLACEMENTS ===
        doc_xml = unpacked / "word" / "document.xml"
        not_found = replace_in_xml(doc_xml, replacements)

        # === FILL PROJECT DESCRIPTION TABLE ===
        # Page 2 has a table with empty TEMP / DIMS / PANEL THICKNESS cells
        # for both the Freezer and Chiller rows. Fill them from the room args.
        cells_filled = fill_project_description_table(
            doc_xml,
            room1_temp=args.room1_temp,
            room1_dims=args.room1_dims,
            room1_panel=args.room1_panel,
            room2_temp=args.room2_temp,
            room2_dims=args.room2_dims,
            room2_panel=args.room2_panel,
        )

        # Also apply some replacements to header/footer XMLs (ref number may appear)
        for header_or_footer in (unpacked / "word").glob("header*.xml"):
            replace_in_xml(header_or_footer, replacements)
        for header_or_footer in (unpacked / "word").glob("footer*.xml"):
            replace_in_xml(header_or_footer, replacements)

        # === REPACK ===
        os.makedirs(os.path.dirname(os.path.abspath(args.output)) or '.', exist_ok=True)
        repack_docx(str(unpacked), args.output)

        # === REPORT ===
        size_kb = os.path.getsize(args.output) / 1024
        print(f"✓ Generated: {args.output} ({size_kb:.1f} KB)")
        print(f"  Reference:  {args.ref}")
        print(f"  Client:     {args.client}")
        print(f"  Date:       {args.date}")
        print(f"  Total:      {total_str}")
        if cells_filled:
            print(f"  Project description table: {cells_filled}/6 cells filled")


if __name__ == "__main__":
    main()
