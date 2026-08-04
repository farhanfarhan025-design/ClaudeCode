# Page archetypes

Nine page types. Every catalogue is built from these — a page that does not fit one of them is
usually a page whose purpose has not been decided yet.

Each entry gives the JSON shape and, more importantly, when the page is the right choice.

## Contents

1. [Config skeleton](#config-skeleton)
2. [cover](#cover)
3. [contents](#contents)
4. [section](#section)
5. [feature](#feature)
6. [grid](#grid)
7. [spec](#spec)
8. [gallery](#gallery)
9. [text](#text)
10. [back](#back)
11. [html — the escape hatch](#html--the-escape-hatch)
12. [Fields every page accepts](#fields-every-page-accepts)
13. [A sequence that works](#a-sequence-that-works)

---

## Config skeleton

```json
{
  "title": "Cold Storage Solutions",
  "folio": "TNDK · Cold Storage Solutions",
  "brand": { "ink": "#1F3864", "accent": "#C9A24E" },
  "extra_css": "",
  "pages": [ { "type": "cover", "...": "..." } ]
}
```

`folio` is the running footer text on every numbered page. `extra_css` is for one-document
tweaks — if you find yourself using it on every catalogue, the change belongs in
`assets/catalogue.css` instead.

Image paths resolve relative to the config file, so keep the config next to its `images/` folder.

---

## cover

The first impression, and the page most likely to be judged on its own.

```json
{
  "type": "cover",
  "mark": "TNDK|.",
  "image": "images/hero.jpg",
  "title": "Cold Storage\nSolutions",
  "subtitle": "One sentence on what the company does and where.",
  "footer": "Company legal name · City, Country"
}
```

- `mark` is the wordmark. Text after `|` renders in the accent colour.
- `\n` in the title forces a line break — use it. Where a headline breaks is a design decision,
  not something to leave to the browser.
- The image is full-bleed under a gradient scrim, so almost any photograph works. Choose one with
  a calm area where the title sits (lower left).

## contents

Worth including from about eight pages up. Below that it is ceremony.

```json
{ "type": "contents", "eyebrow": "Contents", "title": "What's inside" }
```

Entries build themselves: every `section` page becomes a numbered entry, and any page with
`"toc": true` becomes an indented sub-entry beneath it. Page numbers are computed, so they cannot
drift out of sync when you insert a page.

Override with an explicit `items` array only when the automatic list is genuinely wrong.

## section

A full-bleed divider that tells the reader they have moved to a new part of the document.

```json
{
  "type": "section",
  "number": "01",
  "title": "Cold Rooms",
  "subtitle": "One line of orientation.",
  "image": "images/panels.jpg"
}
```

Use one per major group of products. They cost a page each, which is exactly the point — the
pause is what makes a long catalogue navigable. In a catalogue under about ten pages, skip them.

## feature

One product, one page. The workhorse for anything that deserves individual attention.

```json
{
  "type": "feature",
  "toc": true,
  "eyebrow": "Modular cold room",
  "title": "Walk-in chiller and freezer rooms",
  "image": "images/coldroom.jpg",
  "image_height": "118mm",
  "lead": "Two or three lines on what it is and why it is built this way.",
  "bullets_title": "Why this construction",
  "bullets": ["Benefit, not feature", "..."],
  "specs_title": "Specification",
  "specs": [{ "label": "Panel core", "value": "PUF, 40 kg/m³" }],
  "footnote": "A caveat, or where the figures come from."
}
```

Bullets sit left, specifications right. That split is the page's whole logic: the left column
argues, the right column proves.

`image_height` defaults to `118mm`. Raise it when the copy is short — a page that is 40% empty
below the fold looks unfinished, and a taller photograph fixes it without padding the text.

## grid

Two, four or six products at a glance. The right choice for a range where the differences are
obvious and the reader is comparing.

```json
{
  "type": "grid",
  "toc": true,
  "eyebrow": "The range",
  "title": "Room types",
  "intro": "Optional line above the grid.",
  "columns": 2,
  "items": [
    {
      "name": "Chiller room",
      "image": "images/chiller.jpg",
      "line": "One sentence — what it is, who it is for.",
      "tags": ["+2 to +8 °C", "75 mm panel"]
    }
  ]
}
```

Two columns gives four products a page with images big enough to read. Three columns gives six,
with images that are small — only worth it when the products are visually distinct.

Every cell crops to 4:3 regardless of the source image, which is what makes the grid look
deliberate. Keep `line` to one sentence and `tags` to two or three; a cell with five tags stops
being scannable.

## spec

A full-width comparison table. Reach for it when the reader's real question is "which one do I
need", and the answer is a matrix.

```json
{
  "type": "spec",
  "toc": true,
  "eyebrow": "Selection guide",
  "title": "Indicative capacities",
  "intro": "What this table is and is not.",
  "table": {
    "headers": ["Room volume", "Application", "Temperature"],
    "rows": [["Up to 10 m³", "Chiller", "+2 to +8 °C"]]
  },
  "note": "Assumptions behind the figures."
}
```

Around 14 rows fill a page comfortably. Beyond that, split by category across two pages rather
than shrinking the type.

Use `intro` and `note` to state what the numbers assume. A capacity table with no stated ambient
condition is a table someone will hold you to.

## gallery

Proof of work. Installations, sites, finished jobs.

```json
{
  "type": "gallery",
  "eyebrow": "Recent work",
  "title": "Installations",
  "columns": 2,
  "images": [{ "src": "images/site.jpg", "caption": "What this is and where." }]
}
```

Four images at two columns is the reliable arrangement. Caption every one — an uncaptioned
photograph is decoration, and decoration is the first thing a sceptical reader discounts.

## text

Company profile, capability statement, warranty terms — prose that has to be read rather than
scanned.

```json
{
  "type": "text",
  "eyebrow": "About us",
  "title": "Built for Qatar's heat",
  "image": "images/team.jpg",
  "panel": "One sentence worth pulling out of the flow.",
  "columns": 2,
  "body": ["Paragraph one.", "Paragraph two."]
}
```

Two columns for anything over about 150 words — a full-width line of 9.5pt type across A4 is
tiring to read. The `panel` is a pull-quote: use it for the single claim you most want remembered,
and only once per catalogue.

## back

Contact details and one closing line.

```json
{
  "type": "back",
  "headline": "Send us the dimensions and the product. We'll send back a sized proposal.",
  "contact": ["<strong>Company name</strong>", "Address", "Tel", "Email"],
  "note": "Design · Supply · Installation · Maintenance"
}
```

The headline should say what happens next. "Thank you" wastes the last page a reader looks at;
an instruction converts it.

`contact` lines allow inline HTML, so `<strong>` works for the company name.

## html — the escape hatch

```json
{ "type": "html", "html": "<div class=\"well\">…</div>", "dark": false }
```

For the genuine one-off that no archetype covers. Use it rarely: every bespoke page is a page
that will not match the others, and matching is what the system is for. If you reach for it twice
in one document, the right move is a new archetype in the CSS instead.

---

## Fields every page accepts

| Field | Effect |
|---|---|
| `dark` | Force the dark treatment on or off. Cover, section and back default to dark. |
| `folio` | Override the running footer text, or set `false` to drop the page number. |
| `toc` | Include this page as a sub-entry on the contents page. |
| `class` | Extra CSS class, for use with `extra_css`. |

---

## A sequence that works

For a 12-page product catalogue:

| Page | Type | Doing what |
|---|---|---|
| 1 | cover | Name the company and the category |
| 2 | contents | Show the shape of the document |
| 3 | text | Who we are, why we are credible |
| 4 | section | 01 — first product group |
| 5 | feature | The flagship of that group |
| 6 | grid | The rest of the group at a glance |
| 7 | section | 02 — second group |
| 8 | feature | Its flagship |
| 9 | spec | Selection guide across both groups |
| 10 | gallery | Proof — installed work |
| 11 | text | Warranty, service, what happens after |
| 12 | back | How to start |

Shorter documents drop the section openers and the second feature first. Longer ones repeat the
feature-then-grid rhythm — that pairing is the engine of the whole format.
