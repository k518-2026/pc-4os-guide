<!--
article_id: art03-screenshot-screen-recording
article_num: 3
cat_num: 3
category: 情報収集・リサーチ・Web利用
planner_model: qwen3.5:9b
writer_model: gemma4:12b (fact-checked against official docs)
verified_refs_count: 7
-->

# 【4OS徹底比較】スクリーンショット・画面録画の最短手順と保存先トラブル対処｜Windows・macOS・Linux・iPad

「急に画面を撮りたいのにショートカットを忘れてしまった」「録画した動画がどこに保存されたか分からない」「Webページ全体を縦長に保存したい」——。

複数のOSを行き来していると、ショートカットキーや標準の保存先の違いで迷いがちです。この記事では、**Windows 11・macOS・Linux（Ubuntu 22.04/24.04・Wayland対応）・iPadOS** の4環境において、追加アプリ不要の**標準機能だけで完結する正確な手順**と、よくあるトラブルの解決法を比較します。

## 4OS比較早見表

| 機能 | Windows 11 | macOS | Linux (Ubuntu / GNOME) | iPadOS |
| :--- | :--- | :--- | :--- | :--- |
| **スクショ（範囲指定）** | `Win + Shift + S` | `Shift + Cmd + 4` | `Print Screen` キー | トップ＋音量ボタン同時押し |
| **画面録画（標準）** | Snipping Tool / `Win + G` | `Shift + Cmd + 5` / QuickTime | `Ctrl + Shift + Alt + R` | コントロールセンター「画面収録」 |
| **Web縦長保存** | Edge「Webキャプチャ」/ 印刷PDF | Safari「PDFとして書き出す」 | ブラウザ印刷PDF / 開発者ツール | **Safariスクショ →「フルページ」** |
| **デフォルト保存先** | `ピクチャ\Screenshots`<br>`ビデオ\画面録画` | デスクトップ（変更可） | `~/ピクチャ/スクリーンショット`<br>`~/ビデオ/スクリーンキャスト` | 「写真」アプリ（フルページは「ファイル」） |

---

## 1. Windows 11 での実例手順（Snipping Tool / Xbox Game Bar）

現在の Windows 11 では、標準の **Snipping Tool** がスクリーンショットだけでなく**画面録画（範囲指定録画）**にもネイティブ対応しています。

### 具体的な実例手順
* **スクリーンショット**:
  * `Win + Shift + S` を押すと画面上部にオーバーレイが表示され、四角形・ウィンドウ・全画面・フリーフォームで撮影できます。クリップボードにコピーされるほか、自動保存オン時は `C:\Users\ユーザー名\Pictures\Screenshots` へ保存されます。
* **画面録画**:
  * **Snipping Tool** を起動し、上部のカメラアイコンから**ビデオアイコン（録画）**に切り替えて「新規」→ 範囲選択 →「スタート」で録画できます（既定保存先：`C:\Users\ユーザー名\Videos\Screen Recordings`）。
  * ゲームや長時間のアプリ録画には `Win + G`（Xbox Game Bar）も利用可能です（保存先：`Videos\Captures`）。
* **Webページ縦長保存**:
  * Microsoft Edge で `Ctrl + Shift + S`（Webキャプチャ）を使うか、`Ctrl + P` で「PDFとして保存」を利用します。

---

## 2. macOS での実例手順（標準ショートカット / QuickTime Player）

macOS は **`Shift + Command + 3 / 4 / 5`** の3つのショートカットを覚えるだけで、撮影から画面録画、保存先変更まで完結します。

### 具体的な実例手順
* **スクリーンショット**:
  * **全画面**: `Shift + Command + 3`
  * **範囲指定**: `Shift + Command + 4`（ドラッグ中に `Space` を押すと選択範囲を移動、選択前に `Space` を押すとウィンドウ単位で撮影可能）
  * **メニュー付き（録画・保存先変更も可）**: **`Shift + Command + 5`**
* **画面録画**:
  * `Shift + Command + 5` を押して画面下部のツールバーから「画面全体を収録」または「選択部分を収録」を選びます。
  * QuickTime Player を使う場合は、メニューバーの **「ファイル」＞「新規画面収録」** を選択します（※「新規ムービー収録」はWebカメラ撮影なので注意）。
* **保存先の確認・変更**:
  * デフォルトはデスクトップですが、`Shift + Command + 5` →「オプション」から任意のフォルダに変更できます。

---

## 3. Linux（Ubuntu系）での実例手順（GNOME標準 / Wayland対応）

Ubuntu 22.04 LTS / 24.04 LTS 以降では、ディスプレイサーバーに **Wayland** が標準採用されています。従来の X11 向けツール（`ffmpeg -f x11grab` 等）は Wayland 環境では真っ黒な画面になるため、まずは **GNOME 標準機能**を使うのが最も確実です。

### 具体的な実例手順
* **スクリーンショット（GNOME標準UI）**:
  * `Print Screen` キーを押すと、範囲選択・画面全体・ウィンドウ選択ができる標準キャプチャUIが開きます。
  * `Shift + Print Screen` で即座に全画面撮影、`Alt + Print Screen` でアクティブウィンドウ撮影。
  * 保存先：`~/Pictures/Screenshots`（日本語環境では `~/ピクチャ/スクリーンショット`）
