import json
import tempfile
import unittest
from pathlib import Path

from src.catalog_manager import CatalogManager
from src.site_builder import build_github_pages


class TestPC4OSGuide(unittest.TestCase):
    def test_17_category_rotation_order(self):
        mgr = CatalogManager(
            categories_path=Path("data/categories.json"),
            catalog_path=Path("data/catalog.json"),
            content_dir=Path(tempfile.mkdtemp()),
        )
        self.assertEqual(len(mgr.categories), 17)
        self.assertEqual(len(mgr.catalog), 17)
        # First round covers categories 1..17 in order
        cat_nums = [int(item["cat_num"]) for item in mgr.select_next_articles(count=17)]
        self.assertEqual(cat_nums, list(range(1, 18)))
        # Next rotation wraps cleanly back to 1, 2, 3
        self.assertEqual(mgr.get_next_rotation_cat_nums(count=3), [1, 2, 3])

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
                "# テストPDF記事\n\n## 4OS比較早見表\n\n| OS | 方法 |\n|---|---|\n| Windows | Edge |\n",
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
            self.assertIn("テストPDF記事", (docs_dir / "index.html").read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(built), 3)


if __name__ == "__main__":
    unittest.main()
