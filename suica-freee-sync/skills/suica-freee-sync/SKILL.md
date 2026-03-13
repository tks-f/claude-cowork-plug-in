---
name: suica-freee-sync
description: |
  モバイルSuicaの利用履歴をfreee会計に同期するスキル。
  Suicaサイトからブラウザ操作で取引明細を取得し、freeeに存在しない明細を
  特定してCSVインポートする。freee APIの自動同期が止まった場合の手動リカバリに対応。

  このスキルは以下のようなリクエストで使う：
  「Suicaの明細をfreeeに同期して」「Suicaとfreeeの差分を確認して」
  「freeeにSuicaの明細をインポートして」「交通費をfreeeに入れて」
  「Suicaの取引をfreeeに取り込んで」「freeeのSuica同期を修復して」
  Suica・freee・交通費・交通系ICに関する同期やインポートの話題が出たら
  積極的にこのスキルを使うこと。
  ブラウザ自動操作（Claude in Chrome）が必要。
compatibility: "Claude in Chrome (browser automation), Bash, Python 3"
---

# Suica → freee 同期スキル

モバイルSuicaの利用履歴をfreee会計に同期するワークフロー。
freee APIの自動同期が停止した場合に、Suicaサイトからの手動データ取得→CSV作成→freeeインポートで補完する。

## 全体フロー

```
1. freeeのモバイルSuica口座から全明細を抽出（日付・金額・内容）
2. Suicaサイトにログイン（ユーザー操作）
3. 対象カードを選択し履歴を取得
4. 明細レベルで差分を照合（日付+金額+内容で突合）
5. freeeに存在しない明細のみCSVを作成
6. 差分CSVのみをfreeeにアップロード
7. アップロード後に再照合して差分ゼロを検証
```

**原則: 差分のみ同期する。** freee側の既存明細と1件ずつ突合し、freeeに存在しない
Suica明細だけをCSVにまとめてインポートする。全件上書きはしない。

## 重要な制約事項

### Suicaサイトの制約
- **履歴上限**: 1回の検索で最大100件（+繰越1件 = 101行）
- **保存期間**: 過去26週間（約6ヶ月）のみ。それ以前のデータは完全消失する
- **ログイン**: パスワード入力はユーザーが行う。ログインページが表示されたら必ずユーザーに操作を促す
- **セッション**: 長時間操作しないとタイムアウトする（約20分）。タイムアウトしたら再ログインを依頼

### freeeの制約
- **CSV形式**: UTF-8 BOM (`utf-8-sig`) 必須。ヘッダーは `日付,金額,内容`
- **重複チェック**: freeeが自動で重複判定するが、Suicaは同一日・同一金額の明細が多く完全ではない
- **口座指定**: アップロード先のモバイルSuica口座を正しく選択する

## Step 1: freee側の全明細を抽出

freeeの明細一覧ページで、モバイルSuica口座の **全明細** を日付・金額・内容つきで抽出する。
この情報がStep 3の差分照合に必要。

```
URL: https://secure.freee.co.jp/wallet_txns
```

確認項目：
- 口座フィルタを「モバイルSuica」に設定
- 表示件数を最大にする（100件/ページ推奨）
- ページネーションがある場合は全ページ分を取得する

### freee明細データのJavaScript抽出

**重要**: 差分照合のため、日付・金額・内容の3項目を抽出する。

```javascript
const rows = document.querySelectorAll('table tbody tr');
const data = [];
rows.forEach(r => {
  const cells = r.querySelectorAll('td');
  if (cells.length >= 5) {
    const date = cells[2]?.textContent.trim();
    const desc = cells[3]?.textContent.trim();
    const amount = cells[4]?.textContent.trim().replace(/,/g, '');
    data.push(date + '|' + amount + '|' + desc);
  }
});
data.join('\n');
```

出力形式: `YYYY-MM-DD|金額|内容`

ページネーションがある場合は各ページで上記を実行し、結果を連結する。
抽出したデータはファイルに保存しておく（例: `freee_all.txt`）。

## Step 2: Suicaサイトでの明細取得

