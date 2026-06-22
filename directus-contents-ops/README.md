# TRYWITH SEO Article Agent

A Cowork plugin that turns the 株式会社TryWith SEO article-writing agent into a reusable skill.
It drafts inquiry-driving, SEO-optimized Japanese articles for the corporate site, checks
Directus for duplicates, generates Japanese banner/figure images, uploads them to Directus, and
registers the finished article as a **draft**.

## What it does

This plugin bundles **three skills**: `seo-article-writer` (the workflow below), `codex-imagegen`
(Codex-based image generation for the banner and figures), and `seo-aeo-audit` (audit existing
articles — including drafts — for SEO/AEO and list prioritized fixes). Image generation is bundled,
so the plugin is self-contained for visuals.

To audit existing content, say things like「既存記事のSEO/AEOをチェックして」「下書きの記事を診断して」.
The `seo-aeo-audit` skill reads `posts` from Directus, scores each article, and reports fixes
(read-only by default).

Given an article theme, the `seo-article-writer` skill runs the full workflow:

1. Frames the article (reader, service, search intent, conversion path).
2. Does web research to reinforce search intent and comparison angles.
3. Checks the Directus **記事** data model for near-duplicate articles and differentiates if needed.
4. Writes the full **SEO + AEO** deliverable: 検索キーワード → 検索意図 → タイトル案 →
   メタディスクリプション → 見出し構成 → 本文の完成ドラフト → FAQ → CTA案 → 構造化データ（JSON-LD）案.
5. Generates a Japanese text **banner** plus **two or more** supporting **figures / 図版**
   (scaled to the article's length, on-brand per the TryWith palette and aspect ratios), then
   verifies the in-image Japanese with an automated OCR check plus a visual review.
6. Uploads each image to Directus and uses the returned Directus URL in the article.
7. Registers the article in Directus with status **`draft`** (never published), schema-first.

## Triggering

Say things like:「○○についてのSEO記事を書いて」「AI導入のコラムを作成して」「小売向けシステム開発の集客記事のドラフト」.
The skill activates automatically for TryWith article/コンテンツ requests.

## Required / recommended connectors

This plugin does **not** bundle any credentials. Connect these in Cowork (Settings → Connectors /
Capabilities):

| Capability | Why | Required? |
|---|---|---|
| **Directus** (MCP connector) | Duplicate check, image upload, draft registration | **Required** |
| **Web search** | Reinforce search intent / comparison angles | Built-in |
| **Codex CLI** (Windows, signed in) | Used by the bundled `codex-imagegen` skill to generate images | Required for images |

The `codex-imagegen` skill is **bundled in this plugin** (no separate install). It drives the
signed-in Codex CLI on Windows, so no OPENAI_API_KEY is needed. The OCR check ships its own
Japanese data (`scripts/tessdata`) and uses `pytesseract` + `pillow`.

If Directus is not connected, the skill can still draft the article text, but it cannot run the
duplicate check, upload images, or save the draft until Directus is available.

## Guardrails baked in

- **Draft only** — articles are always saved with status `draft`; never published.
- **Schema-first** — the skill confirms the actual Directus 記事 schema before saving and never
  guesses field names.
- **No fabrication** — no invented track records, numbers, client names, or effects; company
  facts are grounded in https://trywith.co.jp/.
- **Natural Japanese** — a final review pass removes AI-sounding / translationese phrasing.

## Structure

```
seo-article-writer/
├── .claude-plugin/plugin.json
├── skills/
│   ├── seo-article-writer/
│   │   ├── SKILL.md
│   │   ├── references/  (company-profile, directus-workflow, writing-and-review,
│   │   │                 deliverable-and-visuals, brand-guide, aeo)
│   │   └── scripts/verify_image_text.py  (+ tessdata/jpn.traineddata)
│   ├── codex-imagegen/
│   │   ├── SKILL.md
│   │   ├── references/  (prompting, banner-workflow, troubleshooting)
│   │   └── scripts/generate_image.ps1
│   └── seo-aeo-audit/
│       ├── SKILL.md
│       ├── references/seo-aeo-criteria.md
│       └── scripts/audit_article.py
└── README.md
```
