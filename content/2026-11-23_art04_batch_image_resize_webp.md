<!--
article_id: art04-batch-image-resize-webp
article_num: 4
cat_num: 4
category: 画像・イラスト・デザイン制作
planner_model: qwen3.5:9b
writer_model: gemma4:12b (fact-checked against official docs)
verified_refs_count: 8
-->

# 【4OS徹底比較】画像の一括リサイズ＆HEIC/WebP変換の実例ガイド｜Windows・macOS・Linux・iPad

「ブログやWebサイトに載せる大量の写真をまとめて横幅1200pxに縮小したい」「iPhoneで撮ったHEIC形式をJPEGや軽量なWebPへ一括変換したい」——。

こうしたバッチ処理は、OSごとに「標準機能でできる範囲」と「公式ユーティリティ／CLIを使うべきライン」がはっきり分かれます。この記事では、Windows 11・macOS・Linux（Ubuntu系）・iPadOS の4環境における確実な手順を比較解説します。

---

## 4OS比較早見表

| OS | おすすめの標準／公式手段 | HEIC読込 | 一括リサイズ | WebP変換 | 特徴 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Windows 11** | Microsoft PowerToys (Image Resizer) | 要「HEIF 画像拡張機能」 | ◎（右クリック一括） | △（`cwebp`等併用） | PowerToys導入でエクスプローラーから最速処理 |
| **macOS** | Finder「クイックアクション」/ プレビュー / `sips` | ◎（標準対応） | ◎（GUI・CLI両方） | △（`cwebp`併用推奨） | Finder右クリックの「イメージを変換」が非常に手軽 |
| **Linux (Ubuntu)** | ImageMagick / `heif-convert` / `cwebp` | ◎（`libheif-examples`） | ◎（CLI一括） | ◎（`cwebp` / ImageMagick） | 大量ファイル・品質指定・自動化で最強 |
| **iPadOS** | 標準「ショートカット」アプリ | ◎（標準対応） | ◎（ショートカット） | △（JPEG/PNG/HEIF標準） | **外部アプリ不要でショートカットによる一括変換が可能** |

---

## 1. Windows 11 での実例手順

Windows の標準「フォト」アプリは1枚ずつのサイズ変更には対応していますが、複数ファイルの一括処理には不向きです。そこで Microsoft 公式ユーティリティ **PowerToys** の **Image Resizer** を使うのが定番です。

### 準備と実例手順
1. **HEIC対応**: HEIC画像が開けない場合は、Microsoft Store から **「HEIF 画像拡張機能」** をインストールします。
2. **一括リサイズ（Microsoft PowerToys Image Resizer）**:
   * Microsoft Store または `winget install Microsoft.PowerToys` で PowerToys を導入し、設定で「Image Resizer」を有効化。
   * エクスプローラーで対象画像を複数選択 → 右クリック → **「Image Resizer でサイズ変更」**。
   * プリセットまたはカスタムピクセルサイズ（例：幅 1200px）を指定して実行するだけで一括リサイズが完了します。
3. **WebPへの一括変換（公式 `cwebp` 使用例）**:
   ```powershell
   # Google公式のlibwebp (cwebp) を導入済みの環境で一括変換
   Get-ChildItem *.jpg | ForEach-Object {
     cwebp -q 82 $_.FullName -o ($_.BaseName + ".webp")
   }
   ```

---

## 2. macOS での実例手順

macOS は **Finder の「クイックアクション」** と **「プレビュー」**、さらに標準CLIの **`sips`** の3通りから選べます。

### GUIでの最短手順（Finder クイックアクション）
1. Finder で変換・リサイズしたい画像（HEIC・PNG等）を複数選択。
2. 右クリック → **「クイックアクション」＞「イメージを変換」** を選択。
3. フォーマット（JPEG / PNG / HEIF）と画像サイズ（小・中・大・実際のサイズ）を選んで「JPEGに変換」をクリックするだけで、元ファイルを残したまま一括変換できます。

### 正確なピクセル幅指定（標準CLI `sips`）
```bash
# フォルダ内の全HEICを横幅1280pxのJPEGへ一括変換して out/ に保存
mkdir -p out
for f in *.HEIC; do
  sips -s format jpeg -s formatOptions 85 -Z 1280 "$f" --out "out/${f%.HEIC}.jpg"
done
```
※ WebP へ変換したい場合は Homebrew で `brew install webp` を導入し、`cwebp -q 82 input.jpg -o output.webp` を使うのが最も確実です。

---

## 3. Linux（Ubuntu系）での実例手順

Ubuntu では **ImageMagick**、`libheif-examples`（`heif-convert`）、および **`webp`**（`cwebp`）を組み合わせることで、HEIC・PNG・JPEG・WebP間の相互変換とリサイズを完全に自動化できます。

### パッケージ導入
```bash
sudo apt update && sudo apt install -y imagemagick libheif-examples webp
```

