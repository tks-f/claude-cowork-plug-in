#!/usr/bin/env python3
"""
Verify that the intended Japanese text actually appears in a generated image, using OCR.

Automated "hard" guard for in-image Japanese. After generating an image, OCR it (Tesseract,
Japanese) and check each expected string against the OCR output with a local-similarity metric.
If any expected string scores below the threshold, regenerate.

IMPORTANT: OCR is strong on large headline/banner text but can under-read small or decorated
labels (e.g. diagram captions among icons). Treat a PASS as high confidence and a FAIL as
"inspect closely and very likely regenerate". ALWAYS keep the human/visual check as the final
authority -- a pass here is necessary, not sufficient.

Usage:
  python verify_image_text.py --image banner.png \
      --expect "スポットCTOという選択肢" --expect "外部の技術責任者で意思決定を加速" \
      [--threshold 0.6] [--lang jpn] [--tessdata-dir DIR]

Output: JSON on stdout. Exit 0 if overall_pass else 1 (2 on setup error).
Requires: tesseract-ocr binary + <lang>.traineddata (jpn bundled in scripts/tessdata),
plus pip packages pytesseract + pillow.
"""
import argparse
import json
import os
import re
import sys
from difflib import SequenceMatcher


def normalize(s):
    return re.sub(r"[\s　、。.,:：・/／\-—|｜!！?？()（）\[\]【】「」『』]", "", s)


def best_local_ratio(expected, ocr):
    if not expected:
        return 1.0
    if not ocr:
        return 0.0
    n = len(expected)
    best = 0.0
    step = max(1, n // 4)
    for start in range(0, max(1, len(ocr) - n + 1), step):
        for wlen in (n, int(n * 1.3) + 1):
            r = SequenceMatcher(None, expected, ocr[start:start + wlen]).ratio()
            if r > best:
                best = r
            if best >= 0.999:
                return best
    if len(ocr) <= n * 2:
        best = max(best, SequenceMatcher(None, expected, ocr).ratio())
    return best


def is_subsequence(expected, ocr):
    it = iter(ocr)
    return all(ch in it for ch in expected)


def ocr_text(img, lang, base):
    import pytesseract
    g = img.convert("L")
    w, h = g.size
    if max(w, h) < 2400:
        g = g.resize((w * 2, h * 2))
    out = []
    for psm in ("6", "11", "3"):
        try:
            out.append(pytesseract.image_to_string(g, lang=lang, config=(base + " --psm " + psm).strip()))
        except Exception:
            pass
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--expect", action="append", default=[])
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--lang", default="jpn")
    ap.add_argument("--tessdata-dir", default=None)
    args = ap.parse_args()

    try:
        import pytesseract  # noqa: F401
        from PIL import Image
    except ImportError as e:
        print(json.dumps({"error": "missing dependency: " + str(e) + ". pip install pytesseract pillow"}))
        sys.exit(2)

    try:
        img = Image.open(args.image)
    except Exception as e:
        print(json.dumps({"error": "cannot open image: " + str(e)}))
        sys.exit(2)

    tess_dir = args.tessdata_dir
    if not tess_dir:
        here = os.path.dirname(os.path.abspath(__file__))
        cand = os.path.join(here, "tessdata")
        if os.path.exists(os.path.join(cand, args.lang + ".traineddata")):
            tess_dir = cand
    base = ('--tessdata-dir "' + tess_dir + '"') if tess_dir else ""

    try:
        raw = ocr_text(img, args.lang, base)
        if not raw.strip():
            raise RuntimeError("no text recognized")
    except Exception as e:
        print(json.dumps({"error": "OCR failed: " + str(e) + ". Need tesseract + " + args.lang + ".traineddata."}))
        sys.exit(2)

    ocr = normalize(raw)
    results = []
    overall = True
    for exp in args.expect:
        ne = normalize(exp)
        score = round(best_local_ratio(ne, ocr), 3)
        ok = score >= args.threshold
        overall = overall and ok
        results.append({"expected": exp, "score": score, "subsequence": is_subsequence(ne, ocr), "pass": ok})

    print(json.dumps({"overall_pass": overall, "lang": args.lang, "threshold": args.threshold,
                      "ocr_sample": raw.strip()[:200], "results": results}, ensure_ascii=False))
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
