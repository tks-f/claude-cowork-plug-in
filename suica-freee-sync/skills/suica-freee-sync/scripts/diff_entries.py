#!/usr/bin/env python3
"""
Suica明細とfreee明細の差分を明細レベルで照合するスクリプト。

使い方:
  python diff_entries.py <suica_file> <freee_file> [--year YYYY] [--fuzzy] [--output <diff_file>]

Suicaファイル形式（パイプ区切り）:
  MM/DD|種別1|場所1|種別2|場所2|差額

freeeファイル形式（パイプ区切り）:
  YYYY-MM-DD|金額|内容

--fuzzy: 内容を無視して日付+金額のみで照合する（API同期とCSV取込で内容形式が異なる場合）
--output: 差分明細をパイプ区切りファイルに出力する（create_csv.pyの入力用）
"""

import sys
import argparse
from collections import Counter
from datetime import datetime


def parse_amount(amount_str):
    """金額文字列をintに変換。カンマ・+・\\を除去。"""
    cleaned = amount_str.replace(',', '').replace('+', '').replace('\\', '').replace('¥', '').strip()
    # Handle negative with ▲ prefix
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


def load_suica(filepath, year=None):
    """Suicaパイプ区切りファイルを読み込み、明細リストを返す。"""
    entries = []
    if year is None:
        year = datetime.now().year

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            type1 = parts[1] if len(parts) > 1 else ''

            # 繰（繰越）は除外
            if type1 == '繰':
                continue

            date_str = parts[0]
            month, day = date_str.split('/')
            place1 = parts[2] if len(parts) > 2 else ''
            type2 = parts[3] if len(parts) > 3 else ''
            place2 = parts[4] if len(parts) > 4 else ''
            amount_str = parts[5] if len(parts) > 5 else ''

            full_date = f"{year}/{int(month):02d}/{int(day):02d}"
            desc = build_description(type1, place1, type2, place2)
            amount = parse_amount(amount_str)

            entries.append({
                'date': full_date,
                'amount': amount,
                'desc': desc,
                'raw': line,
            })

    return entries


def load_freee(filepath):
    """freeeパイプ区切りファイルを読み込み、明細リストを返す。"""
    entries = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            date_str = parts[0]
            amount_str = parts[1] if len(parts) > 1 else ''
            desc = parts[2] if len(parts) > 2 else ''

            # 日付正規化: YYYY-MM-DD → YYYY/MM/DD
            date_normalized = date_str.replace('-', '/')
            amount = parse_amount(amount_str)

            entries.append({
                'date': date_normalized,
                'amount': amount,
                'desc': desc.strip(),
            })

    return entries


def compute_diff(suica_entries, freee_entries, fuzzy=False):
    """
    Suica明細とfreee明細の差分を計算する。
    カウントベースの照合により、同一日・同一金額の重複にも対応。

    Returns: freeeに存在しないSuica明細のリスト
    """
    if fuzzy:
        # 日付+金額のみで照合
        freee_counter = Counter((e['date'], e['amount']) for e in freee_entries)
        missing = []
        suica_counter = Counter()
        for entry in suica_entries:
            key = (entry['date'], entry['amount'])
            suica_counter[key] += 1
            # Suica側のこのキーの累計出現数がfreee側を超えたら差分
            if suica_counter[key] > freee_counter.get(key, 0):
                missing.append(entry)
    else:
        # 日付+金額+内容で照合
        freee_counter = Counter((e['date'], e['amount'], e['desc']) for e in freee_entries)
        missing = []
        suica_counter = Counter()
        for entry in suica_entries:
            key = (entry['date'], entry['amount'], entry['desc'])
            suica_counter[key] += 1
            if suica_counter[key] > freee_counter.get(key, 0):
                missing.append(entry)

    return missing