### ログインとカード選択

```
URL: https://www.mobilesuica.com/
```

1. ログインページが表示されたらユーザーにログインを依頼する（パスワード入力禁止）
2. 会員メニューから対象のSuicaカードを選択（複数カードある場合あり）
3. 「SF（電子マネー）利用履歴」をクリック

### 日付フィルタの操作

履歴画面には日付フィルタのドロップダウンがある。`find` ツールで年月と日のセレクタを見つけ、値をセットする。「〇〇以前」の検索で、指定日以前の最大100件が表示される。

### Suica履歴テーブルのJavaScript抽出

Suicaの履歴テーブルは `document.querySelectorAll('table')` のインデックス2（3番目のtable）にある場合が多い。テーブル構造が変わっていた場合は各テーブルの `rows.length` と `rows[0].cells.length` で正しいものを特定する。

```javascript
const table = document.querySelectorAll('table')[2];
const rows = table.querySelectorAll('tr');
const data = [];
for (let i = 1; i < rows.length; i++) {
  const cells = rows[i].querySelectorAll('td');
  if (cells.length >= 7) {
    const date = cells[0]?.textContent.trim();
    const type1 = cells[1]?.textContent.trim();
    const place1 = cells[2]?.textContent.trim();
    const type2 = cells[3]?.textContent.trim();
    const place2 = cells[4]?.textContent.trim();
    const amount = cells[6]?.textContent.trim();
    data.push([date, type1, place1, type2, place2, amount].join('|'));
  }
}
data.join('\n');
```

**出力の切り詰め対策**: 100件超のデータは1回で全て取得できないことがある。`data.slice(0,50).join('\n')` と `data.slice(50).join('\n')` のように分割取得する。

### Suicaデータの形式

```
MM/DD|種別1|場所1|種別2|場所2|差額
```

| 種別 | 意味 | CSVの内容欄に変換 |
|------|------|-----------------|
| `入` / `＊入` | 乗車→降車 | `{場所1}→{場所2}` |
| `ｶｰﾄﾞ` | チャージ | `Suicaチャージ` |
| `物販` | 物品購入 | `物販` |
| `窓出` | 窓口精算 | `{場所1}→{場所2}(窓口精算)` |
| `繰` | 繰越 | **除外する** |

## Step 3: 明細レベル差分照合

Suicaから取得した明細とfreeeの全明細を **1件ずつ突合** し、freeeに存在しないものだけを抽出する。
`scripts/diff_entries.py` を使用して差分分析を行う。

### 照合キー

各明細を `(日付, 金額, 内容)` のタプルで比較する。

- **日付**: Suicaは `MM/DD` → `YYYY/MM/DD` に変換。freeeは `YYYY-MM-DD` → `YYYY/MM/DD` に正規化
- **金額**: 整数に統一（カンマ・符号記号を除去）
- **内容**: Suicaの種別を変換後の文字列（例: `品川→東京`）とfreee側の摘要を比較

### 同一日・同一金額の重複への対処

Suicaでは同日に同一金額の明細が複数存在することがある（例: 同じ区間の往復）。
この場合、単純なセット比較では正しく突合できない。

**対処方法**: カウントベースの照合を行う。

```
1. Suica側: (日付, 金額, 内容) のタプルごとに出現回数を数える
2. freee側: (日付, 金額, 内容) のタプルごとに出現回数を数える
3. Suica出現回数 > freee出現回数 のタプルが差分
4. 差分 = Suica出現回数 - freee出現回数 の件数分をCSVに含める
```

### 内容の曖昧マッチ

freeeにインポート済みの明細は、内容文字列が完全一致しない場合がある
（API同期分とCSV取込分で形式が異なる可能性）。

その場合は `(日付, 金額)` のみで照合し、内容は参考情報として扱う。
`--fuzzy` フラグで切り替え可能にする。

### 永久消失期間の検出

freee明細の最終日とSuica取得可能な最古日を比較し、
回収不能な期間がある場合はユーザーに報告する。

- **永久消失期間** = freee最終日の翌日 ～ Suica取得最古日の前日
- Suicaの26週間制限により、この期間のデータは完全に失われている

