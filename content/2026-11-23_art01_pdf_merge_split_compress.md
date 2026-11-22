<!--
article_id: art01-pdf-merge-split-compress
article_num: 1
cat_num: 1
category: 文書作成・オフィス業務・事務作業
planner_model: qwen3.5:9b
writer_model: gemma4:12b (fact-checked against official docs)
verified_refs_count: 8
-->

# 【4OS徹底比較】PDFの結合・分割・圧縮を無料で行う実例ガイド｜Windows・macOS・Linux・iPad

「複数のPDFを1つにまとめたい」「長い資料から必要なページだけ抜き出したい」「メール添付のためにファイルサイズを軽くしたい」——。こうした場面で、有料のAdobe Acrobatを契約せずとも、**OS標準機能や定番の無料コマンドラインツール**だけで対応できる範囲はかなり広いです。

ただし、**「標準機能だけでできること・できないこと」にはOSごとに明確な差**があります。この記事では、Windows 11・macOS・Linux（Ubuntu系）・iPadOSの4環境における正確な手順と、公式仕様に基づく制限事項・トラブル対処法を徹底比較します。

## 4OS比較早見表

| OS | 主な操作手段 | 結合 | 分割（ページ抽出） | 圧縮（軽量化） | 特徴・注意点 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Windows 11** | Edge / Microsoft Print to PDF | ×（標準のみは不可） | ◎（ページ指定印刷） | ×（標準では非対応） | 分割のみ標準可。結合・圧縮は無料ツール併用が現実的 |
| **macOS** | プレビュー（Preview） | ◎（サムネイルD&D） | ◎（ページ削除／D&D） | ◎（Quartzフィルタ） | **3操作すべてOS標準アプリだけで完結** |
| **Linux (Ubuntu)** | `pdfunite` / `pdfseparate` / `gs` | ◎（`pdfunite`） | ◎（`pdfseparate`） | ◎（Ghostscript `gs`） | CLIで高速・一括処理可能。`qpdf`でWeb最適化も可 |
| **iPadOS** | 「ファイル」＆「ショートカット」 | ◎（ショートカット） | ◎（ファイル/印刷） | △（標準では限定的） | 標準の「ショートカット」アプリで複数PDF結合が可能 |

---

## 1. Windows 11 での実例手順

Windows 11 の標準機能（Microsoft Edge ＋ 仮想プリンタ `Microsoft Print to PDF`）で確実にできるのは**「分割（必要ページの抽出）」**です。

### 具体的な実例手順
* **分割（特定ページだけ抽出）**:
  1. 対象のPDFファイルを **Microsoft Edge** で開く。
  2. `Ctrl + P` で印刷ダイアログを開き、プリンターに **「Microsoft Print to PDF」**（または「PDF として保存」）を選択。
  3. 「ページ」欄をカスタムにし、抽出したいページ番号（例：`1-3, 5`）を指定して保存する。
* **結合・圧縮について（標準機能の制限）**:
  * Windows 標準の `Microsoft Print to PDF` 単体では**複数PDFの結合や、画像再圧縮による大幅な軽量化は行えません**。
  * 結合・圧縮を安全にローカル環境で無料実行したい場合は、オープンソースの `PDFsam Basic` や `PDF24 Creator`、あるいは WSL2 / Winget 経由で Linux と同じ `qpdf`・`Ghostscript` を導入するのが確実です。

---

## 2. macOS での実例手順

macOS は標準搭載の **「プレビュー（Preview）」** アプリが非常に強力で、結合・分割・圧縮の3つすべてが追加アプリなしで完結します。

### 具体的な実例手順
* **結合**:
  1. 1つ目のPDFを「プレビュー」で開き、メニューバーから **「表示」＞「サムネイル」** を選択してサイドバーを表示する。
  2. 結合したい別のPDFファイルを Finder からサイドバーの挿入したい位置へドラッグ＆ドロップする。
  3. **「ファイル」＞「保存」**（または「書き出す…」）で保存する。
* **分割（不要ページの削除・抽出）**:
  * サイドバーのサムネイルで不要なページを選択して `Delete` キーで削除するか、必要なページだけを選択してデスクトップ等へドラッグ＆ドロップすると、そのページだけの新しいPDFが作成されます。
* **圧縮（ファイルサイズ削減）**:
  1. 「プレビュー」でPDFを開き、**「ファイル」＞「書き出す…」** を選択（※「PDFとして書き出す」ではない点に注意）。
  2. **「Quartz フィルタ」** のプルダウンから **「Reduce File Size」** を選択して保存する。

> **macOSでの注意点:**
> 「Reduce File Size」は内蔵画像を強く再圧縮するため、細かい図表やスキャン文字が粗くなる場合があります。元ファイルは必ず別名保存で残してください。

---

## 3. Linux（Ubuntu系）での実例手順

Ubuntu では `poppler-utils`（`pdfunite` / `pdfseparate`）と `ghostscript`（`gs`）を組み合わせるのが、軽量かつ最も確実です。

### 準備（パッケージ導入）
```bash
sudo apt update && sudo apt install -y poppler-utils ghostscript qpdf
```

### 具体的な実例手順
* **結合（`pdfunite`）**:
  ```bash
  pdfunite file1.pdf file2.pdf combined.pdf
  ```
