# Directus workflow

All Directus operations use the connected **Directus MCP**. The user must have Directus
connected (see the plugin README). Two phases touch Directus: the duplicate check (before
writing) and registration (after the draft + images are ready).

## A. Duplicate check — before writing
1. Inspect **only the 記事 (article) data model.** Do not scan other data models, content
   types, files, or auxiliary tables for duplication.
2. First **understand the schema** of the 記事 model (fields, types).
3. Then review existing articles: titles, themes, slugs, and key points.
4. Judge overlap by **search intent / 訴求軸 / 構成**, not just exact title matches. An article
   whose intent and structure are too close counts as a duplicate candidate.
5. If overlap is likely, differentiate the new article: shift the切り口, target reader,
   comparison lens, how examples are placed, or which service is featured.

## B. Schema-first registration — after the draft is ready
1. **Re-confirm the 記事 schema** before saving: required fields, exact field names, and input
   formats. Never guess field names — follow the actual Directus schema.
2. Create (or update) the article record with the drafted content mapped to the correct fields.
3. **Status must always be `draft`.** For both new records and updates, never publish and never
   set `published`. Always save as a draft.

## C. Images — upload first, then reference by URL
1. Generate the images locally (banner + figures).
2. **Upload each image to Directus first** (Directus files). Never reference a local temp file
   or an un-uploaded path in the article.
3. Take the **Directus image URL** returned after upload and use that in the body / article data.
4. Placement rules:
   - If the body field is HTML / Markdown / rich text (can embed image URLs naturally), **embed
     the Directus URL in the body** at the right位置.
   - Use a dedicated image / eyecatch / thumbnail / main-image field **only if** that field truly
     exists in this data model and the schema makes its purpose clear. If no such field is
     confirmed, do not force images into a custom field — place the URL in the body instead.
   - If the body is managed as structured blocks / arrays and an image must go into a block's
     image field, follow that block definition. Do not guess field names, and do not dump
     body images into a main-image field.

## Guardrails
- Confirm schema → then write. Never assume field names or formats.
- 記事 model only for the duplicate check.
- Draft only. No publishing under any circumstance.

## D. Image upload — concrete implementation (Directus REST API + OS secret store)

The Directus MCP **cannot upload binary files** (its `files` tool only imports from a URL).
So upload image **binaries via the Directus REST API** (`POST /files`) with an access token, and
keep **article (`posts`) reads/updates on the Directus MCP** (the upload token often lacks `posts`
permission, and the MCP handles Japanese content reliably).

Division of labor:

- **Image binary → Directus REST API**: `POST {DIRECTUS_URL}/files` (multipart) with a Bearer token.
- **`posts` content → Directus MCP `items`**: create/update the article, embedding the asset URLs.

### Token: least privilege + OS secret store

Create a dedicated Directus user/role with only `directus_files` (create/read) and `posts`
(create/update), and issue a **static token**. Store it in the OS secret store; the script reads it
at run time and never prints it. Naming used by this plugin:

- **key / service**: `directus-contents-ops-api-token`
- **account / username**: `directus-contents-ops-api`

Per-OS storage and retrieval:

- **Windows — Credential Manager**. The `CredentialManager` PowerShell module requires **Windows
  PowerShell 5.1** (`powershell.exe`); it fails under PowerShell 7 (`System.Web` load error). From a
  PowerShell 7 / agent shell, either shell out to `powershell.exe`, or use a **DPAPI** file
  (`ConvertFrom-SecureString` / `ConvertTo-SecureString`), which works in both 5.1 and 7 on Windows.
- **macOS — Keychain** via `security` (`-s directus-contents-ops-api-token -a directus-contents-ops-api`).

### Upload, then reference by URL

```bash
TOKEN=...   # read from the OS secret store (do not print it)
ID=$(curl -s -H "Authorization: Bearer $TOKEN" -F "file=@/path/to/image.png" "$DIRECTUS_URL/files" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["id"])')
echo "$DIRECTUS_URL/assets/$ID"
```

- Embed `{DIRECTUS_URL}/assets/{id}` in the Markdown body (`content`) for in-body figures.
- Set the eyecatch by putting the returned file **UUID** into the article's `image` field
  (m2o to `directus_files`) — not a body figure.
- `status` stays **`draft`** for new records and updates alike.

> The agent shell in Cowork is PowerShell 7, so prefer the DPAPI file (or a `powershell.exe` shim)
> for token retrieval there. Article content updates go through the MCP `items` tool, not this token.
