# TryWith brand guide (for generated images)

Generated banners and figures should look like they belong on https://trywith.co.jp/, not like
generic stock visuals. Match the site's palette, tone, and proportions. Before generating images,
read this guide and fold it into every image prompt.

## Source of truth
The live site https://trywith.co.jp/ is the visual reference. Its `theme-color` is **#DC3545**,
and its hero / OG image is a **dark navy tech scene with white Japanese text and a sharp red
angular accent**. If the brand appears to have changed, re-check the site (homepage + OG image)
and update these values.

## Color palette
- **Brand red (accent): `#DC3545`** — the signature color. Use it distinctly but sparingly: an
  angular/geometric accent shape (chevron/triangle motif), an underline, a key highlight, or a CTA
  button. Do not flood the whole image with red.
- **Dark navy / charcoal: `#0F1B2D`–`#1A2233`** — primary background for hero / eyecatch banners.
- **White `#FFFFFF`** — primary text on dark backgrounds; primary background for in-body diagrams.
- **Neutral grays** — secondary text, separator lines, cards.

Do **not** make the brand blue. Earlier drafts used a blue/teal palette, which is off-brand. The
TryWith accent is **red `#DC3545`** on dark navy + white.

## Tone & style
- Modern, professional, trustworthy BtoB tech. Clean and uncluttered with generous whitespace.
- A bilingual feel is on-brand (Japanese headline plus the occasional short English label such as
  "Solutions" or "AI"), but Japanese stays primary and must be correct.
- Imagery: modern tech / business scenes (offices, dashboards, abstract tech, cityscapes) under a
  dark overlay for hero banners; or clean flat vector for diagrams.
- Echo the brand's subtle angular red accent (a chevron / triangle shape) rather than heavy
  decoration.

## Logo
Do **not** try to render the actual "TryWith" logo inside a generated image — AI will distort the
wordmark. Convey the brand through palette, the red accent, and tone instead. If the real logo is
truly required, overlay the official logo file afterward in an editor.

## Aspect ratio by placement (always state it explicitly in the prompt)
- **Eyecatch / OGP — the `image` field: 1200×630 (1.91:1)**, matching the site's OG image.
- **In-body figures / diagrams: 16:9 landscape** (clean, full-width friendly). Use 4:3 only for a
  dense diagram. Keep every in-body figure in one article at the **same** ratio for consistency.
- Never leave aspect ratio to chance — name the ratio (and, for the eyecatch, the 1200×630 size)
  in the prompt.

## Two banner directions (choose per article)
1. **Dark hero (default, closest to the site):** dark navy tech scene, white Japanese headline,
   red `#DC3545` accent. Use this for most corporate-site eyecatches.
2. **Light clean:** white / light background, dark text, red accent — for lighter, friendly topics.

Default to the dark hero for the eyecatch unless the topic clearly calls for a lighter feel.
