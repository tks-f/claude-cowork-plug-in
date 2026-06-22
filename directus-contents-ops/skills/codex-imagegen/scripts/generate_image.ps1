<#
.SYNOPSIS
  Generate an image with OpenAI Codex's built-in /imagegen skill and save it as a PNG.

.DESCRIPTION
  `codex exec` generates the image with its built-in image_gen tool (it uses the
  signed-in ChatGPT account, so no OPENAI_API_KEY is needed). In this environment Codex
  does NOT reliably write the full-resolution file to the path you ask for -- instead it
  embeds the PNG as base64 inside its session "rollout" log under
  %USERPROFILE%\.codex\sessions\YYYY\MM\DD\rollout-*.jsonl (and only drops a tiny preview
  thumbnail in %TEMP%). This script therefore launches Codex detached and then extracts
  the full-resolution PNG straight from the new session log -- which is more reliable than
  hoping Codex saves the file.

  Image generation takes ~2-4 minutes and the calling tool (Windows-MCP PowerShell) has a
  short timeout, so the work is split into two actions you call separately:
    -Action start    : launch Codex detached, return immediately (prints the WorkDir)
    -Action collect  : check progress; once ready, decode the PNG to -OutputPath

.PARAMETER Action      start | collect
.PARAMETER PromptFile  (start) UTF-8 text file containing the image description/prompt.
                       Use a file (not a command-line arg) so non-ASCII text such as
                       Japanese survives intact.
.PARAMETER OutputPath  (start/collect) Absolute path for the final .png.
.PARAMETER WorkDir     Run-state directory. `start` auto-creates one and prints it in its
                       JSON; pass that same value back to `collect`.
.PARAMETER TimeoutSec  (start) Seconds before collect reports 'timeout'. Default 360.

.OUTPUTS
  Compact JSON on stdout, e.g.
    {"status":"started","workdir":"...","output":"..."}
    {"status":"running","elapsed":42,"codexFinished":false}
    {"status":"done","path":"C:\\out\\img.png","width":1536,"height":1024,"bytes":1662780}
    {"status":"failed","reason":"..."}  |  {"status":"timeout","elapsed":361}

.EXAMPLE
  $r = .\generate_image.ps1 -Action start  -PromptFile C:\tmp\prompt.txt -OutputPath C:\out\img.png
  # wait ~30s, then poll until status=done:
  .\generate_image.ps1 -Action collect -WorkDir <workdir-from-start>
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][ValidateSet('start', 'collect')][string]$Action,
  [string]$PromptFile,
  [string]$OutputPath,
  [string]$WorkDir,
  [int]$TimeoutSec = 360
)
$ErrorActionPreference = 'Stop'

function Get-CodexPath {
  $c = Get-Command codex -ErrorAction SilentlyContinue
  if ($c) { return $c.Source }
  $p = Join-Path $env:LOCALAPPDATA 'Programs\OpenAI\Codex\bin\codex.exe'
  if (Test-Path $p) { return $p }
  throw 'codex CLI not found. Install Codex and ensure `codex` is on PATH (try: codex --version).'
}

function Get-Rollouts {
  $base = Join-Path $env:USERPROFILE '.codex\sessions'
  if (-not (Test-Path $base)) { return @() }
  @(Get-ChildItem $base -Recurse -File -Filter 'rollout-*.jsonl' -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName)
}

