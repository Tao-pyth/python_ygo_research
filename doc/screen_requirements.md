# 画面構成および画面遷移に関する要件定義書

## 1. 画面一覧と機能概要

| 画面ID | 画面名 | 主な機能 |
| ------ | ------ | -------- |
| `MenuScreen` | メインメニュー | 各画面への入口。アプリ終了ボタンを含む |
| `CardInfoScreen` | カード情報取得 | カード名またはデッキURLからカード画像・テキストを取得 |
| `DeckManagerScreen` | デッキ管理 | デッキ作成・削除・CSVインポート・カード一覧表示 |
| `CardListScreen` | カード一覧 | 選択したデッキのカードや全カードを表示・枚数変更 |
| `CardDetailScreen` | カード詳細 | 画像・テキスト表示とスコア入力、効果編集画面へ遷移 |
| `CardEffectEditScreen` | カード効果編集 | 効果YAMLの読込・保存・インポート・エクスポート |
| `ConfigScreen` | 設定 | アプリ設定変更、フォントアップロード |
| `MatchRegisterScreen` | 試合データ登録 | 試合結果を登録（未実装） |
| `StatsScreen` | 統計表示 | 統計情報を表示（未実装） |

## 2. 各画面の要素構成

### メインメニュー（MenuScreen）
- タイトルラベル
- 「カード情報取得」「デッキ管理」「試合データ登録」「統計表示」「設定」ボタン
- アプリ終了ボタン

### カード情報取得（CardInfoScreen）
- タイトルラベル
- 「カード名を入力」「デッキURLを入力」の2タブ
  - カード名入力欄 / デッキURL入力欄
  - カード取得をデッキ登録するチェックボックスとデッキ名入力
- 状態表示ラベル、直近保存カードラベル、画像表示エリア
- 「戻る」「取得する」ボタン

### デッキ管理（DeckManagerScreen）
- 新規デッキ名入力欄と「デッキを作成」ボタン
- デッキ一覧（選択ボタン、インポートアイコン、削除アイコン）
- CSVインポート用パス入力欄と「CSVからインポート」ボタン
- 下部に「戻る」「全てのカードを見る」ボタン

### カード一覧（CardListScreen）
- タイトルラベル（デッキ名または「全カード一覧」）
- スクロール可能なカードリスト（タップで詳細表示）
- 新規カード追加用のカード名・枚数入力欄と「追加」ボタン
- 「戻る」ボタン

### カード詳細（CardDetailScreen）
- カード名ラベル
- カード画像
- 説明テキストおよび追加情報表示
- スコア入力欄（フィールド/手札/墓地）
- デッキ使用状況表示（チップ形式）
- 「戻る」「カード効果を設定する」「保存」ボタン

### カード効果編集（CardEffectEditScreen）
- YAMLテキスト入力欄
- ファイルパス入力欄
- 「読込」「保存」「インポート」「エクスポート」「戻る」ボタン

### 設定（ConfigScreen）
- アニメーション速度、最大表示カード数、フォントサイズ入力欄
- カスタムフォント切替、フォントアップロードボタン
- テーマ色選択、スタイル切替
- 「保存」「リセット」「戻る」ボタン

### 試合データ登録（MatchRegisterScreen）
- タイトルラベル
- 使用デッキ選択ドロップダウン
- 対戦相手デッキタグ選択・追加
- 勝敗チェックボックス
- 備考入力欄
- 「登録」「戻る」ボタン

### 統計表示（StatsScreen）
- タイトルラベル
- 「戻る」ボタン

## 3. 画面遷移図

```
[Menu]
  |-- カード情報取得 ------> [CardInfo]
  |-- デッキ管理 ----------> [DeckManager]
  |-- 試合データ登録 ------> [MatchRegister]
  |-- 統計表示 ------------> [Stats]
  |-- 設定 ----------------> [Config]

[DeckManager] -- デッキ選択 --> [CardList]
[CardList] ---- カードタップ --> [CardDetail]
[CardDetail] -- 効果編集 ----> [EffectEdit]
```
各画面には対応する「戻る」ボタンがあり、前の画面またはメインメニューへ戻る。

## 4. 遷移条件と補足説明
- すべての画面は **KivyMD** を用いた `MDScreenManager` 上で実装される。
- 各ボタンの `on_release` により `manager.current` を変更して遷移する。
- 戻るボタンの遷移先は以下のとおり:
  - CardInfoScreen, DeckManagerScreen, MatchRegisterScreen, StatsScreen, ConfigScreen は `MenuScreen` へ戻る。
  - CardListScreen は `DeckManagerScreen` へ戻る。
  - CardDetailScreen は `CardListScreen` へ戻る。
  - CardEffectEditScreen は `CardDetailScreen` へ戻る。
- DeckManagerScreen でデッキを選択すると CardListScreen でそのデッキ内容を閲覧・編集できる。
- CardInfoScreen で取得したカード画像やテキストはローカルに保存され、CardDetailScreen で利用される。