* **分割（`pdfseparate` で1〜5ページを1ページずつ抽出、または `qpdf` で範囲抽出）**:
  ```bash
  # 1〜5ページを1ページごとのPDFに分割
  pdfseparate -f 1 -l 5 input.pdf page_%d.pdf

  # 1〜5ページを1つのPDFとして抽出（qpdf）
  qpdf input.pdf --pages . 1-5 -- part1.pdf
  ```
* **圧縮（Ghostscript による画像再圧縮）**:
  ```bash
  # /ebook (150dpi相当・バランス重視) や /screen (72dpi相当・最小サイズ) を指定
  gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
     -dNOPAUSE -dQUIET -dBATCH -sOutputFile=compressed.pdf input.pdf
  ```
  ※ Web表示を高速化（先頭ページから順次表示）したい場合は `qpdf --linearize input.pdf web_ready.pdf` を併用します。

---

## 4. iPad（iPadOS）での実例手順

iPadOS でも、標準の **「ファイル」アプリ** と **「ショートカット」アプリ** を組み合わせることで、外部Webサービスにファイルをアップロードせずに結合・抽出が行えます。

### 具体的な実例手順
* **結合（「ショートカット」アプリを使用）**:
  1. 「ショートカット」アプリを開き、新規ショートカットを作成。
  2. アクションを追加：
     - **「ファイルを選択」**（オプションで「複数を選択」をオン）
     - **「PDFを作成」**（または複数画像を1つのPDF化／PDF結合アクション）
     - **「ファイルを保存」**
  3. 実行して対象PDFを選ぶだけで、結合済みPDFを「ファイル」アプリ内に保存できます。
* **分割（特定ページの抽出）**:
  1. 「ファイル」アプリでPDFを開き、共有ボタン（上矢印）→ **「プリント」** をタップ。
  2. 「範囲」で必要なページを指定し、プリント画面のプレビューを共有ボタンから **「“ファイル”に保存」** すると、指定ページだけのPDFとして保存されます。
* **圧縮**:
  * iPadOS標準機能には画質調整付きの高度なPDF圧縮機能はありません。大幅な圧縮が必要な場合は、Macの「プレビュー」やローカルPC側で処理するのが安全です。

---

## よくあるトラブルと解決チェックリスト

| トラブル現象 | 主な原因 | 確認・解決策 |
| :--- | :--- | :--- |
| **結合・抽出後に文字が検索できなくなる** | 仮想プリンタ出力時にテキストが画像化（ラスタライズ）された | Windowsの印刷出力ではなく、`qpdf` や macOS「プレビュー」のサムネイル結合を使う |
| **圧縮したら図表が読めなくなった** | `Reduce File Size` や `-dPDFSETTINGS=/screen` の圧縮率が高すぎる | Ghostscriptなら `/ebook` や `/printer` に変更し、必ず元ファイルを残す |
| **パスワード保護されたPDFが処理できない** | 編集制限・閲覧パスワードが設定されている | 権限のあるファイルであれば `qpdf --password=パスワード --decrypt in.pdf out.pdf` で解除後に処理する |
| **社外秘PDFを無料Webサイトに上げてしまった** | オンライン変換サービスの利用 | 機密文書は必ず本記事のような**オフライン（ローカル）手順**で処理する |

---

## まとめ：快適なマルチOS環境を作るポイント

PDFの結合・分割・圧縮は、**macOS（プレビュー）とLinux（CLI）が標準／無料ツールで完結しやすく、WindowsとiPadは役割分担すると効率的**です。

* **Office互換ソフト・PDF編集ソフト**: 業務で頻繁にPDFのテキスト編集や墨消しを行う場合は、ローカル動作の専用PDFソフトを導入すると作業時間を大幅に短縮できます。
* **外付けキーボード・大型モニター**: 複数PDFを見比べながらページ順を整理する作業では、広い画面とショートカット操作が圧倒的に快適です。

---

## 参考文献・公式ドキュメント（一次情報ソース）

本記事の手順・仕様は以下の各OSおよびツールの公式ドキュメントに基づいています。OSアップデートによりメニュー名称や挙動が変わる場合があるため、最新仕様の確認にもご活用ください。

- **[Windows]** [Microsoft Edge 印刷・PDF関連ポリシー公式ドキュメント | Microsoft Learn](https://learn.microsoft.com/ja-jp/deployedge/microsoft-edge-policies#printing)
- **[macOS]** [Macの「プレビュー」でPDFを結合する - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/preview/prvw43696/mac)
- **[macOS]** [Macの「プレビュー」でPDFのサイズを減らす - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/preview/prvw1509/mac)
- **[Linux]** [Ubuntu Manpage: pdfunite (poppler-utils) - PDF page merger](https://manpages.ubuntu.com/manpages/noble/en/man1/pdfunite.1.html)
- **[Linux]** [Ubuntu Manpage: pdfseparate (poppler-utils) - PDF page extractor](https://manpages.ubuntu.com/manpages/noble/en/man1/pdfseparate.1.html)
- **[Linux]** [Ghostscript High Level Devices (pdfwrite / PDF圧縮設定)](https://ghostscript.readthedocs.io/en/latest/VectorDevices.html)
- **[Linux]** [qpdf CLI Documentation (Web最適化・線形化)](https://qpdf.readthedocs.io/en/stable/cli.html)
- **[iPadOS]** [ショートカット ユーザガイド - Apple サポート (日本)](https://support.apple.com/ja-jp/guide/shortcuts/welcome/ios)
