# PC・スマホ 4OS実例ガイド（pc-4os-guide）

日常や仕事で行うデジタル作業 **17分類** をローテーションしながら、**Windows / macOS / iOS / Android** の4OSでの具体的な手順比較とトラブル解決法をローカルAIで執筆・挿絵生成し、公式ドキュメント参考文献付きでGitHubに書き溜めるプロジェクトです。

## システム構成

* **対象OS**: **Windows 11 / macOS / iOS（iPhone・iPad）/ Android**
* **文章生成（Ollama）**: `http://192.168.128.62:11434/`（`qwen3.5:9b` 構成・検証 × `gemma4:12b` 執筆）
* **挿絵生成（Draw Things）**: `http://192.168.128.59:7860/`（`FLUX.2 [klein] 4B`, `768x512` 内容忠実な日本語タイトル画像）
* **一次情報ソース検証**: Microsoft / Apple / Google 公式ドキュメントURLのHTTP実在チェック付き
* **記事ストック**: `content/YYYY-MM-DD_artXX_slug.md` + `.png`
* **Web公開（GitHub Pages）**: `docs/index.html` および `docs/articles/*.html`
* **はてなブログ1日1回自動メール投稿**: `.github/workflows/publish_hatena.yml`（毎朝 07:17 JST に未投稿1記事＋JPEGアイキャッチを送信、`data/posted_hatena.json` に記録）
* **Google Blogger 1日1回自動メール投稿**: `.github/workflows/publish_blogger.yml`（毎朝 07:37 JST に未投稿1記事＋JPEGアイキャッチを送信、`data/posted_blogger.json` に記録）

## 使い方

```powershell
# 状況確認
python -m src.main --status-report

# 17分類ローテーションで次の1記事＋挿絵を生成してGitHub Pagesを更新
python -m src.main -n 1

# 生成後にそのままGitHubへコミット＆プッシュ
python -m src.main -n 1 --push

# 特定の分類番号（例: 分類11 ネットワーク）を指定して生成
python -m src.main -n 1 --category 11
```

## 書き溜め済み記事一覧（全 32 本 / 最終更新: 2026-11-23 16:25 JST）

