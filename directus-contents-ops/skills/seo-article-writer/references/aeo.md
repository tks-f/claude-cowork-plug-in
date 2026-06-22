# AEO (Answer Engine Optimization)

On top of classic SEO, make the article easy for answer engines (Google AI Overviews, ChatGPT,
Perplexity, Bing Copilot) and featured snippets to **extract, quote, and cite** — while staying
natural for human readers. AEO and SEO are complementary; do both, never sacrifice readability.

## Core principles
- **結論ファースト.** Open each section with a direct answer to its heading in the first 1–2
  sentences (about 40–80 characters), then elaborate. The opening of the article should also state
  the takeaway before the long explanation.
- **質問形の見出し.** Phrase H2/H3 as the actual question a reader would ask (e.g.「スポットCTOとは？」
  「費用はどれくらい？」「常勤CTOと何が違う？」). Heading + its first sentence should read as a
  self-contained Q&A.
- **定義を冒頭で明確化.** Define the core term / entity clearly near the top (1–2 sentences) so an
  engine can lift a clean definition.
- **抽出しやすい構造.** Short paragraphs, bullet lists, and small comparison tables for key facts.
  Don't bury the answer inside long prose.
- **FAQ セクション.** Add a「よくある質問」section with 3–6 real Q&A pairs, each answer 1–3 sentences.
  This maps directly to FAQ rich results and is highly citable. Questions must be ones users
  actually ask; answers must add real value (no filler).
- **エンティティを明示.** Name entities explicitly (service names, 株式会社TryWith, related terms)
  instead of relying on pronouns, so each passage stands alone out of context.
- **根拠・一次情報.** Make factual statements verifiable and grounded — company facts from
  trywith.co.jp, general facts from reputable sources. Never fabricate stats or claims; sourced,
  checkable statements are what answer engines prefer to cite.

## Structured data (hand off to the site / Directus)
The body is Markdown, so JSON-LD normally lives in the site template. Provide ready-to-use schema
as part of the deliverable so the front-end / Directus can embed it:
- **Article** (or BlogPosting) JSON-LD: `headline`, `description`, `datePublished`, `author`
  (株式会社TryWith), `image`.
- **FAQPage** JSON-LD built from the FAQ section's Q&A.

Output these as fenced code blocks labelled「構造化データ（実装側で埋め込み）」. Present them as a
suggestion; do not invent fields the site cannot populate, and do not claim the page already emits
schema unless confirmed.

## What NOT to do
- No keyword stuffing and no robotic Q&A written only to game engines — everything must read
  naturally for a human.
- No FAQ entries that carry no real information.
- Don't overclaim structured-data support; JSON-LD is a recommendation for the implementer.
