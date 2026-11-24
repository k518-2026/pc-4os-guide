# PC・スマホ 4OS実例ガイド（pc-4os-guide）

日常や仕事で行うデジタル作業 **17分類** をローテーションしながら、**Windows / macOS / iOS / Android** の4OSでの具体的な手順比較とトラブル解決法をローカルAIで執筆・挿絵生成し、公式ドキュメント参考文献付きでGitHubに書き溜めるプロジェクトです。

## システム構成

* **対象OS**: **Windows 11 / macOS / iOS（iPhone・iPad）/ Android**
* **文章生成（Ollama）**: `http://192.168.128.62:11434/`（`qwen3.5:9b` 構成・検証 × `gemma4:12b` 執筆）
* **挿絵生成（Draw Things）**: `http://192.168.128.59:7860/`（`FLUX.2 [klein] 4B`, `768x512` 内容忠実な日本語タイトル画像）
* **一次情報ソース検証**: Microsoft / Apple / Google 公式ドキュメントURLのHTTP実在チェック付き
* **記事ストック**: `content/YYYY-MM-DD_artXX_slug.md` + `.png`
* **Web公開（GitHub Pages）**: `docs/index.html` および `docs/articles/*.html`
* **はてなブログ自動メール投稿（16時間ごと）**: `.github/workflows/publish_hatena.yml`（4時間おきに起動し前回投稿から16時間経過していれば未投稿1記事＋JPEGアイキャッチを送信、`data/posted_hatena.json` に記録）
* **Google Blogger 自動メール投稿（16時間ごと）**: `.github/workflows/publish_blogger.yml`（4時間おきに起動し前回投稿から16時間経過していれば未投稿1記事＋JPEGアイキャッチを送信、`data/posted_blogger.json` に記録）

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

## 書き溜め済み記事一覧（全 70 本 / 最終更新: 2026-11-24 14:40 JST）