def detect_lost_period(suica_entries, freee_entries):
    """
    freee明細の最終日とSuica取得可能最古日を比較し、
    永久消失期間を検出する。
    """
    if not suica_entries or not freee_entries:
        return None

    freee_dates = sorted(set(e['date'] for e in freee_entries))
    suica_dates = sorted(set(e['date'] for e in suica_entries))

    if not freee_dates or not suica_dates:
        return None

    freee_latest = freee_dates[-1]
    suica_oldest = suica_dates[0]

    if suica_oldest > freee_latest:
        return {
            'start': freee_latest,
            'end': suica_oldest,
            'note': 'freee最終日の翌日からSuica最古日の前日まで、26週間制限で取得不可'
        }

    return None


def main():
    parser = argparse.ArgumentParser(description='Suica ↔ freee 明細レベル差分照合')
    parser.add_argument('suica_file', help='Suica明細ファイル（パイプ区切り）')
    parser.add_argument('freee_file', help='freee明細ファイル（パイプ区切り）')
    parser.add_argument('--year', type=int, default=None, help='Suicaデータの年（省略時は今年）')
    parser.add_argument('--fuzzy', action='store_true',
                        help='内容を無視して日付+金額のみで照合する')
    parser.add_argument('--output', '-o', help='差分明細の出力ファイル（パイプ区切り）')
    args = parser.parse_args()

    # データ読み込み
    suica_entries = load_suica(args.suica_file, args.year)
    freee_entries = load_freee(args.freee_file)

    print(f"=== データ読み込み ===")
    print(f"Suica明細: {len(suica_entries)}件")
    if suica_entries:
        dates = sorted(e['date'] for e in suica_entries)
        print(f"  期間: {dates[0]} ～ {dates[-1]}")
    print(f"freee明細: {len(freee_entries)}件")
    if freee_entries:
        dates = sorted(e['date'] for e in freee_entries)
        print(f"  期間: {dates[0]} ～ {dates[-1]}")

    # 差分計算
    mode = "曖昧照合（日付+金額）" if args.fuzzy else "厳密照合（日付+金額+内容）"
    print(f"\n=== 差分照合 ({mode}) ===")

    missing = compute_diff(suica_entries, freee_entries, fuzzy=args.fuzzy)
    print(f"freeeにない明細: {len(missing)}件")

    if missing:
        dates = sorted(e['date'] for e in missing)
        print(f"期間: {dates[0]} ～ {dates[-1]}")

        # 月別集計
        months = {}
        for entry in missing:
            month_key = entry['date'][:7]  # YYYY/MM
            if month_key not in months:
                months[month_key] = {'count': 0, 'total': 0}
            months[month_key]['count'] += 1
            months[month_key]['total'] += entry['amount']

        print(f"\n=== 月別集計 ===")
        for m in sorted(months.keys()):
            print(f"  {m}: {months[m]['count']}件, {months[m]['total']:+,}円")

        total = sum(e['amount'] for e in missing)
        charges = sum(e['amount'] for e in missing if e['amount'] > 0)
        expenses = sum(e['amount'] for e in missing if e['amount'] < 0)
        print(f"\n=== 合計 ===")
        print(f"チャージ: +{charges:,}円")
        print(f"利用額: {expenses:,}円")
        print(f"差引: {total:,}円")

        # 明細リスト
        print(f"\n=== 差分明細リスト ===")
        for i, entry in enumerate(missing):
            print(f"{i+1:3d}. {entry['date']} | {entry['desc']:20s} | {entry['amount']:+,}円")

        # 差分ファイル出力
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                for entry in missing:
                    f.write(entry['raw'] + '\n')
            print(f"\n差分ファイル出力: {args.output} ({len(missing)}件)")
    else:
        print("差分なし。freeeはSuicaと同期済みです。")

    # 永久消失期間の検出
    lost = detect_lost_period(suica_entries, freee_entries)
    if lost:
        print(f"\n=== 注意: 永久消失期間 ===")
        print(f"{lost['start']} ～ {lost['end']} の間")
        print(f"{lost['note']}")

    # 終了コード: 差分があれば1、なければ0
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
