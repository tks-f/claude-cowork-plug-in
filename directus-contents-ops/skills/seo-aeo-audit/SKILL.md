---
name: seo-aeo-audit
description: >-
  Audit existing 株式会社TryWith articles in Directus (including drafts) for SEO and AEO, score each,
  and list concrete prioritized fixes. Use when the user wants to check / 診断 / 監査 existing
  articles' SEO or AEO, review drafts before publishing, find weak or thin articles, or get an
  improvement to-do list across the blog. Trigger on 「既存記事のSEOチェック」「記事のSEO/AEO診断」
  「下書きのSEOを見て」「postsのSEO監査」「公開前にSEO/AEOチェック」「記事の改善点を洗い出して」など.
  Read-only by default — it reports; it does not change articles unless explicitly asked.
---

# Existing article SEO / AEO audit

Review articles already in Directus (the 記事 / `posts` model, **including drafts**) against an SEO
and AEO checklist, and produce a prioritized improvement report. Read-only by default.

## Workflow

### 1. Choose scope
Default: all articles **including drafts**. Honor any filter the user gives — status (`draft` /
`published`), a specific slug or title, "recent N", or a single id.

### 2. Read the articles from Directus
Use the connected Directus MCP to read the `posts` model. Confirm field names from the schema
first, then pull `id, title, slug, excerpt, content, tags, image, status, date_published`.

### 3. Run the automated checks per article
For each article, write its fields to a UTF-8 JSON file and run:
`python scripts/audit_article.py --file <article.json>`
It returns `seo_score`, `aeo_score`, `metrics`, and a prioritized `top_issues` list (title/meta
length, slug, heading structure, keyword use, content length, links, eyecatch, image alt; and for
AEO: question-style headings, FAQ presence, extractable structure, early definition).

### 4. Add the qualitative review the script cannot do
Judge what metrics can't: is the primary keyword / search intent genuinely matched? Is the opening
結論ファースト? Are the headings truly answer-shaped? Is the Japanese natural and trustworthy? Does it
actually drive an inquiry (clear CTA)? See `references/seo-aeo-criteria.md`.

### 5. Report
Lead with a **summary table** (article → status, SEO score, AEO score, top issue), sorted
worst-first. Then per-article detail with concrete, prioritized fixes (what to change and why),
grouped into quick wins vs. larger rewrites.

### 6. Read-only by default
Do not modify articles. If the user asks you to apply fixes, do it one article at a time with
confirmation, following the `seo-article-writer` rules (schema-first, keep `status` as-is, never
publish a draft).

## References
- `scripts/audit_article.py` — automated SEO/AEO metrics for one article (JSON in, JSON out; stdlib only).
- `references/seo-aeo-criteria.md` — the full SEO + AEO checklist and what "good" looks like.
