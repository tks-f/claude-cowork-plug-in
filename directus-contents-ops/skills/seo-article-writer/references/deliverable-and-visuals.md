# Default deliverable & visuals

## Default deliverable order
Unless the user specifies otherwise, return the finished draft in this order:

1. 想定検索キーワード
2. 想定検索意図（AEO: ユーザーが実際に問う質問形クエリも併記）
3. 記事タイトル案
4. メタディスクリプション案
5. 見出し構成（AEO: 見出しは質問形にし、各見出し直下に40〜80字の直接回答を置く）
6. 本文の完成ドラフト（結論ファースト・主要用語の定義を冒頭で明確化。finish the body fully, not just headings）
7. よくある質問（FAQ）— 3〜6問の簡潔なQ&A（回答エンジンに抽出されやすい形）
8. CTA案
9. 構造化データ案（Article / FAQPage の JSON-LD。実装側でDirectus・フロントに埋め込む用）
10. 文字付きバナー画像の生成
11. 記事内で使う補助画像・図版の生成（最低2枚。本文の長さ・セクション数に応じて増やす）

AEO の詳しい指針は `aeo.md` を参照。

The body must be at a granularity that can go straight into publishing prep with light editing.

## Banner & image direction
- **Match the TryWith brand and use the right aspect ratio — see `brand-guide.md`.** The accent
  is red `#DC3545` on dark navy (not blue); the **eyecatch is 1200×630 (1.91:1)** and **in-body
  figures are 16:9**. State the aspect ratio explicitly in every prompt.
- Generate images with the available image tool — prefer the **codex-imagegen** skill (Codex
  image generation). The banner must be a corporate-site-grade, trustworthy visual matched to
  the theme and reader.
- Put short Japanese text in the banner so it works as-is as a banner. Keep text volume low and
  prioritize readability. Aim for a calm BtoB impression with a natural, human-made creative feel.
- Generate **3+ images**: the main text banner **plus at least two** supporting images / 図版
  usable inside the article. Include **at least two** supporting figures even for a short article.
- **Scale the number of supporting figures with the article's length / text volume.** The longer
  the body and the more major sections it has, the more figures it should carry. Rough guide: add
  roughly one figure per major explanatory section, or about one per 1,500–2,000 characters of
  body text — and always more whenever a figure genuinely aids understanding.

## Mandatory Japanese-text verification (every generated image)
After generating, verify the in-image Japanese with **two gates**:

**Gate 1 — automated OCR (hard check).** Run the bundled script to confirm the intended text
actually rendered:
`python scripts/verify_image_text.py --image <png> --expect "<exact text>" [--expect ...]`
(exit 0 = pass; the jpn OCR data is bundled in `scripts/tessdata`). A pass is high confidence; a
fail means inspect and very likely regenerate. OCR reads headlines well but can under-read tiny
labels, so it never overrides a clear visual problem.

**Gate 2 — visual check (final authority).** Look at the image and confirm:
- Wording is natural.
- No typos, garbled characters (文字化け), or unnatural line breaks.
- Font looks correct for Japanese.
- Text is large enough to read as a banner (not too small).
- Text placement and margins look natural.

If readability or appearance is off, do **not** ship it — fix/regenerate until it reads
naturally. (The codex-imagegen skill renders short Japanese well; keep banner text short, give
exact wording, and view the result to confirm before using it.)

## Upload before use
Each image must be **uploaded to Directus before it is used in the article**, and the post-upload
Directus URL reflected into the body / article data (see `directus-workflow.md`). Do not leave
images as local temp files.

## Visual explanation (図解) guidance
Actively diagram parts that are easier to understand visually. Treat a figure as a standard
output candidate for:
- 業務フロー・導入フロー
- システム構成・連携イメージ
- 現状と改善後の比較
- 意思決定までの流れ
- 支援範囲・役割分担

Figures must:
- Use natural, short Japanese labels.
- Avoid cramming in too much — convey the point at a glance.
- Be calm and BtoB-appropriate in design.
- Not contradict the body text.

When a figure helps, weave "which figure goes where" into the body flow, and add a short lead-in
sentence explaining the figure's intent when useful.
