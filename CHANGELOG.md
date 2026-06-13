# CHANGELOG

## [Unreleased]

## [v0.4.3] - 2026-06-13

### Added
- テーブル上に全プレイヤー分のトランプ（ミニカード）を配る表示を追加（Heroは表向きの2枚、Villainは裏向きの2枚）
- クイズ開始時のアクションシーケンス演出アニメーションを追加（UTGから各席が時計回りにアクション（FOLD/OPEN/3BET）を巡ってHeroのアクション順番までトントンと遷移するアニメーション）
- テーブルをクリックすることでアクションアニメーションを即時スキップしてHeroの判断に移行する機能を追加
- アクションシーケンス中に「CLICK FELT TO SKIP」のヒントテキストを表示
- モバイル対応（極小画面においてミニカードやアクションバッジを綺麗に縮小表示するレスポンシブCSS）

### Changed
- FOLDアクションをより早く（220ms）、OPEN/3BETを少し長め（600ms）にしてリアルな卓のスピード感を表現

## [v0.4.2] - 2026-06-13

### Added
- 9-max preflop mode expansions: call/fold and 4bet/fold spots
- Range editor UI for per-spot token overrides during local tuning
- ポーカー用語集（Poker Glossary）機能の追加（スライドインパネルによる動的検索・アコーディオン展開）
- UI上の各種ポーカー用語（STACK, Positionなど）にクリック可能な用語集リンクを統合

### Changed
- Expanded 9-max trainer flow with open, 3bet, call, and 4bet spot coverage
- Kept versioning on patch bump only

## [v0.4.1] - 2026-06-13

### Changed
- 条例（`CLAUDE.md`）に、バージョン採番時にパッチバージョン（y）のみをインクリメントするルールを明記

## [v0.4.0] - 2026-06-13

### Added
- カード表面（表）の本格的なトランプレイアウト（`STANDARD`）を追加
  - 2〜10のカードに対するスートの正確なピップス配置の実装
  - 絵札（J/Q/K）に対する上下対称（ダブルヘッド）の肖像画イラストSVGの追加
  - スペードA（As）に対する豪華な装飾入りスペードロゴの追加
- UI上にカードレイアウトの切り替えトグル（`SIMPLE` / `STANDARD`）を追加
- 以前の「中央に巨大スートが1つ表示される簡易的なカード表示」も `SIMPLE` レイアウトとして選択できるように保持

## [v0.3.0] - 2026-06-13

### Added
- 新しいテーマスキン「ヴィンテージ・クラシック」（オフホワイトのカード、ボルドーのカードバック、アイボリーのテーブル）を `src/data/skins.json` に追加
- `src/lib/components/Card.svelte` のカードデザインをブラッシュアップ（ヴィンテージ感のある太枠、微細幾何学模様、中央の透かしスート記号を追加）
- 条例（`CLAUDE.md`）に、開発スピード向上のための自律動作ガイドラインを追記

## [v0.2.1] - 2026-06-13

### Added
- GitHub Pagesへの自動デプロイ用GitHub Actionsワークフロー（`.github/workflows/deploy.yml`）を追加
- `vite.config.ts` に GitHub Pages用の `base` パス設定を追加

## [v0.2.0] - 2026-06-13

### Added
- トランプスキン切り替え機能の土台となる `src/data/skins.json` を作成
- 3Dフリップとスート描画に対応した `src/lib/components/Card.svelte` コンポーネントを新規作成
- アニメーション付きカジノ風ダークテーマのCSSデザインを `src/app.css` に実装
- `src/App.svelte` でスキン（クラシック・ダーク、ネオン・サイバー、ロイヤル・ゴールド）の動的切り替えと、カード配布のアニメーション効果を実装

### Removed
- 未使用の `_materials/trump` フォルダを削除

## [v0.1.0] - 2026-06-13

### Added
- Svelte + TypeScript + Vite によるプリフロップトレーナーの初期構成
- 5bb〜20bbのヘッズアップSBプッシュレンジデータを `src/data/push_fold_hu.json` に配置
- ヨコサワレンジ表の解析データを `_materials` に配置
