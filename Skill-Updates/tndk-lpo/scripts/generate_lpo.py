#!/usr/bin/env python3
"""
TNDK Local Purchase Order generator.

Renders a polished one-page LPO PDF that matches the saved Farhan / TNDK style:
- Dark blue (#1F3864) header band and footer
- Gold (#C9A24E) stripe and "LOCAL PURCHASE ORDER" badge
- Meta block (PO #, Date, Ref Quote, Vendor) on light blue
- VENDOR INFORMATION strip
- Line item table with optional Delivery row, Sub-Total, Discount, Grand Total
- Amount in words, italic notes, computer-generated callout

Two ways to invoke:

  1. From a JSON config (preferred for anything beyond a single line item):
       python3 generate_lpo.py --config po.json --output po.pdf

  2. Directly from CLI args (single-item POs):
       python3 generate_lpo.py \
           --output po.pdf \
           --po-number "LPO-190/2026" --po-date "27-04-2026" \
           --vendor "ABC Trading W.L.L. - Qatar" \
           --currency QAR \
           --item "Cold room insulation panels|Nos|50|115|5750"

JSON schema — see references/json_schema.md for the full definition.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Number-to-words is a small enough utility to inline rather than ship as a separate file.
ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
        "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
        "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _under_thousand(n: int) -> str:
    if n == 0:
        return ""
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + (("-" + ONES[n % 10]) if n % 10 else "")
    return ONES[n // 100] + " Hundred" + ((" " + _under_thousand(n % 100)) if n % 100 else "")


def integer_to_words(n: int) -> str:
    """Convert a non-negative integer into English words (Indian/Western mix is fine for receipts)."""
    if n == 0:
        return "Zero"
    parts = []
    for unit_value, unit_name in [(1_000_000_000, "Billion"),
                                  (1_000_000, "Million"),
                                  (1_000, "Thousand"),
                                  (1, "")]:
        if n >= unit_value:
            chunk = n // unit_value
            n = n % unit_value
            text = _under_thousand(chunk).strip()
            if text:
                parts.append(text + ((" " + unit_name) if unit_name else ""))
    return " ".join(parts).strip()


CURRENCY_FULL_NAME = {
    "QAR": "Qatari Riyals",
    "SR":  "Saudi Riyals",
    "SAR": "Saudi Riyals",
    "AED": "UAE Dirhams",
    "USD": "US Dollars",
    "EUR": "Euros",
    "OMR": "Omani Riyals",
    "BHD": "Bahraini Dinars",
    "KWD": "Kuwaiti Dinars",
    "INR": "Indian Rupees",
}


def amount_to_words(amount: float, currency_code: str) -> str:
    """e.g. 76000.00, 'SR' -> 'Seventy-Six Thousand Saudi Riyals Only (SR 76,000.00)'"""
    cur_full = CURRENCY_FULL_NAME.get(currency_code.upper(), currency_code)
    whole = int(amount)
    fract = round((amount - whole) * 100)
    words = integer_to_words(whole)
    base = f"{words} {cur_full} Only"
    if fract:
        base = f"{words} {cur_full} and {integer_to_words(fract)} Cents Only"
    formatted = f"{currency_code} {amount:,.2f}"
    return f"{base} ({formatted})"


def fmt_money(n: float) -> str:
    return f"{n:,.2f}"


# === Mini template engine ===
# We use a {{VAR}} replacement style with {{#KEY}}...{{/KEY}} for optional blocks.
def render_template(template: str, ctx: dict) -> str:
    """Render the template:
      - {{KEY}}                -> ctx[KEY] (string)
      - {{#KEY}}...{{/KEY}}    -> kept if ctx.get(KEY) is truthy, else removed
    """
    # Process conditional blocks first (allow nested? we don't need nesting here).
    def block_sub(match):
        key = match.group(1)
        body = match.group(2)
        return body if ctx.get(key) else ""
    template = re.sub(r"\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}", block_sub, template, flags=re.DOTALL)
    # Then simple variables.
    def var_sub(match):
        key = match.group(1)
        val = ctx.get(key, "")
        return str(val) if val is not None else ""
    template = re.sub(r"\{\{(\w+)\}\}", var_sub, template)
    return template


# === Line items HTML ===
def build_line_items_html(items: list, currency: str) -> str:
    """Each item dict: {description, specs (list of strings, optional),
                        variant (optional, e.g. 'RHS'), unit, qty, unit_price, total (optional)}"""
    rows = []
    for idx, it in enumerate(items, start=1):
        desc = it.get("description", "")
        specs = it.get("specs") or []
        variant = it.get("variant", "")
        unit = it.get("unit", "")
        qty = it.get("qty", "")
        unit_price = it.get("unit_price")
        total = it.get("total")
        if total is None and unit_price is not None and qty != "":
            try:
                total = float(unit_price) * float(qty)
            except (TypeError, ValueError):
                total = None

        # Build the description cell HTML
        desc_html = f'<div class="title">{desc}</div>'
        if specs:
            specs_inner = "".join(f"<div>• {s}</div>" for s in specs)
            desc_html += f'<div class="specs">{specs_inner}</div>'
        if variant:
            desc_html += f'<div class="variant">– {variant}</div>'

        unit_price_str = fmt_money(float(unit_price)) if unit_price is not None else ""
        total_str = fmt_money(float(total)) if total is not None else ""

        rows.append(f"""    <tr>
      <td class="sn">{idx}</td>
      <td class="desc">{desc_html}</td>
      <td class="unit">{unit}</td>
      <td class="qty">{qty}</td>
      <td class="price">{unit_price_str}</td>
      <td class="total">{total_str}</td>
    </tr>""")
    return "\n".join(rows)


def build_notes_html(notes: list) -> str:
    return "\n".join(f"    <li>{n}</li>" for n in notes)


# === Profile defaults (companies) ===
PROFILES = {
    "tndk": {
        "company_name": "THE NEW DOHA KITCHEN COMPANY",
        "company_subtitle": "",
        "company_address": "P.O. Box 80247, Doha, Qatar  |  farhan@dctsqatar.com",
        "footer_company": "The New Doha Kitchen Company",
    },
    "dcts": {
        "company_name": "DOHA COOLING & TRADING SOLUTIONS W.L.L",
        "company_subtitle": "The New Doha Kitchen Equipment Services",
        "company_address": "P.O. Box 80247, Doha, Qatar  |  farhan@dctsqatar.com",
        "footer_company": "The New Doha Kitchen Equipment Services",
    },
}


def derive_totals(items, delivery_amount, discount):
    """Return (subtotal, grand_total) given items, delivery, discount."""
    items_total = 0.0
    for it in items:
        if it.get("total") is not None:
            items_total += float(it["total"])
        elif it.get("unit_price") is not None and it.get("qty") not in (None, ""):
            try:
                items_total += float(it["unit_price"]) * float(it["qty"])
            except (TypeError, ValueError):
                pass
    subtotal = items_total + (float(delivery_amount) if delivery_amount else 0.0)
    grand = subtotal - (float(discount) if discount else 0.0)
    return subtotal, grand


def build_context(cfg: dict) -> dict:
    """Merge cfg with profile defaults and compute derived fields."""
    profile_key = (cfg.get("profile") or "tndk").lower()
    profile = PROFILES.get(profile_key, PROFILES["tndk"])

    # Allow per-PO overrides on header strings
    company_name = cfg.get("company_name") or profile["company_name"]
    company_subtitle = cfg.get("company_subtitle") or profile["company_subtitle"]
    company_address = cfg.get("company_address") or profile["company_address"]
    footer_company = cfg.get("footer_company") or profile["footer_company"]

    currency = (cfg.get("currency") or "QAR").upper()

    items = cfg.get("items", [])
    delivery_amount = cfg.get("delivery_amount")
    delivery_label = cfg.get("delivery_label", "Delivery to Doha")
    discount = cfg.get("discount")

    # Compute totals if not explicitly given
    subtotal, grand = derive_totals(items, delivery_amount, discount)
    subtotal = cfg.get("subtotal", subtotal)
    grand_total = cfg.get("grand_total", grand)

    # Amount in words
    amount_words = cfg.get("amount_words") or amount_to_words(grand_total, currency)

    # Build vendor contact line — accept either separate fields or a pre-built CONTACT_LINE
    contact_line_parts = []
    for fld in ("mobile", "website", "email"):
        v = cfg.get(fld)
        if v:
            label = {"mobile": "Mobile", "website": "Website", "email": "Email"}[fld]
            contact_line_parts.append(f"{label}: {v}")
    contact_line = cfg.get("contact_line") or " | ".join(contact_line_parts)

    line_items_html = build_line_items_html(items, currency)

    notes = cfg.get("notes", [])
    notes_html = build_notes_html(notes)

    ctx = {
        "COMPANY_NAME": company_name,
        "COMPANY_SUBTITLE": company_subtitle,
        "COMPANY_ADDRESS": company_address,
        "FOOTER_COMPANY": footer_company,
        "PO_NUMBER": cfg["po_number"],
        "PO_DATE": cfg["po_date"],
        "REF_QUOTE": cfg.get("ref_quote", "—"),
        "VENDOR_NAME": cfg["vendor"],
        "CONTACT_PERSON": cfg.get("contact_person", ""),
        "CONTACT_LINE": contact_line,
        "PAYMENT_TERMS": cfg.get("payment_terms", ""),
        "DELIVERY_TERMS": cfg.get("delivery_terms", ""),
        "CURRENCY": currency,
        "LINE_ITEMS_HTML": line_items_html,
        "DELIVERY_ROW": bool(delivery_amount),
        "DELIVERY_LABEL": delivery_label,
        "DELIVERY_AMOUNT": fmt_money(float(delivery_amount)) if delivery_amount else "",
        "DISCOUNT_ROW": bool(discount),
        "DISCOUNT": fmt_money(float(discount)) if discount else "",
        "SUBTOTAL": fmt_money(float(subtotal)),
        "GRAND_TOTAL": fmt_money(float(grand_total)),
        "AMOUNT_WORDS": amount_words,
        "NOTES_BLOCK": bool(notes),
        "NOTES_HTML": notes_html,
    }
    return ctx


def render_pdf(html_path: Path, pdf_path: Path):
    """Render HTML to PDF. Prefers playwright (chromium) for modern CSS support
    (flexbox, gap, etc.). Falls back to wkhtmltopdf if playwright is unavailable —
    note that wkhtmltopdf uses an older WebKit and renders modern CSS imperfectly."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sync_playwright = None

    if sync_playwright is not None:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(html_path.absolute().as_uri(), wait_until="networkidle")
                page.pdf(
                    path=str(pdf_path),
                    format="A4",
                    print_background=True,
                    margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                )
                browser.close()
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                return
        except Exception as e:
            sys.stderr.write(f"[playwright failed — falling back to wkhtmltopdf]\n{e}\n")

    # Fallback: wkhtmltopdf
    if shutil.which("wkhtmltopdf"):
        cmd = [
            "wkhtmltopdf",
            "--enable-local-file-access",
            "--page-size", "A4",
            "--margin-top", "0",
            "--margin-bottom", "0",
            "--margin-left", "0",
            "--margin-right", "0",
            "--print-media-type",
            "--disable-smart-shrinking",
            str(html_path),
            str(pdf_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and pdf_path.exists() and pdf_path.stat().st_size > 0:
            return
        raise RuntimeError(f"wkhtmltopdf failed: {result.stderr}")

    raise RuntimeError(
        "Neither playwright nor wkhtmltopdf is available. "
        "Install one of them to render the LPO."
    )


def parse_cli_item(s: str) -> dict:
    """Parse 'description|unit|qty|unit_price|total' (total optional)."""
    parts = [p.strip() for p in s.split("|")]
    if len(parts) < 4:
        raise ValueError(
            f"--item must have at least 4 pipe-separated fields "
            f"(description|unit|qty|unit_price[|total]), got: {s!r}"
        )
    item = {
        "description": parts[0],
        "unit": parts[1],
        "qty": parts[2],
        "unit_price": float(parts[3]),
    }
    if len(parts) >= 5 and parts[4]:
        item["total"] = float(parts[4])
    return item


def main():
    parser = argparse.ArgumentParser(
        description="Generate a TNDK Local Purchase Order PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", help="Path to JSON config file with all PO data.")
    parser.add_argument("--output", required=True, help="Output PDF path.")
    parser.add_argument("--keep-html", action="store_true",
                        help="Keep the intermediate HTML next to the PDF.")

    # Direct CLI args (overlay on config if both supplied)
    parser.add_argument("--profile", choices=["tndk", "dcts"],
                        help="Header branding: tndk (default) or dcts.")
    parser.add_argument("--company-name", help="Override company name in header.")
    parser.add_argument("--company-subtitle", help="Override company subtitle.")
    parser.add_argument("--po-number")
    parser.add_argument("--po-date")
    parser.add_argument("--ref-quote")
    parser.add_argument("--vendor")
    parser.add_argument("--contact-person")
    parser.add_argument("--mobile")
    parser.add_argument("--website")
    parser.add_argument("--email")
    parser.add_argument("--payment-terms")
    parser.add_argument("--delivery-terms")
    parser.add_argument("--currency", default=None,
                        help="Currency code (e.g. QAR, SR, USD). Default: QAR.")
    parser.add_argument("--item", action="append", default=[],
                        help="A line item as 'description|unit|qty|unit_price[|total]'. "
                             "Can be repeated.")
    parser.add_argument("--delivery-amount", type=float)
    parser.add_argument("--delivery-label")
    parser.add_argument("--discount", type=float)
    parser.add_argument("--note", action="append", default=[],
                        help="A note line. Can be repeated.")

    args = parser.parse_args()

    # Load config
    cfg = {}
    if args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            cfg = json.load(f)

    # CLI overrides
    overrides = {
        "profile": args.profile,
        "company_name": args.company_name,
        "company_subtitle": args.company_subtitle,
        "po_number": args.po_number,
        "po_date": args.po_date,
        "ref_quote": args.ref_quote,
        "vendor": args.vendor,
        "contact_person": args.contact_person,
        "mobile": args.mobile,
        "website": args.website,
        "email": args.email,
        "payment_terms": args.payment_terms,
        "delivery_terms": args.delivery_terms,
        "currency": args.currency,
        "delivery_amount": args.delivery_amount,
        "delivery_label": args.delivery_label,
        "discount": args.discount,
    }
    for k, v in overrides.items():
        if v is not None:
            cfg[k] = v

    if args.item:
        cfg["items"] = [parse_cli_item(s) for s in args.item]
    if args.note:
        cfg["notes"] = args.note

    # Validate required fields
    required = ["po_number", "po_date", "vendor"]
    missing = [r for r in required if not cfg.get(r)]
    if missing:
        parser.error(f"Missing required fields: {', '.join(missing)}")
    if not cfg.get("items"):
        parser.error("At least one line item is required (use --item or 'items' in JSON config).")

    # Render
    ctx = build_context(cfg)
    template_path = Path(__file__).parent.parent / "assets" / "lpo_template.html"
    template = template_path.read_text(encoding="utf-8")
    html_out = render_template(template, ctx)

    output_pdf = Path(args.output).absolute()
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "lpo.html"
        html_path.write_text(html_out, encoding="utf-8")
        if args.keep_html:
            kept = output_pdf.with_suffix(".html")
            kept.write_text(html_out, encoding="utf-8")
            print(f"HTML written to: {kept}")
        render_pdf(html_path, output_pdf)

    print(f"LPO written to: {output_pdf}")


if __name__ == "__main__":
    main()
