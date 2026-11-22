import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class CatalogManager:
    """Manages the 17-category rotation catalog and stocked content files."""

    def __init__(
        self,
        categories_path: Path = Path("data/categories.json"),
        catalog_path: Path = Path("data/catalog.json"),
        content_dir: Path = Path("content"),
    ):
        self.categories_path = Path(categories_path)
        self.catalog_path = Path(catalog_path)
        self.content_dir = Path(content_dir)
        self.categories: List[Dict[str, Any]] = self._load_json(self.categories_path)
        self.catalog: List[Dict[str, Any]] = self._load_json(self.catalog_path)

    @staticmethod
    def _load_json(path: Path) -> List[Dict[str, Any]]:
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []

    def save_catalog(self) -> None:
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.catalog_path.write_text(
            json.dumps(self.catalog, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def get_category_by_num(self, cat_num: int) -> Optional[Dict[str, Any]]:
        for c in self.categories:
            if int(c.get("cat_num", 0)) == int(cat_num):
                return c
        return None

    def find_stock_file(self, article_id: str) -> Optional[Path]:
        if not self.content_dir.exists():
            return None
        safe_id = article_id.replace("-", "_")
        matches = sorted(self.content_dir.glob(f"*{safe_id}.md"))
        if matches:
            return matches[-1]
        matches_dash = sorted(self.content_dir.glob(f"*{article_id}.md"))
        return matches_dash[-1] if matches_dash else None

    def get_stocked_articles(self) -> List[Dict[str, Any]]:
        results = []
        for item in self.catalog:
            sf = self.find_stock_file(item["id"])
            if sf is not None:
                results.append(
                    {
                        "item": item,
                        "md_path": sf,
                        "img_path": sf.with_suffix(".png") if sf.with_suffix(".png").exists() else None,
                    }
                )
        return results

    def get_unstocked_articles(self, cat_num: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Returns unstocked articles ordered by article_num (which follows the 1..17 category rotation).
        Optionally filters by a specific cat_num (1..17).
        """
        unstocked = []
        for item in sorted(self.catalog, key=lambda x: int(x.get("article_num", 99999))):
            if cat_num is not None and int(item.get("cat_num", 0)) != int(cat_num):
                continue
            if self.find_stock_file(item["id"]) is None:
                unstocked.append(item)
        return unstocked

    def select_next_articles(self, count: int = 1, cat_num: Optional[int] = None) -> List[Dict[str, Any]]:
        return self.get_unstocked_articles(cat_num=cat_num)[:count]

    def get_next_rotation_cat_nums(self, count: int = 1) -> List[int]:
        """Determines the next category numbers (1..17) in strict rotation after the current catalog."""
        total_cats = len(self.categories) or 17
        if not self.catalog:
            last_cat = 0
        else:
            last_cat = int(self.catalog[-1].get("cat_num", 0))
        result = []
        curr = last_cat
        for _ in range(count):
            curr = (curr % total_cats) + 1
            result.append(curr)
        return result

    def append_articles(self, new_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        existing_ids = {item["id"] for item in self.catalog}
        max_num = max((int(item.get("article_num", 0)) for item in self.catalog), default=0)
        added = []
        for item in new_items:
            if not item.get("id") or item["id"] in existing_ids:
                continue
            max_num += 1
            item["article_num"] = max_num
            self.catalog.append(item)
            existing_ids.add(item["id"])
            added.append(item)
        if added:
            self.save_catalog()
        return added