* **画面録画（GNOME標準スクリーンキャスト）**:
  * **`Ctrl + Shift + Alt + R`**（または `Print Screen` のUIでビデオアイコンへ切替）で録画開始／停止ができます。
  * 保存先：`~/Videos/Screencasts`（WebM形式）
* **X11セッション環境で CLI 録画する場合（`ffmpeg`）**:
  ```bash
  # ※ WaylandではなくXorg(X11)セッション上でのみ有効
  ffmpeg -f x11grab -video_size 1920x1080 -i :0.0 -c:v libx264 -pix_fmt yuv420p output.mp4
  ```

---

## 4. iPad（iPadOS）での実例手順

iPadOS は標準機能だけで **Safari のWebページ全体（フルページ）保存** にも対応しています。

### 具体的な実例手順
* **スクリーンショット**:
  * ホームボタンのないモデル：**トップボタン ＋ いずれかの音量ボタン**を同時押し（または Apple Pencil で画面左下／右下隅から斜め上にスワイプ）。
  * ホームボタンのあるモデル：**トップボタン ＋ ホームボタン**を同時押し。
* **Safari のWebページ縦長保存（フルページ）**:
  1. Safari で保存したいページを開き、通常通りスクリーンショットを撮る。
  2. 左下に表示されるサムネイルをタップし、画面上部の **「フルページ」** タブに切り替える。
  3. 「完了」→ **「PDFを“ファイル”に保存」** を選ぶと、ページ全体の縦長PDFとして保存されます。
* **画面録画**:
  * 画面右上から下にスワイプしてコントロールセンターを開き、**「画面収録（二重丸アイコン）」** をタップ。音声（マイク）も入れたい場合はアイコンを長押ししてマイクをオンにします。

---

## よくあるトラブルと解決チェックリスト

| トラブル現象 | 主な原因 | 確認・解決策 |
| :--- | :--- | :--- |
| **WindowsでSnipping Toolの録画ファイルが見つからない** | 自動保存オフ、または録画中断で一時フォルダに残留 | `Videos\Screen Recordings` を確認。異常終了時はアプリ設定（設定 ＞ アプリ ＞ インストールされているアプリ ＞ Snipping Tool ＞ 詳細オプション）から修復を実行 |
| **macOSで画面収録ができない・背景しか映らない** | 「画面収録」のプライバシー権限がオフ | システム設定 ＞ プライバシーとセキュリティ ＞「画面収録とシステムオーディオ録音」を確認 |
| **Ubuntuで `ffmpeg` の `x11grab` が真っ黒になる** | WaylandセッションでX11用キャプチャを実行している | GNOME標準の `Ctrl + Shift + Alt + R` を使うか、ログイン画面で「Ubuntu on Xorg」を選択 |
| **iPadの画面録画で自分の声が入らない** | コントロールセンターのマイク設定がオフ | 画面収録ボタンを**長押し**し、下部のマイクアイコンをタップしてオンにする |

---

## まとめ：快適なマルチOS環境を作るポイント

4OSとも、最新バージョンでは**外部アプリを入れなくても「範囲指定スクショ＋画面録画＋Web縦長保存」が標準で完結**するようになっています。

* **トラックボールマウス**: 細かい範囲指定キャプチャや長時間のリサーチ作業で手首の負担を減らせます。
* **VPNサービス**: 外出先の公衆Wi-Fiで調査・画面共有を行う際の通信保護に有効です。
* **ブルーライトカット眼鏡・モニターライト**: キャプチャ確認やドキュメント作成の長時間作業での目の疲労軽減に役立ちます。

---

## 参考文献・公式ドキュメント（一次情報ソース）

本記事の手順・仕様は以下の各OSおよびツールの公式ドキュメントに基づいています。OSアップデートによりメニュー名称や挙動が変わる場合があるため、最新仕様の確認にもご活用ください。

- **[Windows]** [Snipping Tool を使ってスクリーンショットをキャプチャする・画面録画する - Microsoft サポート](https://support.microsoft.com/ja-jp/windows/snipping-tool-%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%E3%82%92%E3%82%AD%E3%83%A3%E3%83%97%E3%83%81%E3%83%A3%E3%81%99%E3%82%8B-00246869-1843-655f-f220-97299b865f6b)
- **[macOS]** [Macでスクリーンショットを撮る - Apple サポート (日本)](https://support.apple.com/ja-jp/102646)
- **[macOS]** [Macで画面を収録する方法 - Apple サポート (日本)](https://support.apple.com/ja-jp/102618)
- **[Linux]** [スクリーンショットとスクリーンキャスト - GNOME ヘルプ（Ubuntu標準）](https://help.gnome.org/users/gnome-help/stable/screen-shot-record.html.ja)
- **[Linux]** [FFmpeg Devices Documentation (x11grab / 入力デバイス仕様)](https://ffmpeg.org/ffmpeg-devices.html)
- **[iPadOS]** [iPadでスクリーンショットを撮る（フルページ保存を含む） - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/ipad/ipad08a40f3b/ipados)
- **[iPadOS]** [iPhone、iPad、iPod touchで画面を録画する - Apple サポート (日本)](https://support.apple.com/ja-jp/102653)
