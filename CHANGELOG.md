# CHANGELOG

## [Unreleased]

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
