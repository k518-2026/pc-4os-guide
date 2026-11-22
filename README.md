# PC 4OS実例ガイド（pc-4os-guide）

PCで行うことができる作業 **17分類** をローテーションしながら、**Windows / macOS / Linux / iPad** の4OSでの具体的な手順比較とトラブル解決法をローカルAIで自動執筆・挿絵生成し、GitHubに書き溜めるプロジェクトです。

## システム構成

* **文章生成（Ollama）**: `http://192.168.128.62:11434/`（`qwen3.5:9b` 構成・検証 × `gemma4:12b` 執筆）
* **挿絵生成（Draw Things）**: `http://192.168.128.59:7860/`（`FLUX.2 [klein] 4B`, `768x512` 横長アイキャッチ）
* **記事ストック**: `content/YYYY-MM-DD_artXX_slug.md` + `.png`
* **Web公開（GitHub Pages）**: `docs/index.html` および `docs/articles/*.html`

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

## 書き溜め済み記事一覧（全 1 本 / 最終更新: 2026-11-23 01:18 JST）

| No. | 17分類カテゴリ | 記事タイトル（Markdown） | 挿絵 | 生成日 |
| :---: | :--- | :--- | :---: | :---: |
| #01 | 分類01: 文書作成・オフィス業務・事務作業 | [【4OS徹底比較】PDFの結合・分割・圧縮を無料で行う実例ガイド｜Windows・macOS・Linux・iPad](content/2026-11-23_art01_pdf_merge_split_compress.md) | あり | 2026-11-23 |
