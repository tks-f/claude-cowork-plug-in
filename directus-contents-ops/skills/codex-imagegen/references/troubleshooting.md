# Troubleshooting & how it works

## How retrieval works (why the script reads the session log)

Codex's built-in image tool, in this environment, does **not** dependably write the
full-resolution PNG to the path you request. Instead the full image is stored as **base64
inside the session "rollout" log**: `%USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl`.
A standalone base64 PNG always begins with `iVBORw0KGgo` (PNG magic bytes `89 50 4E 47`).
`%TEMP%` usually also gets a small **preview thumbnail** (a few hundred px) — that is NOT
the deliverable; ignore it.

`generate_image.ps1` therefore:
1. snapshots existing rollout files before launching (so it can spot the new one),
2. launches `codex exec --skip-git-repo-check -s workspace-write` with the prompt on stdin,
3. on `collect`, scans the new rollout for the **largest** decodable base64 PNG and writes
   it to your `-OutputPath`.

## status = failed

"Codex finished but no image was found." Open `codex.log` in the run's `WorkDir` and look
for the cause:

- **Not signed in / auth error** → have the user run `codex login` (or open Codex once and
  sign in), then retry.
- **Refusal / safety** → the prompt was declined; rephrase.
- **`/imagegen` not available** → confirm the imagegen skill exists:
  `Test-Path "$env:USERPROFILE\.codex\skills\.system\imagegen"`. If absent, update Codex.

The flags `--skip-git-repo-check` (run outside a git repo) and `-s workspace-write` are
already set by the script, so the classic "Not inside a trusted directory" and sandbox
write errors should not occur.

## status = timeout

Generation exceeded the budget (default 360s). Re-run `-Action start` with a larger
`-TimeoutSec`, and keep polling. A complex prompt, a slow network, or Codex hunting for the
file can all add time. You can also check whether Codex is still working:
`Get-Process codex` (several `codex` processes during a run is normal).

## In-image text came out garbled

Most common with Japanese. Options, in order: regenerate; shorten the in-image text; give
the exact characters verbatim; or switch to a **no-text** version and let the user overlay
the title in an editor. English text is usually fine.

## codex not found

`generate_image.ps1` looks for `codex` on PATH, then at
`%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe`. If neither exists, install the Codex
CLI and ensure `codex --version` works, then retry.

## A codex process keeps running after `done`

The script returns `done` as soon as the image is in the session log, which can be a bit
before Codex's own run finishes tidying up. The leftover `codex` process is harmless and
exits on its own. If you want to stop it immediately and no other Codex work is running:
`Get-Process codex -ErrorAction SilentlyContinue | Stop-Process -Force`.

## Encoding / non-ASCII prompts

Always write the prompt with the Write tool to a UTF-8 file and pass it as `-PromptFile`.
The script re-encodes it to UTF-8 (no BOM) and feeds Codex via stdin redirection, which is
byte-exact and immune to the console code page — this is what keeps Japanese intact. Do not
build the prompt inline in a PowerShell/cmd command.
