# Prompting for Codex image generation

Codex's built-in image tool responds well to clear, descriptive prompts written in plain
language. You don't need keyword soup — full phrases work. Cover four things:

## 1. Subject / scene
What is actually in the frame. Be concrete: objects, people, setting, action, mood.

## 2. Style
Pick one clear direction, e.g.:
- `photorealistic`, `professional stock-photo quality`, `cinematic shallow depth of field`
- `modern flat vector illustration`, `clean minimal tech illustration`
- `3D glossy render`, `soft gradient, depth`
- `watercolor`, `isometric`, `line art`

## 3. Size / aspect ratio
State it in words and the tool picks a sensible resolution:
- Banner / OGP / eyecatch → `ultra-wide 1.91:1 banner (OGP / social thumbnail)` ≈ 1200×628
- Hero → `16:9 wide`
- Social square → `1:1 square`
- Portrait → `4:5` or `3:4`

## 4. In-image text (optional)
If text should appear in the image, give the **exact text verbatim** and where it goes.

- **English renders reliably.** Brand names and short English labels usually come out clean.
- **Japanese can garble.** Keep in-image Japanese **short** (a few characters / one short
  phrase), state it exactly, and **always verify** by viewing the generated PNG with the
  Read tool. If it's wrong, regenerate, shorten the text, or switch to a no-text version
  the user can typeset themselves.
- Ask for a `clean negative space` region (e.g. "leave the left third empty for text") if
  the user plans to overlay their own copy later.

## Worked example — article banner (this actually rendered correctly)

> Photorealistic ultra-wide horizontal banner for a tech blog article header, 1.91:1
> aspect ratio (OGP / social thumbnail). Scene: a bright, modern, minimalist desk
> workspace shot slightly from above with cinematic shallow depth of field; a sleek laptop
> and an external monitor display colorful terminal windows full of code; a coffee cup, a
> notebook, and a smartphone on a light wood desk; soft warm natural window light; clean,
> energetic, productive mood. Warm palette of white and light wood with a glowing
> warm-orange (#D97757) accent from the screens. Keep clean negative space in the left
> third for text. Render bold, perfectly legible Japanese headline text reading exactly:
> 日常業務を爆速化 — large modern sans-serif — with a smaller English label reading exactly:
> Claude Code just above it. Sharp, high-contrast text, no garbled characters, no watermark.

Notes on why it worked: the scene is specific, the palette is named, a text-safe negative
space is requested, and the in-image Japanese is a single short phrase given verbatim.