| No. | 17分類カテゴリ | 記事タイトル（Markdown） | 挿絵 | 生成日 |
| :---: | :--- | :--- | :---: | :---: |
| #32 | 分類15: エンターテインメント・趣味 | [動画・音楽のオフライン保存とダウンロードできない・容量圧迫の対策実例｜Windows・macOS・iOS・Android](content/2026-11-23_art32_offline_music_video_download.md) | あり | 2026-11-23 |
| #31 | 分類14: ハードウェア・周辺機器・IoT連携 | [外部モニター・サブディスプレイ接続の設定と映らない・解像度ズレ対処｜Windows・macOS・iOS・Android](content/2026-11-23_art31_dual_monitor_external_display.md) | あり | 2026-11-23 |
| #30 | 分類13: ファイル管理・バックアップ・データ復旧 | [ZIPファイルの圧縮・解凍と文字化け・開けない時の解決実例｜Windows・macOS・iOS・Android](content/2026-11-23_art30_zip_unzip_mojibake_password.md) | あり | 2026-11-23 |
| #29 | 分類12: セキュリティ・プライバシー対策 | [PC・スマホ紛失時の遠隔ロック・位置検索（探す機能）の設定実例｜Windows・macOS・iOS・Android](content/2026-11-23_art29_lost_device_find_lock_wipe.md) | あり | 2026-11-23 |
| #28 | 分類11: ネットワーク・サーバー・インフラ構築 | [Wi-Fiが遅い・突然切れる原因の切り分けと改善チェック実例｜Windows・macOS・iOS・Android](content/2026-11-23_art28_wifi_slow_disconnect_fix.md) | あり | 2026-11-23 |
| #27 | 分類10: システム管理・OS設定・メンテナンス | [OSアップデートが終わらない・失敗するときの安全な対処手順｜Windows・macOS・iOS・Android の比較ガイド](content/2026-11-23_art27_os_update_stuck_recovery.md) | あり | 2026-11-23 |
| #26 | 分類09: データ分析・科学計算・AI活用 | [生成AI（ChatGPT/Gemini）をPCとスマホで連携・履歴活用する実例｜Windows・macOS・iOS・Android](content/2026-11-23_art26_ai_chat_history_prompt_sync.md) | あり | 2026-11-23 |
| #25 | 分類08: Web制作・ブログ・デジタルマーケティング | [QRコード作成・読み取りとPC〜スマホ間のURL即時共有実例｜Windows・macOS・iOS・Android](content/2026-11-23_art25_qr_code_short_url_share.md) | あり | 2026-11-23 |
| #24 | 分類07: プログラミング・ソフトウェア開発 | [初心者向けMarkdownメモの書き方と全端末同期・プレビュー実例｜Windows・macOS・iOS・Android](content/2026-11-23_art24_markdown_editor_sync_beginners.md) | あり | 2026-11-23 |
| #23 | 分類06: 3D・CAD・ものづくり | [スマホの計測・3Dスキャンで家具サイズや間取りを確認・共有する実例｜Windows・macOS・iOS・Android](content/2026-11-23_art23_room_3d_scan_floorplan_measure.md) | あり | 2026-11-23 |
| #22 | 分類05: 動画・音声・音楽制作 | [ボイスメモ・会議録音の文字起こしと音声ファイル共有の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art22_voice_memo_transcription_sync.md) | あり | 2026-11-23 |
| #21 | 分類04: 画像・イラスト・デザイン制作 | [Instagram 投稿ワークフロー：PC デザインからスマホ投稿まで｜Windows・macOS・iOS・Android](content/2026-11-23_art21_social_media_schedule.md) | あり | 2026-11-23 |
| #20 | 分類03: 情報収集・リサーチ・Web 利用 | [クロスデバイス検索：ブラウザ間でのブックマークとメモ共有｜Windows・macOS・iOS・Android](content/2026-11-23_art20_news_verification_flow.md) | あり | 2026-11-23 |
| #19 | 分類02: コミュニケーション・情報共有 | [PC での PDF 注釈とスマホからの即時返答｜Windows・macOS・iOS・Android](content/2026-11-23_art19_meeting_notes_sync.md) | あり | 2026-11-23 |
| #18 | 分類01: 文書作成・オフィス業務・事務作業 | [複数 OS で同時編集：Google ドキュメント vs ローカルファイル｜Windows・macOS・iOS・Android](content/2026-11-23_art18_office_collab.md) | あり | 2026-11-23 |
| #17 | 分類17: 生活・行政手続き・家計・資産管理 | [領収書スキャン・確定申告データの整理と安全な保存手順｜Windows・macOS・iOS・Android](content/2026-11-23_art17_etax_receipt_scan_pdf_archive.md) | あり | 2026-11-23 |
| #16 | 分類16: 学習・教育・自己啓発 | [デジタル学習ノート・暗記カードの全端末同期とトラブル対策｜Windows・macOS・iOS・Android](content/2026-11-23_art16_digital_notes_sync_study.md) | あり | 2026-11-23 |
| #15 | 分類15: エンターテインメント・趣味 | [画面ミラーリング・テレビ投影の実例と映らない・音ズレ対処｜Windows・macOS・iOS・Android](content/2026-11-23_art15_screen_mirroring_casting.md) | あり | 2026-11-23 |
| #14 | 分類14: ハードウェア・周辺機器・IoT連携 | [Bluetooth機器のマルチペアリング設定と繋がらない時の解決法｜Windows・macOS・iOS・Android](content/2026-11-23_art14_bluetooth_multi_device_switch.md) | あり | 2026-11-23 |
| #13 | 分類13: ファイル管理・バックアップ・データ復旧 | [外付けSSDを4OSで共用するバックアップ手順と認識しない時の対処｜Windows・macOS・iOS・Android](content/2026-11-23_art13_external_ssd_photo_backup.md) | あり | 2026-11-23 |
| #12 | 分類12: セキュリティ・プライバシー対策 | [パスキー・パスワード管理＆2段階認証の安全な同期実例｜Windows・macOS・iOS・Android](content/2026-11-23_art12_passkey_password_security.md) | あり | 2026-11-23 |
| #11 | 分類11: ネットワーク・サーバー・インフラ構築 | [自宅LANの共有フォルダ・NAS（SMB）接続とエラー解決の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art11_lan_smb_file_sharing.md) | あり | 2026-11-23 |
| #10 | 分類10: システム管理・OS設定・メンテナンス | [ストレージ容量不足の原因特定と安全な空き容量確保の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art10_storage_cleanup_disk_usage.md) | あり | 2026-11-23 |
| #09 | 分類09: データ分析・科学計算・AI活用 | [CSV文字化け（UTF-8/Shift_JIS）の確実な直し方と実例｜Windows・macOS・iOS・Android](content/2026-11-23_art09_csv_encoding_mojibake_fix.md) | あり | 2026-11-23 |
| #08 | 分類08: Web制作・ブログ・デジタルマーケティング | [Webサイトの表示確認・スーパーリロード＆キャッシュ削除の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art08_blog_website_mobile_preview.md) | あり | 2026-11-23 |
| #07 | 分類07: プログラミング・ソフトウェア開発 | [初心者向けGitHub・コード閲覧とブラウザ開発環境の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art07_github_code_browser_mobile.md) | あり | 2026-11-23 |
| #06 | 分類06: 3D・CAD・ものづくり | [3Dデータ（STL/OBJ/AR）の閲覧・確認の実例ガイド｜Windows・macOS・iOS・Android](content/2026-11-23_art06_3d_ar_model_viewer.md) | あり | 2026-11-23 |
| #05 | 分類05: 動画・音声・音楽制作 | [動画の圧縮・トリミング・MP4共有の実例と再生エラー対処｜Windows・macOS・iOS・Android](content/2026-11-23_art05_video_compression_mp4.md) | あり | 2026-11-23 |
| #04 | 分類04: 画像・イラスト・デザイン制作 | [画像の一括リサイズ＆HEIC/WebP変換の実例ガイド｜Windows・macOS・iOS・Android](content/2026-11-23_art04_batch_image_resize_webp.md) | あり | 2026-11-23 |
| #03 | 分類03: 情報収集・リサーチ・Web利用 | [スクリーンショット・画面録画の最短手順と保存先トラブル対処｜Windows・macOS・iOS・Android](content/2026-11-23_art03_screenshot_screen_recording.md) | あり | 2026-11-23 |
| #02 | 分類02: コミュニケーション・情報共有 | [クラウドストレージ同期と共有トラブル解決の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art02_cross_os_cloud_sync_conflict.md) | あり | 2026-11-23 |
| #01 | 分類01: 文書作成・オフィス業務・事務作業 | [PDFの結合・分割・圧縮を無料で行う実例ガイド｜Windows・macOS・iOS・Android](content/2026-11-23_art01_pdf_merge_split_compress.md) | あり | 2026-11-23 |
