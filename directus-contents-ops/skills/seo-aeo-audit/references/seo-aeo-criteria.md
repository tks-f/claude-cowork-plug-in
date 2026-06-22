# SEO + AEO audit criteria

What the audit checks and what "good" looks like. The script (`scripts/audit_article.py`) covers
the measurable items; apply judgment for the qualitative ones.

## SEO
- **Title** — present; about 28–35 full-width characters; includes the primary keyword naturally.
- **Meta description (excerpt)** — present; about 80–120 characters; compelling, not truncated and
  not keyword soup.
- **Slug** — lowercase ASCII + hyphens, concise and readable.
- **Heading structure** — several H2/H3 that map the article's logic; one clear topic per heading.
- **Keyword & intent** — primary keyword in the title, the first paragraph, and at least one
  heading; the search intent is genuinely answered (judgment).
- **Depth** — enough body to satisfy the intent (a BtoB explainer is usually ~1,500+ characters);
  not thin.
- **Links** — at least one relevant internal / related or source link.
- **Eyecatch & images** — the eyecatch (`image`) is set; in-body images have alt text.

## AEO (Answer Engine Optimization)
- **結論ファースト** — the intro and each section state the answer first, then elaborate (judgment).
- **Question-style headings** — headings phrased as the questions users actually ask
  (〜とは / 〜は？ / 違いは？).
- **FAQ section** — a「よくある質問」block of real Q&A; high value for answer engines and snippets.
- **Extractable structure** — bullet lists and small tables for key facts.
- **Early definition** — the core term is defined near the top.
- **Citability** — claims are specific and grounded (trywith.co.jp for company facts); never
  fabricated.
- **Structured data** — Article / FAQPage JSON-LD is recommended for the site to embed (it lives in
  the template, not the Markdown body).

## Scoring
`seo_score` and `aeo_score` are weighted pass rates (severity weights: high=3, med=2, low=1). Treat
them as a triage signal, not an absolute grade — always read `top_issues` and add qualitative
judgment before recommending changes.
