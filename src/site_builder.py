import html
import re
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List

import markdown

from src.catalog_manager import CatalogManager

JST = timezone(timedelta(hours=9))

COMMON_CSS = """
:root {
  --bg: #f8fafc;
  --surface: #ffffff;
  --text: #0f172a;
  --muted: #475569;
  --accent: #0284c7;
  --accent-soft: #e0f2fe;
  --border: #e2e8f0;
  --code-bg: #0f172a;
  --code-text: #e2e8f0;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Noto Sans JP", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.75;
}
header.site-header {
  background: linear-gradient(135deg, #0f172a 0%, #0369a1 100%);
  color: #fff;
  padding: 2.2rem 1.25rem;
}
header.site-header .inner { max-width: 980px; margin: 0 auto; }
header.site-header h1 { margin: 0 0 0.4rem; font-size: 1.75rem; }
header.site-header p { margin: 0; opacity: 0.9; font-size: 0.96rem; }
main { max-width: 980px; margin: 2rem auto; padding: 0 1.25rem 3rem; }
.badge {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 600;
  background: var(--accent-soft);
  color: #0369a1;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 1.25rem;
}
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08); }
.card img { width: 100%; aspect-ratio: 3 / 2; object-fit: cover; display: block; background: #e2e8f0; }
.card-body { padding: 1rem 1.1rem 1.2rem; flex: 1; display: flex; flex-direction: column; gap: 0.5rem; }
.card-title { font-size: 1.02rem; font-weight: 700; margin: 0; line-height: 1.45; }
.card-meta { font-size: 0.82rem; color: var(--muted); margin-top: auto; }
article.post {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 2rem;
}
article.post img.eyecatch {
  width: 100%;
  max-height: 460px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 1.5rem;
}
article.post h1 { font-size: 1.65rem; line-height: 1.35; margin-top: 0; }
article.post h2 {
  font-size: 1.3rem;
  margin-top: 2.1rem;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid var(--accent-soft);
}
article.post h3 { font-size: 1.08rem; margin-top: 1.4rem; }
article.post table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.2rem 0;
  font-size: 0.92rem;
  display: block;
  overflow-x: auto;
}
article.post th, article.post td {
  border: 1px solid var(--border);
  padding: 0.6rem 0.8rem;
  text-align: left;
}
article.post th { background: #f1f5f9; font-weight: 700; }
article.post pre {
  background: var(--code-bg);
  color: var(--code-text);
  padding: 1rem 1.15rem;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.88rem;
  line-height: 1.55;
}
article.post code {
  background: #f1f5f9;
  padding: 0.15rem 0.38rem;
  border-radius: 4px;
  font-size: 0.9em;
}
article.post pre code { background: transparent; padding: 0; color: inherit; }
article.post blockquote {
  margin: 1.2rem 0;
  padding: 0.8rem 1.1rem;
  border-left: 4px solid var(--accent);
  background: #f0f9ff;
  border-radius: 0 8px 8px 0;
}
.back-link { display: inline-block; margin-bottom: 1rem; color: var(--accent); text-decoration: none; font-weight: 600; }
footer { text-align: center; color: var(--muted); font-size: 0.85rem; padding: 2rem 1rem; }
@media (max-width: 640px) {
  article.post { padding: 1.2rem; }
}
"""


def _strip_meta_comment(md_text: str) -> str:
    return re.sub(r"^\s*<!--.*?-->\s*", "", md_text, count=1, flags=re.DOTALL).strip()


def _extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return fallback