ユーザーには永久消失期間の有無・範囲を必ず明確に報告すること。

## Step 4: 差分CSVの作成

差分照合で特定された **freeeに存在しない明細のみ** でCSVを作成する。
`scripts/create_csv.py` を使用する。

### CSV仕様

| 項目 | 値 |
|------|-----|
| エンコーディング | UTF-8 BOM (`utf-8-sig`) |
| ヘッダー | `日付,金額,内容` |
| 日付形式 | `YYYY/MM/DD` |
| 金額 | 整数（マイナス=支出、プラス=チャージ） |
| 改行コード | CRLF (`\r\n`) |

金額のクリーニング: `,` `+` `\` を除去して `int()` に変換。
`繰` 行は必ず除外する。差分0件の場合はCSV作成をスキップして完了報告する。

## Step 5: freeeへCSVアップロード

### アップロードページへの遷移

直接URLでは到達できないことが多い。以下の手順で遷移する：

```
1. https://secure.freee.co.jp/walletables （口座の一覧）
2. 対象のモバイルSuica口座をクリック
3. 「明細アップロード」ボタンをクリック
```

### DataTransfer APIによるファイルアップロード

freeeのファイル選択はhidden input[type="file"]で、通常クリックでは操作しにくい。
CSVをBase64エンコードし、JavaScriptのDataTransfer APIでセットする。

```bash
# Bashでbase64エンコード
base64 -w 0 /path/to/suica_import.csv
```

```javascript
const base64Data = "<base64文字列>";
const byteCharacters = atob(base64Data);
const byteNumbers = new Array(byteCharacters.length);
for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
}
const byteArray = new Uint8Array(byteNumbers);
const blob = new Blob([byteArray], { type: 'text/csv' });
const file = new File([blob], 'suica_import.csv', { type: 'text/csv' });

const fileInput = document.querySelector('input[type="file"]');
const dataTransfer = new DataTransfer();
dataTransfer.items.add(file);
fileInput.files = dataTransfer.files;
fileInput.dispatchEvent(new Event('change', { bubbles: true }));
```

### アップロード後の操作

1. 2回目以降: 「ご自身で作成したCSV（前回と同じフォーマット）」を選択
2. 初回: 「ご自身で作成したCSV（新規のフォーマット）」を選択し、カラムマッピング:
   - 1列目 → 取引日
   - 2列目 → 取引金額
   - 3列目 → 利用内容・摘要
3. 「アップロードを開始」をクリック

## Step 6: 検証（再照合）と報告

インポート完了後、freee明細一覧を **再度取得** し、差分がゼロになったことを検証する。

### 再照合の手順

```
1. freee明細一覧を再度開き、Step 1と同じJavaScriptで全明細を再抽出
2. Suicaデータと再度diff_entries.pyで差分照合
3. 差分が0件であることを確認
4. 差分が残っている場合は原因を調査（重複判定の問題等）
```

### 報告すべき内容

- インポート成功件数（差分CSVの件数と一致するか）
- インポートした日付範囲
- チャージ合計・利用合計・差引
- 月別集計
- 再照合結果（差分ゼロかどうか）
- 永久消失期間の有無と範囲（回収不能データがある場合）

## トラブルシューティング

### 100件を超える差分
Suicaは1検索で最大100件。日付フィルタを調整して複数回に分けて取得する。例: 12/11以前で100件取得 → 最古の日付を確認 → その日付以前でさらに100件。

### freeeアップロードページに直接遷移できない
URLを直打ちせず、口座一覧→口座詳細→明細アップロードの順で遷移する。

### Suicaセッションタイムアウト
長い分析作業の前にSuicaデータをローカルファイルに保存しておく。freee作業中にSuicaに戻る必要がなくなる。

### テーブルインデックスのズレ
各テーブルの行数・列数をログ出力して正しいテーブルを特定する：
```javascript
document.querySelectorAll('table').forEach((t, i) =>
  console.log(i, t.rows.length, t.rows[0]?.cells.length));
```
