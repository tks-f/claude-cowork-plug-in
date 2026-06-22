#!/usr/bin/env python3
"""Audit one article's SEO + AEO. Reads a JSON object (article fields) from --file or stdin and
prints a JSON report with seo_score / aeo_score and a prioritized issue list. Read-only; stdlib only.

Input JSON (all optional): title, slug, excerpt, content (markdown), tags (list),
image / has_image, status, date_published.
"""
import argparse
import json
import re
import sys


def jlen(s):
    return len(s or "")


def strip_md(md):
    s = md or ""
    s = re.sub(r"`{1,3}[^`]*`{1,3}", "", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"[#>*_|`-]", "", s)
    s = re.sub(r"\s+", "", s)
    return s


def chk(name, ok, sev, detail, suggestion):
    return {"name": name, "pass": bool(ok), "severity": sev, "detail": detail, "suggestion": suggestion}


def score(checks):
    w = {"high": 3, "med": 2, "low": 1}
    tot = sum(w[c["severity"]] for c in checks)
    got = sum(w[c["severity"]] for c in checks if c["pass"])
    return round(100 * got / tot) if tot else 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file")
    args = ap.parse_args()
    raw = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    a = json.loads(raw)

    title = a.get("title") or ""
    slug = a.get("slug") or ""
    meta = a.get("excerpt") or ""
    content = a.get("content") or ""
    tags = a.get("tags") or []
    has_image = bool(a.get("image")) or bool(a.get("has_image"))

    headings = [h[1].strip() for h in re.findall(r"(?m)^(#{2,3})\s+(.+)$", content)]
    body_chars = len(strip_md(content))
    links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", content)
    imgs = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", content)
    img_no_alt = sum(1 for alt, _ in imgs if not alt.strip())
    bullets = len(re.findall(r"(?m)^\s*[-*]\s+\S", content))
    numbered = len(re.findall(r"(?m)^\s*\d+\.\s+\S", content))
    tables = len(re.findall(r"(?m)^\s*\|.*\|\s*$", content))
    q_headings = [t for t in headings if ("？" in t or "?" in t or "とは" in t or re.search(r"か[\?？]?$", t))]
    faq = bool(re.search(r"よくある質問|FAQ|Q&A|Q[\.:：]", content))
    primary = tags[0] if tags else ""
    kw_in_title = bool(primary) and primary in title
    kw_in_intro = bool(primary) and primary in strip_md(content[:300])

    seo = [
        chk("title_present", bool(title), "high", "len=%d" % jlen(title), "タイトルを設定"),
        chk("title_length", 20 <= jlen(title) <= 40, "med", "%d字 (推奨~28-35)" % jlen(title), "全角28〜35字目安に"),
        chk("meta_present", bool(meta), "high", "len=%d" % jlen(meta), "メタ(excerpt)を設定"),
        chk("meta_length", 70 <= jlen(meta) <= 130, "med", "%d字 (推奨~80-120)" % jlen(meta), "80〜120字目安に"),
        chk("slug_ascii", bool(re.fullmatch(r"[a-z0-9-]+", slug or "")), "med", slug, "英数字+ハイフンのスラッグに"),
        chk("has_headings", len(headings) >= 2, "high", "H2/H3=%d" % len(headings), "見出し(##)で構造化"),
        chk("tags_present", len(tags) > 0, "med", "%d tags" % len(tags), "主要KWをタグに"),
        chk("keyword_in_title", kw_in_title, "med", "primary=%s" % primary, "主要KWをタイトルに"),
        chk("keyword_in_intro", kw_in_intro, "low", "", "冒頭に主要KWを自然に"),
        chk("content_length", body_chars >= 800, "med", "%d字" % body_chars, "本文を厚く(800字以上)"),
        chk("has_links", len(links) >= 1, "low", "%d links" % len(links), "関連記事/出典リンクを追加"),
        chk("eyecatch_set", has_image, "med", str(has_image), "アイキャッチ画像を設定"),
        chk("img_alt", img_no_alt == 0, "low", "%d without alt" % img_no_alt, "本文画像にalt付与"),
    ]
    aeo = [
        chk("question_headings", len(q_headings) >= 1, "med", "%d 質問形見出し" % len(q_headings), "見出しを質問形に(〜とは/〜は？)"),
        chk("faq_section", faq, "high", str(faq), "FAQ(よくある質問)を追加"),
        chk("extractable_structure", (bullets + numbered + tables) >= 2, "med",
            "bul=%d num=%d tbl=%d" % (bullets, numbered, tables), "箇条書き・表で要点を構造化"),
        chk("definition_early", "とは" in strip_md(content[:200]), "low", "", "冒頭で主要用語を定義"),
    ]

    sev = {"high": 0, "med": 1, "low": 2}
    issues = [dict(area=area, **c) for area, cs in (("SEO", seo), ("AEO", aeo)) for c in cs if not c["pass"]]
    issues.sort(key=lambda c: sev[c["severity"]])

    print(json.dumps({
        "title": title, "status": a.get("status"),
        "seo_score": score(seo), "aeo_score": score(aeo),
        "metrics": {"title_len": jlen(title), "meta_len": jlen(meta), "headings": len(headings),
                    "body_chars": body_chars, "links": len(links), "bullets": bullets, "tables": tables,
                    "q_headings": len(q_headings), "faq": faq, "eyecatch": has_image},
        "seo_checks": seo, "aeo_checks": aeo, "top_issues": issues[:8],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
