<!--
article_id: art04-batch-image-resize-webp
article_num: 4
cat_num: 4
category: 画像・イラスト・デザイン制作
planner_model: qwen3.5:9b
writer_model: gemma4:12b (fact-checked against official docs)
verified_refs_count: 7
-->

# 【4OS徹底比較】画像の一括リサイズ＆HEIC/WebP変換の実例ガイド｜Windows・macOS・iOS・Android

「ブログやSNSに載せる大量の写真をまとめて横幅1200pxに縮小したい」「iPhoneで撮ったHEIC形式を、どこでも開けるJPEGや軽量なWebPへ一括変換したい」——。

こうした画像処理は、OSごとに「標準機能でできる範囲」と「公式ユーティリティを使うべきライン」がはっきり分かれます。この記事では、**Windows 11・macOS・iOS（iPhone / iPad）・Android** の4環境における初心者でも迷わない確実な手順を比較解説します。

---

## 4OS比較早見表

| OS | おすすめの標準／公式手段 | HEIC読込 | 一括リサイズ | WebP変換 | 特徴 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Windows 11** | Microsoft PowerToys (Image Resizer) | 要「HEIF 画像拡張機能」 | ◎（右クリック一括） | △（`cwebp`等併用） | PowerToys導入でエクスプローラーから最速処理 |
| **macOS** | Finder「クイックアクション」/ プレビュー | ◎（標準対応） | ◎（GUI一括） | △（`cwebp`併用推奨） | Finder右クリックの「イメージを変換」が非常に手軽 |
| **iOS (iPhone/iPad)** | 標準「ショートカット」アプリ | ◎（標準対応） | ◎（ショートカット） | △（JPEG/PNG/HEIF標準） | **外部アプリ不要でショートカットによる一括変換が可能** |
| **Android** | Google フォト / カメラ設定 / 専用アプリ | ◎（標準対応） | △（標準は1枚ずつ） | ◎（閲覧・一部対応） | 1枚の切り抜きはGoogleフォト、一括処理はPCまたは専用アプリが現実的 |

---

## 1. Windows 11 での実例手順

Windows の標準「フォト」アプリは1枚ずつのサイズ変更には対応していますが、複数ファイルの一括処理には不向きです。そこで Microsoft 公式ユーティリティ **PowerToys** の **Image Resizer** を使うのが定番です。

### 準備と実例手順
1. **HEIC対応**: HEIC画像が開けない場合は、Microsoft Store から **「HEIF 画像拡張機能」** をインストールします。
2. **一括リサイズ（Microsoft PowerToys Image Resizer）**:
   * Microsoft Store で **Microsoft PowerToys** をインストールし、設定画面で「Image Resizer」を有効化。
   * エクスプローラーで対象画像を複数選択 → 右クリック → **「Image Resizer でサイズ変更」**。
   * プリセットまたはカスタムピクセルサイズ（例：幅 1200px）を指定して実行するだけで一括リサイズが完了します。
3. **WebPへの一括変換（Google公式 `cwebp` 使用例）**:
   ```powershell
   # Google公式のlibwebp (cwebp) を導入済みの環境で一括変換
   Get-ChildItem *.jpg | ForEach-Object {
     cwebp -q 82 $_.FullName -o ($_.BaseName + ".webp")
   }
   ```

---

## 2. macOS での実例手順

macOS は **Finder の「クイックアクション」** を使うと、アプリを立ち上げることなく右クリックだけで複数画像を一括変換・縮小できます。

### GUIでの最短手順（Finder クイックアクション）
1. Finder で変換・リサイズしたい画像（HEIC・PNG等）を複数選択。
2. 右クリック → **「クイックアクション」＞「イメージを変換」** を選択。
3. フォーマット（JPEG / PNG / HEIF）と画像サイズ（小・中・大・実際のサイズ）を選んで「JPEGに変換」をクリックするだけで、元ファイルを残したまま一括変換できます。

### 細かいピクセル幅を指定したい場合（「プレビュー」アプリ）
1. 対象画像を複数選択して「プレビュー」で開き、サイドバーで全画像を選択（`Cmd + A`）。
2. メニューバーの **「ツール」＞「サイズを調整…」** から希望の幅（px）を指定して保存します。

---

## 3. iOS（iPhone / iPad）での実例手順

iOS でも、Apple 標準の **「ショートカット」アプリ** を使えば、追加アプリなしで複数写真の一括リサイズ＆JPEG変換が可能です。

