import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.article_generator import compose_title_card
from src.catalog_manager import CatalogManager
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


if __name__ == "__main__":
    unittest.main()
