#!/usr/bin/env python3
"""
Suica明細データからfreeeインポート用CSVを作成するスクリプト。

通常はdiff_entries.pyで差分抽出した結果を入力として使用する。
全件インポートの場合はSuica生データを直接入力することも可能。

使い方:
  python create_csv.py <input_file> <output_file> [--year YYYY]

入力ファイル形式（パイプ区切り）:
  MM/DD|種別1|場所1|種別2|場所2|差額

出力CSV形式（UTF-8 BOM）:
  日付,金額,内容
"""

import csv
import sys
import argparse
from datetime import datetime


def parse_amount(amount_str):
    """金額文字列をintに変換。カンマ・+・\\を除去。"""
    cleaned = amount_str.replace(',', '').replace('+', '').replace('\\', '').replace('¥', '').strip()
    if '▲' in cleaned:
        cleaned = '-' + cleaned.replace('▲', '')
    try:
        return int(cleaned)
    except (ValueError, TypeError):
        return 0


def build_description(type1, place1, type2, place2):
    """Suica種別から内容説明文を生成する。"""
    if type1 in ('入', '＊入'):
        return f"{place1}→{place2}"
    elif type1 == 'ｶｰﾄﾞ':
        return "Suicaチャージ"
    elif type1 == '物販':
        return "物販"
    elif type1 == '窓出':
        return f"{place1}→{place2}(窓口精算)"
    else:
        return f"{type1} {place1} {place2}".strip()


def detect_year(date_str, default_year=None):
    """MM/DD形式の日付から年を推定する。"""
    if default_year:
        return default_year
    return datetime.now().year


def main():
    parser = argparse.ArgumentParser(description='Suica明細→freee CSV変換')
    parser.add_argument('input_file', help='パイプ区切りのSuica明細ファイル（diff_entries.pyの出力推奨）')
    parser.add_argument('output_file', help='出力CSVファイルパス')
    parser.add_argument('--year', type=int, default=None,
                        help='日付の年（省略時は現在の年）')
    args = parser.parse_args()

    entries = []
    skipped = 0

    with open(args.input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('|')
            date_str = parts[0]
            type1 = parts[1] if len(parts) > 1 else ''
            place1 = parts[2] if len(parts) > 2 else ''
            type2 = parts[3] if len(parts) > 3 else ''
            place2 = parts[4] if len(parts) > 4 else ''
            amount_str = parts[5] if len(parts) > 5 else ''

            # 繰（繰越）は除外
            if type1 == '繰':
                skipped += 1
                continue

            # 年を付与
            month, day = date_str.split('/')
            year = detect_year(date_str, args.year)
            full_date = f"{year}/{int(month):02d}/{int(day):02d}"

            entries.append({
                'date': full_date,
                'amount': parse_amount(amount_str),
                'desc': build_description(type1, place1, type2, place2),
            })

    if not entries:
        print("差分なし。CSVの作成をスキップします。")
        sys.exit(0)

    # CSV出力（UTF-8 BOM、CRLF）
    with open(args.output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['日付', '金額', '内容'])
        for entry in entries:
            writer.writerow([entry['date'], entry['amount'], entry['desc']])

    # サマリー表示
    total = sum(e['amount'] for e in entries)
    charges = sum(e['amount'] for e in entries if e['amount'] > 0)
    expenses = sum(e['amount'] for e in entries if e['amount'] < 0)

    print(f"CSV作成完了: {args.output_file}")
    print(f"  件数: {len(entries)}件 (除外: {skipped}件)")
    if entries:
        dates = sorted(e['date'] for e in entries)
        print(f"  期間: {dates[0]} ～ {dates[-1]}")
    print(f"  チャージ合計: +{charges:,}円")
    print(f"  利用合計: {expenses:,}円")
    print(f"  差引: {total:,}円")


if __name__ == '__main__':
    main()