### 一括リサイズ＆フォーマット変換の実例
```bash
# 1. HEICを横幅1600px以下のJPEGに一括変換（ImageMagick）
mkdir -p out_jpg
for f in *.HEIC; do
  convert "$f" -auto-orient -resize '1600x>' -quality 85 "out_jpg/${f%.HEIC}.jpg"
done

# 2. 変換したJPEGをWebPへ一括変換（Google公式 cwebp）
mkdir -p out_webp
for f in out_jpg/*.jpg; do
  base=$(basename "$f" .jpg)
  cwebp -q 82 "$f" -o "out_webp/${base}.webp"
done
```
※ `-auto-orient` を付けることでスマホ写真のExif回転情報による向きズレを防ぎ、`1600x>` の `>` 指定で「元画像が1600px未満なら拡大しない」設定にできます。

---

## 4. iPad（iPadOS）での実例手順

iPadOS でも、Apple 標準の **「ショートカット」アプリ** を使えば、追加アプリなしで複数写真の一括リサイズ＆JPEG変換が可能です。

### 「ショートカット」での一括リサイズ＆変換フロー
1. **「ショートカット」アプリ** を開き、右上の「＋」から新規ショートカットを作成。
2. 以下のアクションを順に並べる：
   - **「写真を選択」**（オプションで「複数を選択」をオン）
   - **「イメージのサイズを変更」**（例：幅 `1200` × 高さ `自動`）
   - **「イメージを変換」**（フォーマットを **JPEG**、品質を80〜85%に設定）
   - **「写真アルバムに保存」** または **「ファイルを保存」**
3. 作成したショートカットを実行し、変換したい写真をまとめて選ぶだけで一括処理が完了します。

> **iPhone/iPadで撮る写真を最初からJPEG互換にしたい場合:**
> 「設定」＞「カメラ」＞「フォーマット」で「互換性優先」を選ぶと、HEIFではなくJPEGで保存されるようになります。

---

## よくあるトラブルと解決チェックリスト

| トラブル現象 | 主な原因 | 確認・解決策 |
| :--- | :--- | :--- |
| **WindowsでHEIC画像が開けない・変換できない** | 「HEIF 画像拡張機能」が未導入 | Microsoft Store から「HEIF 画像拡張機能」をインストール |
| **リサイズしたら写真が90度回転してしまった** | Exifの回転情報（Orientation）が処理時に反映されていない | ImageMagickなら `-auto-orient` オプションを必ず付ける |
| **小さい画像まで拡大されてボケてしまった** | リサイズ時に上限指定をしていない | ImageMagickなら `-resize '1600x>'`（`>`で拡大防止）を使用 |
| **macOS/iPad標準機能でWebPが選べない** | 標準の「イメージを変換」はJPEG/PNG/HEIF中心 | WebP出力には `cwebp`（Google公式libwebp）を併用する |

---

## まとめ：快適なマルチOS環境を作るポイント

大量の画像処理は、**Windows（PowerToys）・macOS（Finderクイックアクション/`sips`）・Linux（ImageMagick/`cwebp`）・iPadOS（ショートカット）** と、それぞれの標準・公式ツールを使うことで安全かつ高速に完結します。

* **カラーマネジメントモニター**: 複数OS間で色味を確認しながら画像書き出しを行う場合、sRGBカバー率の高いモニターがあると仕上がりのブレを防げます。
* **高速な外付けSSD**: 高解像度RAW・大量のHEICデータをOS間で受け渡す際、USB-C接続の外付けSSDがあるとバッチ処理の待ち時間を大幅に短縮できます。

---

## 参考文献・公式ドキュメント（一次情報ソース）

本記事の手順・仕様は以下の各OSおよびツールの公式ドキュメントに基づいています。OSアップデートによりメニュー名称や挙動が変わる場合があるため、最新仕様の確認にもご活用ください。

- **[Windows]** [Image Resizer Windowsのユーティリティ - PowerToys | Microsoft Learn](https://learn.microsoft.com/ja-jp/windows/powertoys/image-resizer)
- **[macOS]** [Macの「プレビュー」で画像を切り取る/サイズ変更する/回転する - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/preview/prvw2015/mac)
- **[macOS]** [MacのFinderでクイックアクションを実行する（イメージを変換） - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/mac-help/mchl97ff9142/mac)
- **[Linux]** [ImageMagick Command-line Processing Documentation](https://imagemagick.org/script/command-line-processing.php)
- **[Linux]** [libheif (heif-convert) Official GitHub Repository](https://github.com/strukturag/libheif)
- **[Linux / 共通]** [cwebp | WebP Official Documentation | Google for Developers](https://developers.google.com/speed/webp/docs/cwebp)
- **[iPadOS]** [Apple製のデバイスでHEIF／HEVCメディアを扱う - Apple サポート (日本)](https://support.apple.com/ja-jp/116944)
- **[iPadOS]** [ショートカット ユーザガイド - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/shortcuts/welcome/ios)