| No. | 17分類カテゴリ | 記事タイトル（Markdown） | 挿絵 | 生成日 |
| :---: | :--- | :--- | :---: | :---: |
| #70 | 分類02: コミュニケーション・情報共有 | [メールに大容量ファイルが送れない時の共有リンク活用＆誤送信防止の実例｜Windows・macOS・iOS・Android](content/2026-11-24_art70_email_attachment_size_limit_fix.md) | あり | 2026-11-24 |
| #69 | 分類01: 文書作成・オフィス業務・事務作業 | [住所・定型文を一発変換！OS標準「ユーザー辞書登録」と時短活用の実例｜Windows・macOS・iOS・Android](content/2026-11-24_art69_japanese_ime_dictionary_register.md) | あり | 2026-11-24 |
| #68 | 分類17: 生活・行政手続き・家計・資産管理 | [もしもの災害・緊急時に備える「緊急SOS・メディカルID・オフライン地図」設定実例｜Windows・macOS・iOS・Android](content/2026-11-24_art68_emergency_medical_id_disaster.md) | あり | 2026-11-24 |
| #67 | 分類16: 学習・教育・自己啓発 | [長文記事やPDFを耳で聴く！OS標準「読み上げ機能」の活用実例｜Windows・macOS・iOS・Android](content/2026-11-24_art67_text_to_speech_read_aloud.md) | あり | 2026-11-24 |
| #66 | 分類15: エンターテインメント・趣味 | [旅行写真を画質劣化なしで家族共有！共有アルバム＆スライドショー活用実例｜Windows・macOS・iOS・Android](content/2026-11-24_art66_photo_slideshow_album_family.md) | あり | 2026-11-24 |
| #65 | 分類14: ハードウェア・周辺機器・IoT連携 | [USB-Cケーブル・ハブで充電や画面出力ができない原因と正しい選び方実例｜Windows・macOS・iOS・Android](content/2026-11-24_art65_usb_c_cable_hub_not_charging.md) | あり | 2026-11-24 |
| #64 | 分類13: ファイル管理・バックアップ・データ復旧 | [新しいPC・スマホ買い替え時の公式データ移行＆失敗しない事前チェック実例｜Windows・macOS・iOS・Android](content/2026-11-24_art64_device_migration_new_pc_phone.md) | あり | 2026-11-24 |
| #63 | 分類12: セキュリティ・プライバシー対策 | [フィッシング詐欺・迷惑メール／SMSを見抜いてブロックする標準セキュリティ実例｜Windows・macOS・iOS・Android](content/2026-11-24_art63_phishing_spam_mail_sms_block.md) | あり | 2026-11-24 |
| #62 | 分類11: ネットワーク・サーバー・インフラ構築 | [サイトが開けない・遅い時のDNS設定（1.1.1.1 / 8.8.8.8）変更実例｜Windows・macOS・iOS・Android](content/2026-11-24_art62_dns_change_fast_safe_internet.md) | あり | 2026-11-24 |
| #61 | 分類10: システム管理・OS設定・メンテナンス | [PC・スマホの動作が重い・起動が遅い時のスタートアップ整理＆軽量化実例｜Windows・macOS・iOS・Android](content/2026-11-24_art61_startup_apps_slow_boot_fix.md) | あり | 2026-11-24 |
| #60 | 分類09: データ分析・科学計算・AI活用 | [PDFの表や紙の明細をExcel・スプレッドシートへ取り込んで集計する実例｜Windows・macOS・iOS・Android](content/2026-11-24_art60_pdf_table_to_spreadsheet_extract.md) | あり | 2026-11-24 |
| #59 | 分類08: Web制作・ブログ・デジタルマーケティング | [SNSシェア時にブログのアイキャッチ（OGP）が出ない・更新されない時の解決実例｜Windows・macOS・iOS・Android](content/2026-11-24_art59_blog_ogp_thumbnail_cache_fix.md) | あり | 2026-11-24 |
| #58 | 分類07: プログラミング・ソフトウェア開発 | [2つの文章・原稿の違いを一瞬で見抜く「差分比較（Diff）」の実例｜Windows・macOS・iOS・Android](content/2026-11-24_art58_text_diff_compare_changes.md) | あり | 2026-11-24 |
| #57 | 分類06: 3D・CAD・ものづくり | [3Dプリンター用モデル（STL）の入手・サイズ確認・データ共有の初心者実例｜Windows・macOS・iOS・Android](content/2026-11-24_art57_3d_print_stl_cloud_slicer_prep.md) | あり | 2026-11-24 |
| #56 | 分類05: 動画・音声・音楽制作 | [動画の自動字幕（ライブキャプション）表示＆字幕作成の実例｜Windows・macOS・iOS・Android](content/2026-11-24_art56_video_subtitles_captions_auto.md) | あり | 2026-11-24 |
| #55 | 分類04: 画像・イラスト・デザイン制作 | [SNS投稿前の写真ぼかし・モザイク加工と位置情報（Exif）削除の実例｜Windows・macOS・iOS・Android](content/2026-11-24_art55_photo_mosaic_exif_privacy.md) | あり | 2026-11-24 |
| #54 | 分類03: 情報収集・リサーチ・Web利用 | [ブラウザの自動入力（住所・クレカ・ID）を安全に管理・削除する実例｜Windows・macOS・iOS・Android](content/2026-11-24_art54_browser_autofill_privacy_manage.md) | あり | 2026-11-24 |
| #53 | 分類02: コミュニケーション・情報共有 | [クリップボード履歴とPC・スマホ間のコピペ連携を極める実例｜Windows・macOS・iOS・Android](content/2026-11-24_art53_clipboard_history_cross_device.md) | あり | 2026-11-24 |
| #52 | 分類01: 文書作成・オフィス業務・事務作業 | [キーボード不要！標準「音声入力」で文書・メールを高速作成する実例｜Windows・macOS・iOS・Android](content/2026-11-24_art52_voice_typing_dictation_docs.md) | あり | 2026-11-24 |
| #51 | 分類17: 生活・行政手続き・家計・資産管理 | [マイナポータル・オンライン行政手続きの読み取りエラー対策と活用実例｜Windows・macOS・iOS・Android](content/2026-11-24_art51_mynumber_digital_id_setup.md) | あり | 2026-11-24 |
| #50 | 分類16: 学習・教育・自己啓発 | [勉強・仕事に集中する「集中モード／通知制御」設定と着信逃し防止の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art50_focus_mode_notification_control.md) | あり | 2026-11-23 |
| #49 | 分類15: エンターテインメント・趣味 | [電子書籍・PDF読書の全端末同期とストレージ節約の管理実例｜Windows・macOS・iOS・Android](content/2026-11-23_art49_ebook_manga_library_sync.md) | あり | 2026-11-23 |
| #48 | 分類14: ハードウェア・周辺機器・IoT連携 | [Wi-Fiプリンターへのワイヤレス印刷設定と「オフライン」エラー解決実例｜Windows・macOS・iOS・Android](content/2026-11-23_art48_wireless_printer_airprint_setup.md) | あり | 2026-11-23 |
| #47 | 分類13: ファイル管理・バックアップ・データ復旧 | [誤削除した写真・書類をごみ箱やクラウド履歴から復元する緊急ガイド｜Windows・macOS・iOS・Android](content/2026-11-23_art47_deleted_file_trash_recovery.md) | あり | 2026-11-23 |
| #46 | 分類12: セキュリティ・プライバシー対策 | [フリーWi-Fiを安全に使うプライバシー設定とログイン画面が出ない時の対処｜Windows・macOS・iOS・Android](content/2026-11-23_art46_public_wifi_vpn_privacy_check.md) | あり | 2026-11-23 |
| #45 | 分類11: ネットワーク・サーバー・インフラ構築 | [スマホのテザリング（インターネット共有）接続手順と繋がらない時の解決実例｜Windows・macOS・iOS・Android](content/2026-11-23_art45_tethering_hotspot_connection_fix.md) | あり | 2026-11-23 |
| #44 | 分類10: システム管理・OS設定・メンテナンス | [バッテリーの減りが早い原因特定と劣化を防ぐ充電設定の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art44_battery_health_power_saving.md) | あり | 2026-11-23 |
| #43 | 分類09: データ分析・科学計算・AI活用 | [表計算ソフトでグラフ作成＆スマホでの確認・修正実例｜Windows・macOS・iOS・Android](content/2026-11-23_art43_spreadsheet_graph_chart_mobile.md) | あり | 2026-11-23 |
| #42 | 分類08: Web制作・ブログ・デジタルマーケティング | [仕事と私用を分けるブラウザ「プロファイル」管理と拡張機能トラブル対策｜Windows・macOS・iOS・Android](content/2026-11-23_art42_browser_profile_work_private.md) | あり | 2026-11-23 |
| #41 | 分類07: プログラミング・ソフトウェア開発 | [プログラミング不要で毎日を時短！標準自動化ツール活用の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art41_shortcuts_automator_routine.md) | あり | 2026-11-23 |
| #40 | 分類06: 3D・CAD・ものづくり | [模様替え・DIYの簡易図面＆手書きスケッチをPCとスマホで共有する実例｜Windows・macOS・iOS・Android](content/2026-11-23_art40_sketch_floorplan_diy_design.md) | あり | 2026-11-23 |
| #39 | 分類05: 動画・音声・音楽制作 | [音声ファイル（M4A/WAV/MP3）の変換と再生できない時の解決実例｜Windows・macOS・iOS・Android](content/2026-11-23_art39_audio_format_convert_mp3.md) | あり | 2026-11-23 |
| #38 | 分類04: 画像・イラスト・デザイン制作 | [写真の背景切り抜き・透過PNG作成を標準機能＆無料で行う実例｜Windows・macOS・iOS・Android](content/2026-11-23_art38_photo_background_remove_cutout.md) | あり | 2026-11-23 |
| #37 | 分類03: 情報収集・リサーチ・Web利用 | [増えすぎたタブ整理・リーディングリスト活用と全端末同期の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art37_reading_list_offline_articles.md) | あり | 2026-11-23 |
| #36 | 分類02: コミュニケーション・情報共有 | [Web会議（Zoom/Teams/Meet）でマイク・カメラが使えない時の解決実例｜Windows・macOS・iOS・Android](content/2026-11-23_art36_web_meeting_mic_camera_trouble.md) | あり | 2026-11-23 |
| #35 | 分類01: 文書作成・オフィス業務・事務作業 | [写真・スクショから文字をコピー（OCR文字認識）する標準機能の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art35_text_ocr_image_to_text.md) | あり | 2026-11-23 |
| #34 | 分類17: 生活・行政手続き・家計・資産管理 | [カレンダー予定の家族共有・全端末同期と通知が来ない時の対処実例｜Windows・macOS・iOS・Android](content/2026-11-23_art34_household_budget_calendar_sync.md) | あり | 2026-11-23 |
| #33 | 分類16: 学習・教育・自己啓発 | [Web翻訳・カメラ翻訳・音声翻訳の使い分けとオフライン翻訳の実例｜Windows・macOS・iOS・Android](content/2026-11-23_art33_language_translation_ocr_camera.md) | あり | 2026-11-23 |
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
