# Deck Analyzer Wiki

このWikiでは、Yu-Gi-Oh! デッキ管理アプリケーション **Deck Analyzer** の基本的な使い方やセットアップ方法をまとめます。

## 1. プロジェクト概要

Deck Analyzer は Kivy と KivyMD を用いたデッキ管理・カード分析アプリです。デッキ作成やカード一覧の編集に加え、CSV からのデッキインポートやモンテカルロシミュレーション、カード情報取得などの機能を提供します。

## 2. セットアップ

必要な依存パッケージは `README.md` に記載されています。Python 3.8 以上が必要です。依存関係のインストール例:

```bash
pip install kivy kivymd pillow beautifulsoup4 selenium matplotlib
```

`external_resource` ディレクトリを作成し、SQLite データベース (`db/ygo_data.db`) を配置してください。初回起動時には `external_resource/config/config.json` が自動生成され、アニメーション速度や表示枚数、テーマカラー・スタイルを編集できます。カード画像取得には `external_resource/chromedriver-win32/chromedriver.exe` を設置し、Selenium が参照できるようにします。フォントは既定で Windows の `msgothic.ttc` が使用されますが、設定画面からカスタムフォントをアップロードし `resource/theme/font` に保存したファイルを指定することも可能です。

## 3. アプリの起動

メイン画面は `main.py` から起動します:

```bash
python3 main.py
```

起動後、カード情報取得やデッキ管理、戦績登録、統計表示などのメニューが表示されます。デッキデータは `external_resource/db/ygo_data.db` に保存されます。

## 4. 付属ツール

 - `function/core/card_img_download.py` : Selenium を使ったカード画像収集ツール
 - `data/archive/MontecarloSimulator.py` : デッキのカード貢献度を評価するモンテカルロシミュレータ

これらのツールの詳細はリポジトリの `README.md` を参照してください。

## 5. リンク

- [GitHub リポジトリ](../)
- [README](../README.md)

以上が Deck Analyzer の概要です。詳しい使い方や追加情報は、Wiki 内の各ページで紹介していきます。
