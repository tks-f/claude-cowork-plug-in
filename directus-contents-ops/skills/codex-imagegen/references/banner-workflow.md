# Article / blog banner workflow

Use this when the user wants a banner, thumbnail, eyecatch, or OGP image for a specific
article or blog post (often given as a URL).

## Steps

1. **Get the content.** If a URL is given, fetch it (web_fetch). Identify the **title**,
   the core **topic**, and any **tags/keywords**. If it's pasted text, read that instead.

2. **Decide direction (ask if ambiguous).** Two choices drive the result the most, so when
   they're not obvious, ask the user briefly:
   - **Style** — photorealistic / flat illustration / 3D.
   - **Text treatment** — Japanese title baked in (warn: AI may garble Japanese), English
     only, or no text (cleanest; user overlays their own title). Offer "no text" as the
     safe default when unsure.

3. **Pick the size.** Default to **OGP 1200×628** (`ultra-wide 1.91:1`) unless the user's
   platform wants something else.

4. **Design the prompt.** Translate the article's topic into a concrete scene that evokes
   it (don't just restate the title). Name a palette, request clean negative space for any
   text, and if including a title, give the exact wording verbatim and keep Japanese short.
   See `prompting.md` for a worked example.

5. **Generate** via the core workflow in SKILL.md (write prompt → `-Action start` →
   poll `-Action collect`).

6. **Verify and deliver.** View the PNG with the Read tool — check the scene and, critically,
   that any in-image text is spelled correctly. Then present it. When a title was baked in,
   it's often worth also producing a **no-text version** of the same scene so the user can
   typeset the headline themselves; offer both.

## Tips

- Tech articles usually look best as either a clean flat illustration or a tidy
  photorealistic desk/terminal scene with a warm accent color.
- If the baked-in Japanese title comes out wrong, don't fight it many times — switch to a
  no-text banner and tell the user they can overlay the title in any editor.
