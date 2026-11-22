import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.article_generator import compose_title_card
from src.catalog_manager import CatalogManager
from src.config import AppConfig
from src.hatena_mailer import (
    HatenaHistoryManager,
    HatenaMailSender,
    format_markdown_for_hatena,
    select_next_article_for_hatena,
)
from src.reference_verifier import format_references_markdown, get_verified_references
from src.site_builder import build_github_pages


class TestPC4OSGuide(unittest.TestCase):
    def test_title_card_composition(self):
        buf = io.BytesIO()
        Image.new("RGB", (768, 512), color=(30, 60, 120)).save(buf, format="PNG")
        out = compose_title_card(
            buf.getvalue(),
            article={
                "article_num": 1,
                "cat_num": 1,
                "category": "文書作成・オフィス業務・事務作業",
                "title": "【4OS徹底比較】PDFの結合・分割・圧縮を無料で行う実例ガイド｜Windows・macOS・iOS・Android",
            },
            category_meta={"short_name": "文書・オフィス", "accent_hex": "#E11D48"},
        )
        img = Image.open(io.BytesIO(out))
        self.assertEqual(img.size, (768, 512))

    def test_references_formatter_no_linux(self):
        for cnum in (1, 2, 3, 4):
            refs = get_verified_references(cat_num=cnum, check_live=False)
            self.assertGreaterEqual(len(refs), 4)
            md = format_references_markdown(refs)
            self.assertIn("参考文献・公式ドキュメント", md)
            self.assertNotIn("[Linux]", md)

    def test_17_category_rotation_order_and_4os(self):
        mgr = CatalogManager(
            categories_path=Path("data/categories.json"),
            catalog_path=Path("data/catalog.json"),
            content_dir=Path(tempfile.mkdtemp()),
        )
        self.assertEqual(len(mgr.categories), 17)
        self.assertEqual(len(mgr.catalog), 17)
        cat_nums = [int(item["cat_num"]) for item in mgr.select_next_articles(count=17)]
        self.assertEqual(cat_nums, list(range(1, 18)))
        self.assertEqual(mgr.get_next_rotation_cat_nums(count=3), [1, 2, 3])
        for item in mgr.catalog:
            self.assertIn("Windows・macOS・iOS・Android", item["title"])
            self.assertNotIn("Linux", item["title"])

    def test_site_builder_generates_html_and_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            content_dir = tmp_path / "content"
            docs_dir = tmp_path / "docs"
            readme_path = tmp_path / "README.md"
            content_dir.mkdir()

            sample_md = content_dir / "2026-11-23_art01_pdf_merge_split_compress.md"
            sample_md.write_text(
                "<!-- article_id: art01-pdf-merge-split-compress -->\n\n"
                "# テストPDF記事｜Windows・macOS・iOS・Android\n\n## 4OS比較早見表\n\n| OS | 方法 |\n|---|---|\n| Windows | Edge |\n",
                encoding="utf-8",
            )

            mgr = CatalogManager(
                categories_path=Path("data/categories.json"),
                catalog_path=Path("data/catalog.json"),
                content_dir=content_dir,
            )
            built = build_github_pages(mgr, docs_dir=docs_dir, readme_path=readme_path)
            self.assertTrue((docs_dir / "index.html").exists())
            self.assertTrue((docs_dir / "articles" / "art01-pdf-merge-split-compress.html").exists())
            self.assertTrue(readme_path.exists())
            index_txt = (docs_dir / "index.html").read_text(encoding="utf-8")
            readme_txt = readme_path.read_text(encoding="utf-8")
            self.assertIn("Windows・macOS・iOS・Android", index_txt)
            self.assertNotIn("Linux", index_txt)
            self.assertNotIn("Linux", readme_txt)
            self.assertGreaterEqual(len(built), 3)

    def test_hatena_mailer_format_mime_and_daily_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            md_file = tmp_path / "2026-11-23_art01_pdf_merge_split_compress.md"
            md_file.write_text(
                "<!-- article_id: art01-pdf-merge-split-compress -->\n\n"
                "# テストタイトル｜Windows・macOS・iOS・Android\n\n"
                "導入テキスト\n\n## 4OS比較早見表\n\n| OS | 方法 |\n|---|---|\n| Windows | Edge |\n",
                encoding="utf-8",
            )
            png_file = md_file.with_suffix(".png")
            Image.new("RGB", (768, 512), color=(10, 40, 80)).save(png_file, format="PNG")

            item = {"id": "art01-pdf-merge-split-compress", "article_num": 1, "title": "fallback"}
            post = format_markdown_for_hatena(item, md_file, png_file)
            self.assertEqual(post.title, "テストタイトル｜Windows・macOS・iOS・Android")
            self.assertNotIn("<h1>", post.html_body)
            self.assertIn("<table", post.html_body)

            cfg = AppConfig(
                ollama_host="http://localhost:11434",
                planner_model="qwen3.5:9b",
                writer_model="gemma4:12b",
                draw_things_host="http://localhost:7860",
                image_width=768,
                image_height=512,
                image_steps=16,
                image_guidance_scale=4.0,
                site_base_url="",
                smtp_host="smtp.gmail.com",
                smtp_port=587,
                smtp_user="sender@example.com",
                smtp_password="secret",
                smtp_use_tls=True,
                smtp_use_ssl=False,
                mail_from_name="PC 4OS Guide",
                hatena_post_email="test.blog@hatenablog.com",
                blogger_post_email="secret.test@blogger.com",
            )
            sender = HatenaMailSender(cfg, platform="hatena")
            mime_msg = sender.build_mime_message(post)
            raw_mime = mime_msg.as_string()
            self.assertIn('filename="art01_eyecatch.jpg"', raw_mime)
            self.assertTrue(sender.send_post(post, dry_run=True)["success"])

            blogger_sender = HatenaMailSender(cfg, platform="blogger")
            blogger_html = blogger_sender.sanitize_html_for_blogger(post.html_body)
            self.assertNotIn("<table", blogger_html)
            self.assertNotIn("style=", blogger_html)
            self.assertIn("Windows", blogger_html)
            self.assertTrue(blogger_sender.send_post(post, dry_run=True)["success"])

            hist_mgr = HatenaHistoryManager(history_path=tmp_path / "posted_hatena.json")
            self.assertFalse(hist_mgr.has_posted_today())
            hist_mgr.record_post(post)
            self.assertTrue(hist_mgr.has_posted_today())
            self.assertIn("art01-pdf-merge-split-compress", hist_mgr.posted_ids())


if __name__ == "__main__":
    unittest.main()