def build_github_pages(
    catalog_mgr: CatalogManager,
    docs_dir: Path = Path("docs"),
    readme_path: Path = Path("README.md"),
) -> List[Path]:
    """Rebuilds docs/ static HTML site and updates README.md article catalog."""
    docs_dir = Path(docs_dir)
    articles_dir = docs_dir / "articles"
    images_dir = docs_dir / "images"
    articles_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    stocked = catalog_mgr.get_stocked_articles()
    built_files: List[Path] = []
    cards_html: List[str] = []
    readme_rows: List[str] = []

    for entry in reversed(stocked):
        item = entry["item"]
        md_path: Path = entry["md_path"]
        img_path = entry["img_path"]

        raw_md = md_path.read_text(encoding="utf-8", errors="ignore")
        clean_md = _strip_meta_comment(raw_md)
        title = _extract_title(clean_md, item.get("title", item["id"]))
        cat_num = item.get("cat_num", 0)
        cat_name = item.get("category", "")
        art_num = int(item.get("article_num", 0))
        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})_", md_path.name)
        pub_date = date_match.group(1) if date_match else datetime.now(JST).strftime("%Y-%m-%d")

        img_rel_from_article = ""
        img_rel_from_index = ""
        if img_path and img_path.exists():
            dst_img = images_dir / img_path.name
            shutil.copy2(img_path, dst_img)
            img_rel_from_article = f"../images/{img_path.name}"
            img_rel_from_index = f"images/{img_path.name}"

        body_html = markdown.markdown(
            clean_md,
            extensions=["tables", "fenced_code", "nl2br"],
        )

        eyecatch_tag = (
            f'<img class="eyecatch" src="{html.escape(img_rel_from_article)}" alt="{html.escape(title)}">'
            if img_rel_from_article
            else ""
        )
        article_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} | PC 4OS実例ガイド</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
  <header class="site-header">
    <div class="inner">
      <h1>PC 4OS実例ガイド</h1>
      <p>Windows・macOS・iOS・Android の実践比較＆トラブル解決アーカイブ</p>
    </div>
  </header>
  <main>
    <a class="back-link" href="../index.html">← 記事一覧へ戻る</a>
    <article class="post">
      <p><span class="badge">#{art_num:02d}｜分類{cat_num:02d}: {html.escape(cat_name)}</span> <small style="color:#64748b;margin-left:0.5rem;">{pub_date}</small></p>
      {eyecatch_tag}
      {body_html}
    </article>
  </main>
  <footer>Generated with Local Ollama (qwen3.5 / gemma4) &amp; Draw Things (FLUX.2 klein 4B)</footer>
</body>
</html>
"""
        out_html = articles_dir / f"{item['id']}.html"
        out_html.write_text(article_html, encoding="utf-8")
        built_files.append(out_html)

        thumb_html = (
            f'<img src="{html.escape(img_rel_from_index)}" alt="{html.escape(title)}" loading="lazy">'
            if img_rel_from_index
            else ""
        )
        cards_html.append(
            f"""<a class="card" href="articles/{html.escape(item['id'])}.html">
  {thumb_html}
  <div class="card-body">
    <div><span class="badge">分類{cat_num:02d}: {html.escape(cat_name)}</span></div>
    <h2 class="card-title">{html.escape(title)}</h2>
    <div class="card-meta">#{art_num:02d} ・ {pub_date}</div>
  </div>
</a>"""
        )

        img_mark = "あり" if img_path else "なし"
        readme_rows.append(
            f"| #{art_num:02d} | 分類{cat_num:02d}: {cat_name} | [{title}](content/{md_path.name}) | {img_mark} | {pub_date} |"
        )

    cards_section = (
        '<div class="grid">\n' + "\n".join(cards_html) + "\n</div>"
        if cards_html
        else "<p>まだ記事が生成されていません。<code>python -m src.main -n 1</code> を実行して最初の記事を作成してください。</p>"
    )

    updated_str = datetime.now(JST).strftime("%Y-%m-%d %H:%M JST")
    index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PC・スマホ 4OS実例ガイド｜Windows・macOS・iOS・Android比較＆トラブル解決</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
  <header class="site-header">
    <div class="inner">
      <h1>PC・スマホ 4OS実例ガイド</h1>
      <p>デジタル作業17分類をローテーションで網羅｜Windows・macOS・iOS・Android の実践比較＆トラブル解決</p>
    </div>
  </header>
  <main>
    <p style="color:#475569;margin-bottom:1.5rem;">公開記事数: <strong>{len(stocked)}</strong> 本（最終更新: {updated_str}）</p>
    {cards_section}
  </main>
  <footer>Powered by Local Ollama &amp; Draw Things (FLUX.2) ・ Hosted on GitHub Pages</footer>
</body>
</html>
"""
    index_path = docs_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    built_files.append(index_path)

    # Update README.md
    table_body = "\n".join(readme_rows) if readme_rows else "| - | - | まだ生成された記事はありません | - | - |"
    readme_text = f"""# PC・スマホ 4OS実例ガイド（pc-4os-guide）

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

## 書き溜め済み記事一覧（全 {len(stocked)} 本 / 最終更新: {updated_str}）

| No. | 17分類カテゴリ | 記事タイトル（Markdown） | 挿絵 | 生成日 |
| :---: | :--- | :--- | :---: | :---: |
{table_body}
"""
    readme_path.write_text(readme_text, encoding="utf-8")
    built_files.append(readme_path)
    return built_files
