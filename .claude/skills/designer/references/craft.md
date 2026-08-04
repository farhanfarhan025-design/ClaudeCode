# Craft notes

The system behind the archetypes: brand tokens, type, images, and what changes when a catalogue
goes to a commercial printer.

## Contents

1. [Brand tokens](#brand-tokens)
2. [Retargeting to another company](#retargeting-to-another-company)
3. [The type scale](#the-type-scale)
4. [The grid](#the-grid)
5. [Image specifications](#image-specifications)
6. [Print production](#print-production)
7. [Fonts](#fonts)
8. [Diagnosing a page that looks wrong](#diagnosing-a-page-that-looks-wrong)

---

## Brand tokens

Set in the config's `brand` block; they become CSS custom properties on `:root`.

| Token | Default | Used for |
|---|---|---|
| `ink` | `#1F3864` | Headings, dark page fields, table headers, folio numerals |
| `accent` | `#C9A24E` | Eyebrows, rules, section numerals, bullet marks |
| `wash` | `#F2F2F2` | Panel fills, empty image frames |
| `tint` | `#D6E4F0` | Hairlines, table stripes, tag chips |
| `paper` | `#FFFFFF` | Page background |
| `body-ink` | `#333333` | Body text |
| `muted` | `#6B7280` | Captions, secondary labels |
| `font` | Calibri stack | Everything |

Two colours carry the whole system. That is deliberate: a catalogue using five colours reads as
uncertain, and the restraint is most of what makes the pages feel like one document.

## Retargeting to another company

```json
"brand": {
  "ink": "#14532D",
  "accent": "#B45309",
  "tint": "#DCFCE7"
}
```

When a brand gives you only one colour, do not invent a second. Use the brand colour as `ink`,
set `accent` to a darker or lighter step of the same hue, and let the layout carry the
distinctiveness instead of the palette.

Check contrast before committing: `ink` must hold white type at 15pt and above, and `accent` must
be legible at 8pt on white for the eyebrows. A pale gold that works as a rule can disappear as
text.

## The type scale

Sizes are in points because the output is print. Each step is far enough from the next to be read
as a different level — that separation is what creates hierarchy.

| Element | Size | Role |
|---|---|---|
| `.cover__title` | 42pt | Cover only |
| `.section__title` | 34pt | Section openers |
| `h1` | 25pt | Page titles |
| `h2` | 13pt | Sub-heads |
| `h3` | 10pt | Column heads inside a page |
| `.lead` | 11pt | Opening paragraph |
| `p` | 9.5pt | Body |
| `.caption` | 7.5pt | Captions, footnotes |
| `.eyebrow` | 8pt, tracked | The small label above a title |

Do not add sizes between these. If something needs emphasis, change weight or colour rather than
introducing a 15pt that will look like a mistake next to the 13pt on the facing page.

The eyebrow does real work: it tells the reader what kind of page they are on before they read
the title. Use it on every interior page.

## The grid

A4 with 16mm margins, six columns, 6mm gutters. Content sits in `.well`, which stops 26mm from
the foot so nothing collides with the folio.

Full-bleed elements — cover images, feature photographs, section imagery — sit outside the well
deliberately. That contrast between a photograph running to the trim edge and text held well
inside the margin is most of the visual energy in the format.

## Image specifications

| Use | Aspect | Minimum long edge |
|---|---|---|
| Cover | Portrait or square, cropped to A4 | 2000px |
| Feature | Landscape, cropped to ~210×118mm | 2000px |
| Grid cell | Any — cropped to 4:3 | 1200px |
| Gallery | Any — cropped to the cell | 1200px |
| Section opener | Landscape band across the foot | 1600px |

Everything crops with `object-fit: cover`, so mixed sources still align. What that cannot fix:

- **A subject at the edge of the frame** gets cut. Check the preview, not the source file.
- **A busy background** behind cover type stays busy under the scrim. Prefer a photograph with a
  calm lower-left area.
- **A low-resolution image** prints soft. Say so rather than shipping it — the user may have a
  better copy, and cannot know it matters unless you tell them.
- **A portrait phone photo in a 4:3 cell** loses its top and bottom. Sometimes that is fine;
  sometimes it decapitates the product.

SVG works anywhere a raster does, and is the better choice for diagrams and line drawings because
it stays sharp at any print size.

## Print production

The PDF is A4 at 100% with no printer margins, which is right for office printing and for most
digital print shops.

If it is going to a commercial printer, two things change and both need the user's input rather
than your assumption:

- **Bleed.** Full-bleed images need 3mm of image beyond the trim edge, which means a 216×303mm
  page. Ask the printer before adding it — supplying bleed when they expect trimmed pages is as
  much of a problem as omitting it.
- **Colour.** This system is RGB. Commercial presses are CMYK, and `#C9A24E` gold will shift when
  converted. If colour fidelity matters, the printer should do the conversion from your PDF, and
  the user should see a proof before the run.

For a stapled booklet the page count must be a multiple of four. Plan for it early — discovering
it at the end means padding with a page that has nothing to say.

## Fonts

The stack is `Calibri, Carlito, Liberation Sans, DejaVu Sans, sans-serif`.

Calibri is the house font and is present on the user's machine. It is often absent from a Linux
build container, where the render falls back to Liberation Sans — metrically similar but visibly
different in the details. Line breaks in a headline can therefore differ slightly between your
preview and what the user sees.

If a layout is tight enough that a font substitution would break it, the layout is too tight.

## Diagnosing a page that looks wrong

| What you see | Usually means |
|---|---|
| Pink hatched block | Image path wrong — check it is relative to the config file |
| Text running under the folio rule | Content overflowing `.well`; cut copy or move it to two pages |
| Page three-quarters empty | Raise `image_height` on a feature, or merge two thin pages |
| Grid cells at different heights | A `line` far longer than the others — even them up |
| Headline breaking awkwardly | Put `\n` in the title where you want the break |
| Colours washed out in the PDF | `print-color-adjust: exact` was removed from the CSS; restore it |
| Everything shifted down a page | A page's content exceeded 297mm and pushed into the next |
