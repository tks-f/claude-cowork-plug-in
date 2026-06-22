---
name: codex-imagegen
description: >-
  Generate images with OpenAI Codex's built-in /imagegen tool on Windows (it uses the
  signed-in ChatGPT account, so no OPENAI_API_KEY is needed). Use this WHENEVER the user
  wants to create, generate, or make an image, illustration, photo, banner, thumbnail,
  hero/eyecatch/OGP image, product mockup, or any raster visual with Codex -- even if they
  don't say the word "Codex", as long as Codex is their available image generator. Also
  use it for blog/article banners: read the article, design a prompt, then generate.
  It handles in-image text (including short Japanese), custom size/aspect ratio, and
  reliably retrieves the full-resolution PNG from Codex's session log. Trigger on requests
  like "Codexで画像生成して", "この記事のバナーを作って", "アイキャッチ画像を作って",
  "サムネを生成して", "generate an image of...", "make a banner for this post".
compatibility: >-
  Requires Windows with the Codex CLI installed and signed in (codex --version works), and
  a way to run PowerShell on that machine (e.g. the Windows-MCP PowerShell tool). Uses the
  bundled script scripts/generate_image.ps1.
---

# Codex Image Generation

Generate raster images (photos, illustrations, banners, mockups, icons) by driving the
OpenAI **Codex CLI** and its built-in `/imagegen` skill. Codex generates with its built-in
`image_gen` tool using the user's signed-in ChatGPT account, so **no API key is required**.

## Why this skill exists (read this once)

Driving Codex for images by hand has three sharp edges that this skill smooths over:

1. **Codex does not reliably save the file you ask for.** In this environment the built-in
   image tool keeps the full-resolution PNG only as **base64 inside its session log**
   (`%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl`) and drops just a tiny
   preview thumbnail in `%TEMP%`. The reliable way to get the real image is to **extract it
   from the session log** — which the bundled script does for you.
2. **Quoting and encoding are fragile.** Passing the prompt straight on a PowerShell/cmd
   command line mangles embedded quotes and corrupts non-ASCII text (e.g. Japanese). The
   script avoids this by reading the prompt from a UTF-8 file and feeding Codex via stdin.
3. **It needs the right flags and it's slow.** `codex exec` must run with
   `--skip-git-repo-check -s workspace-write`, and a single image takes ~2–4 minutes, so
   the run is launched detached and polled.

The bundled `scripts/generate_image.ps1` handles all three. Prefer it over ad-hoc commands.

## Prerequisites

- Codex CLI installed and signed in. Quick check (via PowerShell): `codex --version`.
  If missing, tell the user to install Codex and sign in, then retry.
- Ability to run PowerShell on the user's Windows machine (the Windows-MCP `PowerShell`
  tool). All script calls below go through it.

## Core workflow — generate one image

### 1. Write the prompt to a UTF-8 file (do NOT type it into a PowerShell command)

Use the **Write tool** to save the image description to a UTF-8 text file in your outputs/
working folder, e.g. `…\outputs\codex_prompt.txt`. Writing the prompt with the file tool
(rather than embedding it in a shell command) is what keeps Japanese and other non-ASCII
text from being corrupted.

A good prompt specifies, in plain language:

- **Subject / scene** — what is in the image.
- **Style** — e.g. "photorealistic", "modern flat vector illustration", "3D glossy render".
- **Size / aspect** — e.g. "ultra-wide 1.91:1 banner (OGP/thumbnail)", "square 1:1",
  "portrait 4:5". Codex picks a sensible resolution from this.
- **In-image text (optional)** — give the EXACT text verbatim. English renders cleanly;
  Japanese can garble, so keep Japanese short and plan to verify (see references/prompting.md).

See `references/prompting.md` for recipes and a worked banner prompt.

### 2. Launch generation (detached)

Run the bundled script with `-Action start`. Use the script's absolute path (this skill's
folder + `\scripts\generate_image.ps1`) and an absolute `-OutputPath`:

```
powershell -NoProfile -ExecutionPolicy Bypass -File "<SKILL_DIR>\scripts\generate_image.ps1" `
  -Action start -PromptFile "<…\outputs\codex_prompt.txt>" -OutputPath "<…\outputs\image.png>"
```

It returns compact JSON like `{"status":"started","workdir":"C:\\...\\codex-imagegen\\1a2b3c4d","output":"..."}`.
**Save the `workdir`** — you pass it to every poll.

### 3. Poll until done (≈2–4 minutes)

Wait ~30 seconds, then call `-Action collect` with the `workdir`. Repeat until the status
is `done`. (Keep each poll short; don't sleep for minutes inside one PowerShell call —
generation continues on its own between polls.)

```
powershell -NoProfile -ExecutionPolicy Bypass -File "<SKILL_DIR>\scripts\generate_image.ps1" `
  -Action collect -WorkDir "<workdir from step 2>"
```

Statuses:

- `running` → wait ~30s and poll again.
- `done` → `{"status":"done","path":"…","width":…,"height":…}`; the PNG is saved at `path`.
- `failed` → Codex finished without producing an image; read `codex.log` in the workdir
  and see `references/troubleshooting.md`.
- `timeout` → exceeded the time budget; see troubleshooting.

### 4. Deliver

The PNG is at `OutputPath` (on the user's machine). To show it: make sure a copy is in your
outputs folder, **view it with the Read tool to verify quality** (especially any in-image
text), then present it with `present_files`. Report the saved location and dimensions.

## Article / blog banner workflow

When the user wants a banner, thumbnail, or eyecatch for an article or blog post, follow
`references/banner-workflow.md`: fetch the article, distill its topic, design a banner
prompt (composition, OGP size 1200×628, optional title text), then run the core workflow
above. Offer a text and a no-text variant when appropriate.

## Good defaults

- **Banner / OGP / eyecatch** → ultra-wide ~1.91:1 (1200×628).
- **Social square** → 1:1. **Hero** → 16:9.
- Always confirm in-image text wording with the user when it matters; verify the rendered
  result by viewing the PNG, since text (especially Japanese) can come out wrong.

## Reference files

- `references/prompting.md` — how to write effective prompts; in-image text guidance; a
  worked banner example.
- `references/banner-workflow.md` — end-to-end steps for article/blog banners.
- `references/troubleshooting.md` — what to do on `failed`/`timeout`, how the session-log
  extraction works, flags, encoding, and Codex-not-found.