### 「ショートカット」での一括リサイズ＆変換フロー
1. **「ショートカット」アプリ** を開き、右上の「＋」から新規ショートカットを作成。
2. 以下のアクションを順に並べる：
   - **「写真を選択」**（オプションで「複数を選択」をオン）
   - **「イメージのサイズを変更」**（例：幅 `1200` × 高さ `自動`）
   - **「イメージを変換」**（フォーマットを **JPEG**、品質を80〜85%に設定）
   - **「写真アルバムに保存」** または **「ファイルを保存」**
3. 作成したショートカットを実行し、変換したい写真をまとめて選ぶだけで一括処理が完了します。

> **iPhoneで撮る写真を最初からJPEG互換にしたい場合:**
> 「設定」＞「カメラ」＞「フォーマット」で **「互換性優先」** を選ぶと、HEIFではなくJPEGで保存されるようになります。

---

## 4. Android での実例手順

Android は機種ごとに標準ギャラリーアプリが異なりますが、多くの端末に標準搭載されている **Google フォト** とカメラ設定を押さえておくと迷いません。

### 具体的な実例手順
* **1枚ずつの切り抜き・軽量化（Google フォト）**:
  1. **Google フォト** で写真を開き、下部の **「編集」** → **「切り抜き」** から比率や範囲を調整して「コピーを保存」。
* **HEIC（高効率フォーマット）を使わずJPEGで撮る設定**:
  * 標準カメラアプリの「設定」で **「高効率写真（HEIF / HEIC）」** がオンになっていると他環境で開けない場合があります。互換性重視ならオフ（JPEG保存）にしておきます。
* **複数枚の一括リサイズ・WebP変換について**:
  * Android標準のGoogleフォトには「複数写真を指定ピクセル幅へ一括リサイズ／WebP変換する機能」はありません。大量の写真を一括処理する場合は、Googleドライブ経由でPC側（Windows PowerToys / macOS クイックアクション）で処理するのが最も確実で画質管理もしやすい方法です。

---

## よくあるトラブルと解決チェックリスト

| トラブル現象 | 主な原因 | 確認・解決策 |
| :--- | :--- | :--- |
| **WindowsでiPhoneのHEIC画像が開けない** | 「HEIF 画像拡張機能」が未導入 | Microsoft Store から「HEIF 画像拡張機能」をインストール |
| **スマホから送った写真が横向きになる** | 変換ツールがExifの回転情報（Orientation）を保持していない | OS公式ツール（PowerToys / Finderクイックアクション / iOSショートカット）を使う |
| **小さい画像まで拡大されてボケてしまった** | リサイズ設定で元より大きい幅を指定した | PowerToysなら「小さい画像は拡大しない」オプションを有効にする |
| **WebP形式の画像を古いソフトで開けない** | 相手先ソフトがWebPに非対応 | 配布・提出用はJPEGまたはPNG形式で書き出してから渡す |

---

## まとめ：快適なマルチOS環境を作るポイント

大量の画像処理は、**PC側（Windows PowerToys / macOS Finderクイックアクション）とiOS「ショートカット」**を使い分けることで、余計な広告付きアプリを入れずに安全かつ高速に完結します。

* **カラーマネジメントモニター**: PCでブログ画像や写真の色味を確認しながら書き出す場合、発色の正確なモニターがあると仕上がりのブレを防げます。
* **高速な外付けSSD**: 高解像度写真や大量のHEICデータをPCとスマホ間で受け渡す際、USB-C接続の外付けSSDがあると作業待ち時間を大幅に短縮できます。

---

## 参考文献・公式ドキュメント（一次情報ソース）

本記事の手順・仕様は以下の各OSおよびツールの公式ドキュメントに基づいています。OSアップデートによりメニュー名称や挙動が変わる場合があるため、最新仕様の確認にもご活用ください。

- **[Windows]** [Image Resizer Windowsのユーティリティ - PowerToys | Microsoft Learn](https://learn.microsoft.com/ja-jp/windows/powertoys/image-resizer)
- **[macOS]** [Macの「プレビュー」で画像を切り取る/サイズ変更する/回転する - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/preview/prvw2015/mac)
- **[macOS]** [MacのFinderでクイックアクションを実行する（イメージを変換） - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/mac-help/mchl97ff9142/mac)
- **[iOS]** [Apple製のデバイスでHEIF／HEVCメディアを扱う - Apple サポート (日本)](https://support.apple.com/ja-jp/116944)
- **[iOS]** [ショートカット ユーザガイド - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/shortcuts/welcome/ios)
- **[Android]** [写真を編集する - Google フォト ヘルプ](https://support.google.com/photos/answer/6128850?hl=ja)
- **[共通]** [cwebp | WebP Official Documentation | Google for Developers](https://developers.google.com/speed/webp/docs/cwebp)