# Read a file even while another process holds it open for writing. Codex keeps the
# rollout log open during a run, so a plain ReadAllText throws a sharing violation.
function Read-AllTextShared([string]$path) {
  $fs = [System.IO.File]::Open($path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
  try {
    $sr = New-Object System.IO.StreamReader($fs, [System.Text.Encoding]::UTF8)
    try { return $sr.ReadToEnd() } finally { $sr.Dispose() }
  }
  finally { $fs.Dispose() }
}

# Find the largest base64-encoded PNG inside a rollout log and write it to $dest.
# Returns the byte length on success, or $null if no PNG was found.
function Export-PngFromRollout([string]$rolloutPath, [string]$dest) {
  $txt = Read-AllTextShared $rolloutPath
  $best = $null; $bestLen = 0
  foreach ($m in [regex]::Matches($txt, '[A-Za-z0-9+/]{20000,}={0,2}')) {
    $b = $m.Value; $r = $b.Length % 4; if ($r) { $b = $b.Substring(0, $b.Length - $r) }
    try { $by = [Convert]::FromBase64String($b) } catch { continue }
    # PNG magic bytes: 89 50 4E 47
    if ($by.Length -gt 8 -and $by[0] -eq 0x89 -and $by[1] -eq 0x50 -and $by[2] -eq 0x4E -and $by[3] -eq 0x47 -and $by.Length -gt $bestLen) {
      $best = $by; $bestLen = $by.Length
    }
  }
  if (-not $best) { return $null }
  $outDir = Split-Path $dest -Parent
  if ($outDir -and -not (Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }
  [System.IO.File]::WriteAllBytes($dest, $best)
  return $bestLen
}

if ($Action -eq 'start') {
  if (-not $PromptFile -or -not (Test-Path $PromptFile)) { throw "PromptFile not found: $PromptFile" }
  if (-not $OutputPath) { throw 'OutputPath is required for -Action start.' }
  if (-not $WorkDir) {
    $WorkDir = Join-Path $env:TEMP ('codex-imagegen\' + [guid]::NewGuid().ToString('N').Substring(0, 8))
  }
  New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null
  $codex = Get-CodexPath

  # Build the instruction. Read the prompt as UTF-8, neutralise any double quotes so the
  # prompt="..." wrapper can't break, collapse whitespace, and tell Codex to just generate
  # (we pull the result from the session log, so it shouldn't waste time saving/searching).
  $desc = [System.IO.File]::ReadAllText($PromptFile, [System.Text.Encoding]::UTF8)
  $desc = (($desc -replace '"', "'") -replace '\s+', ' ').Trim()
  $instr = '/imagegen prompt="' + $desc + '". Generate this image. Treat it as a preview only: do not save, move, copy, rename, or search the filesystem for the output afterward -- simply generating it is sufficient.'
  $enc = New-Object System.Text.UTF8Encoding($false)   # UTF-8, no BOM
  [System.IO.File]::WriteAllText((Join-Path $WorkDir 'instruction.txt'), $instr, $enc)

  # Snapshot existing session logs so `collect` can identify the NEW one this run creates.
  (Get-Rollouts) | Set-Content -Path (Join-Path $WorkDir 'rollouts_before.txt') -Encoding utf8

  # Wrapper .cmd feeds the UTF-8 prompt via stdin redirection (byte-level, so Japanese and
  # other non-ASCII text survive regardless of the console code page).
  $cmd = @"
@echo off
chcp 65001 >nul
cd /d "$WorkDir"
"$codex" exec --skip-git-repo-check -s workspace-write < instruction.txt > codex.log 2>&1
echo DONE exit=%ERRORLEVEL%>> codex.log
"@
  Set-Content -Path (Join-Path $WorkDir 'run.cmd') -Value $cmd -Encoding ascii
  Remove-Item (Join-Path $WorkDir 'codex.log') -ErrorAction SilentlyContinue
  Start-Process -FilePath (Join-Path $WorkDir 'run.cmd') -WorkingDirectory $WorkDir -WindowStyle Hidden

  @{ workdir = $WorkDir; output = $OutputPath; start = (Get-Date).ToString('o'); timeoutSec = $TimeoutSec } |
    ConvertTo-Json | Set-Content -Path (Join-Path $WorkDir 'run.json') -Encoding utf8

  [pscustomobject]@{ status = 'started'; workdir = $WorkDir; output = $OutputPath } | ConvertTo-Json -Compress
  return
}

if ($Action -eq 'collect') {
  if (-not $WorkDir -or -not (Test-Path $WorkDir)) { throw "WorkDir not found: $WorkDir" }
  $run = Get-Content (Join-Path $WorkDir 'run.json') -Raw | ConvertFrom-Json
  if (-not $OutputPath) { $OutputPath = $run.output }

  $before = @()
  if (Test-Path (Join-Path $WorkDir 'rollouts_before.txt')) {
    $before = Get-Content (Join-Path $WorkDir 'rollouts_before.txt')
  }
  $newRollouts = @(Get-Rollouts | Where-Object { $before -notcontains $_ } |
      Get-Item -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)

  $bytes = $null
  foreach ($rl in $newRollouts) {
    $bytes = Export-PngFromRollout $rl.FullName $OutputPath
    if ($bytes) { break }
  }

  if ($bytes) {
    $w = 0; $h = 0
    try {
      Add-Type -AssemblyName System.Drawing
      $im = [System.Drawing.Image]::FromFile($OutputPath); $w = $im.Width; $h = $im.Height; $im.Dispose()
    } catch { }
    [pscustomobject]@{ status = 'done'; path = $OutputPath; width = $w; height = $h; bytes = $bytes } | ConvertTo-Json -Compress
    return
  }

  $elapsed = [int]((Get-Date) - [datetime]$run.start).TotalSeconds
  $codexDone = [bool](Select-String -Path (Join-Path $WorkDir 'codex.log') -Pattern 'DONE exit' -SimpleMatch -ErrorAction SilentlyContinue)
  if ($codexDone) {
    [pscustomobject]@{ status = 'failed'; reason = 'Codex finished but no image was found in the session log. Check codex.log in the WorkDir.'; elapsed = $elapsed } | ConvertTo-Json -Compress
  }
  elseif ($elapsed -ge [int]$run.timeoutSec) {
    [pscustomobject]@{ status = 'timeout'; elapsed = $elapsed } | ConvertTo-Json -Compress
  }
  else {
    [pscustomobject]@{ status = 'running'; elapsed = $elapsed; codexFinished = $codexDone } | ConvertTo-Json -Compress
  }
  return
}
