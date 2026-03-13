---
description: Suica明細をfreeeに差分同期する
allowed-tools: Read, Write, Bash, Grep, Glob, Task, WebFetch
---

モバイルSuicaの利用履歴をfreee会計に差分同期する。

まず `${CLAUDE_PLUGIN_ROOT}/skills/suica-freee-sync/SKILL.md` を読み込み、記載されたワークフローに従って実行する。

処理の流れ:
1. freeeのモバイルSuica口座から全明細を抽出（日付・金額・内容）
2. ユーザーにSuicaサイトへのログインを依頼
3. Suica利用履歴を取得
4. 明細レベルで差分を照合（日付+金額+内容で突合）
5. freeeに存在しない明細のみCSVを作成
6. 差分CSVをfreeeにアップロード
7. アップロード後に再照合して差分ゼロを検証

差分が0件の場合は「同期済みです」と報告して終了する。

$ARGUMENTS が指定された場合、それを追加の指示として考慮する（例: 特定の期間のみ、fuzzyモード等）。
