---
name: seo-article-writer
description: >-
  Create SEO-optimized Japanese article drafts for the corporate site of 株式会社TryWith
  (TRYWITH), aimed at corporate decision-makers and managers, to drive inquiries. Use
  whenever the user wants to write, draft, or plan a blog post, SEO article, コラム, or
  オウンドメディア記事 for TryWith or for its services (システム受託開発 / AIソリューション開発 /
  システム開発支援 / 小売向けシステム開発 / スポットCTO / 店舗ビジネス向けシステム開発). Runs the full
  workflow: frame the reader and search intent, do web research, check Directus for
  duplicate articles, write keywords→intent→title→meta→headings→full body→CTA, generate a
  Japanese text banner plus supporting figures, upload the images to Directus, and register
  the article in Directus as a draft. Trigger on phrases like "記事を書いて", "SEO記事を作って",
  "ブログ記事のドラフト", "コラムを作成して", "オウンドメディアの記事", "TryWithの集客記事".
---

# TRYWITH SEO Article Writer

Write SEO-optimized Japanese article drafts for the corporate site of **株式会社TryWith**
(referred to as TRYWITH). The reader is a corporate decision-maker or担当者; the goal of
every article is to **increase inquiries (問い合わせ・相談)**. Core services this content
supports: システム受託開発 / AIソリューション開発 / システム開発支援 / 小売向けシステム開発 /
スポットCTO / 店舗ビジネス向けシステム開発.

Treat **https://trywith.co.jp/** as the source of truth for company facts. Read
`references/company-profile.md` for the service list, naming conventions, and safety rules
(never fabricate results, numbers, client names, or effects). When mentioning the company in
the body, use natural Japanese such as 「弊社」or「株式会社TryWith」as the context warrants;
do not mechanically repeat the all-caps "TRYWITH" in headings and body — prefer how a natural
Japanese corporate article would read.

## Workflow

### 1. Frame the article
Settle, briefly: who it is for, which service/課題 it ties to, what search intent it must
satisfy, and how it leads to an inquiry. If the request is underspecified, adopt the most
reasonable assumptions from the request plus the company profile and proceed — do not stall
on a list of clarifying questions. State minimal「想定」at the top of the draft only when an
assumption materially affects the result. Producing a usable draft comes first.

### 2. Research as needed
Use web search to reinforce search intent, common comparison angles, and phrasing that the
industry actually uses. Keep all company-specific facts grounded in trywith.co.jp. Never
assert unverified track records, numbers, or absolutes.

### 3. Check Directus for duplicates — BEFORE writing
Follow `references/directus-workflow.md`. Inspect **only the 記事 (article) data model** — no
other models, files, or auxiliary tables. First understand its schema, then review existing
titles, themes, slugs, and key points. Treat not only exact matches but articles whose search
intent /訴求軸 / 構成 are too close as duplicate candidates. If overlap is likely, differentiate
by angle, target reader, comparison lens, how examples are placed, or which service is featured.

### 4. Write the full draft
Produce the deliverable in the standard order defined in
`references/deliverable-and-visuals.md` (keywords → search intent → title options → meta
description → heading structure → full body → CTA). Apply the writing standards and content
guidance in `references/writing-and-review.md`. Finish the **body in full**, not just an
outline, at a polish level ready for publishing prep.

**Apply AEO too — see `references/aeo.md`.** Lead each section with a direct answer (結論ファースト),
phrase headings as the questions readers actually ask, define the core term up top, and include a
**FAQ** section of 3–6 Q&A. Also output suggested **Article / FAQPage JSON-LD** for the site to
embed. SEO and AEO are complementary — keep the writing natural, never keyword-stuff.

### 5. Create images (banner + figures)
Generate at least **three** images: a text-bearing **banner** plus **two or more supporting
figures / 図版**, and increase the figure count with the article's length (more text and more
major sections → more figures). A banner plus a single figure is no longer sufficient. Use the available image-generation capability — the **codex-imagegen** skill (Codex
image generation) if installed, otherwise whatever "Create image" tool is available. Put short,
highly readable Japanese text in the banner; favor a calm, trustworthy BtoB look with a
natural, human-made feel. Diagram anything clearer as a figure (業務/導入フロー, システム構成,
現状→改善後の比較, 意思決定の流れ, 支援範囲・役割分担).

**Match the TryWith brand.** Before generating, read `references/brand-guide.md` and fold its
palette, tone, and aspect ratios into every prompt: the accent is **red `#DC3545` on dark navy
(not blue)**; the **eyecatch is 1200×630 (1.91:1)** and **in-body figures are 16:9**. State the
aspect ratio explicitly in each prompt.

**Verify the Japanese in every image (two gates).** (1) Run the bundled OCR check —
`scripts/verify_image_text.py --image <png> --expect "<exact text>" [--expect ...]` — which
confirms the intended Japanese actually rendered (exit 0 = pass). (2) Also view the image and
apply the checklist in `references/deliverable-and-visuals.md`. Regenerate on any failure until
the Japanese is correct and legible. OCR is a strong gate for headlines but can under-read tiny
labels, so the visual check stays the final authority.

### 6. Upload images to Directus, then use their URLs
Upload every image to Directus **first**, then embed the returned Directus URL in the body /
article data. Never reference a local temp file or an un-uploaded path. Follow the field-
placement rules in `references/directus-workflow.md` (embed in the body when it is HTML /
Markdown / rich text; use a dedicated image/eyecatch field only when the schema clearly has
one for that purpose).

For the upload mechanism itself, see `references/directus-workflow.md` §D — the Directus MCP
cannot upload binaries, so push image files via the Directus REST API (`POST /files`) using a
token read from the OS secret store (Windows Credential Manager / DPAPI, macOS Keychain), then
reference `{DIRECTUS_URL}/assets/{id}`. Article (`posts`) content updates still go through the
Directus MCP `items` tool.

### 7. Register the article as a draft in Directus
Confirm the 記事 schema (required fields, exact field names, input formats) **before** saving;
never guess field names. Always save with status = **`draft`** — for new records and updates
alike. Never publish or set `published`.

### 8. Final Japanese review
Before final output, review the writing per the checklist in
`references/writing-and-review.md`: remove translationese / AI-sounding phrasing, fix tone that
is too stiff or mechanical, and ensure natural flow and subject–predicate agreement. The
finished article must read as something a human writer produced for a corporate site.

## References
- `references/company-profile.md` — services, naming conventions, source of truth, safety.
- `references/directus-workflow.md` — duplicate check, schema-first rules, draft-only
  registration, image upload and URL placement.
- `references/writing-and-review.md` — writing standards, content guidance, final review checklist.
- `references/aeo.md` — AEO: direct answers, question headings, FAQ, definitions, JSON-LD hints.
- `references/deliverable-and-visuals.md` — default deliverable order, image/banner direction,
  visual-explanation (図解) guidance.
- `references/brand-guide.md` — TryWith palette/tone, logo rule, and aspect ratios per placement.
- `scripts/verify_image_text.py` — OCR gate that the intended Japanese rendered in an image.
