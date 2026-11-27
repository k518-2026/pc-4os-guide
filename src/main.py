import argparse
import logging
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List

from src.article_generator import ArticleGenerator
from src.catalog_manager import CatalogManager
from src.config import get_config
from src.hatena_mailer import (
    HatenaHistoryManager,
    HatenaMailSender,
    select_next_article_for_hatena,
)
from src.site_builder import build_github_pages

JST = timezone(timedelta(hours=9))
logger = logging.getLogger("pc-4os-guide")


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def print_status_report(catalog_mgr: CatalogManager) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    stocked = catalog_mgr.get_stocked_articles()
    unstocked = catalog_mgr.get_unstocked_articles()
    img_count = sum(1 for x in stocked if x["img_path"] is not None)

    print("\n" + "=" * 78)
    print(" 【PC 4OS実例ガイド（17分類ローテーション）GitHub 書き溜め状況】")
    print("=" * 78)
    print(f"  ・登録カテゴリ数     : {len(catalog_mgr.categories)} 分類（ローテーション運用）")
    print(f"  ・カタログ総記事数   : {len(catalog_mgr.catalog)} 本")
    print(f"  ・生成済み（ストック）: {len(stocked)} 本（うち挿絵あり {img_count} 本）")
    print(f"  ・未生成（待機中）   : {len(unstocked)} 本")
    print("-" * 78)

    if stocked:
        print("\n[OK] 生成済み記事:")
        for entry in stocked:
            it = entry["item"]
            mark = "[画像あり]" if entry["img_path"] else "[画像なし]"
            print(f"  [#{it['article_num']:02d} | 分類{it['cat_num']:02d}] {mark} {it['title']} -> {entry['md_path']}")
    else:
        print("\n[!] まだ生成済みの記事はありません。")

    if unstocked:
        print("\n[NEXT] 次のローテーション執筆予定（先頭5件）:")
        for it in unstocked[:5]:
            print(f"  [#{it['article_num']:02d} | 分類{it['cat_num']:02d}: {it['category']}] {it['id']} : {it['task_topic']}")
    print("=" * 78 + "\n")


def git_sync_and_push(generated_files: List[Path]) -> bool:
    if not generated_files:
        return True
    try:
        subprocess.run(["git", "add", "README.md", "content/", "data/", "docs/"], check=True)
        diff_res = subprocess.run(["git", "diff", "--staged", "--quiet"])
        if diff_res.returncode == 0:
            logger.info("No staged changes to commit.")
            return True

        msg = f"feat(articles): Add {len(generated_files)} PC 4OS guide asset(s) & update GitHub Pages"
        subprocess.run(["git", "commit", "-m", msg], check=True)

        remote_check = subprocess.run(["git", "remote"], capture_output=True, text=True)
        if "origin" not in remote_check.stdout.split():
            logger.warning("Git remote 'origin' is not configured yet. Changes were committed locally.")
            return True

        git_env = {**os.environ, "GIT_EDITOR": "true"}
        subprocess.run(["git", "fetch", "origin", "main"], check=False, env=git_env)
        subprocess.run(["git", "merge", "--no-edit", "-X", "ours", "origin/main"], check=False, env=git_env)
        subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
        logger.info("Successfully pushed articles, illustrations & GitHub Pages to GitHub!")
        return True
    except Exception as e:
        logger.error(f"Git sync/push failed: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PC 4-OS Practical Guide Generator (17-Category Rotation, Ollama + Draw Things -> GitHub)"
    )
    parser.add_argument("-n", "--stock-count", type=int, default=0, help="Generate N articles + illustrations in 17-category rotation")
    parser.add_argument("--category", type=int, default=None, help="Filter/target a specific category number (1..17)")
    parser.add_argument("--article-id", default=None, help="Target a specific article ID from data/catalog.json")
    parser.add_argument("--generate-images", action="store_true", help="Generate missing .png illustrations for existing articles")
    parser.add_argument("--build-pages", action="store_true", help="Rebuild docs/ (GitHub Pages) and README.md")
    parser.add_argument("--push", action="store_true", help="Git commit & push after generation/build")
    parser.add_argument("--status-report", action="store_true", help="Show current stock & rotation status")
    parser.add_argument("--post-hatena", action="store_true", help="Send the next unposted article to Hatena Blog via email")
    parser.add_argument("--post-blogger", action="store_true", help="Send the next unposted article to Google Blogger via email")
    parser.add_argument("--min-interval-hours", type=float, default=0.0, help="Minimum hours required since last post (e.g. 16 for every-16-hours cadence)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate email posting without sending or updating history")
    parser.add_argument("--preview-html", action="store_true", help="Save rendered email HTML to preview_<platform>.html")
    parser.add_argument("--force", action="store_true", help="Force regeneration or override posting interval guard")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()
    setup_logging(args.verbose)

    config = get_config()
    catalog_mgr = CatalogManager()

    if args.post_hatena or args.post_blogger:
        platform = "blogger" if args.post_blogger else "hatena"
        platform_jp = "Google Blogger" if platform == "blogger" else "はてなブログ"
        hist_file = Path("data/posted_blogger.json") if platform == "blogger" else Path("data/posted_hatena.json")
        preview_name = "preview_blogger.html" if platform == "blogger" else "preview_hatena.html"

        blog_history = HatenaHistoryManager(history_path=hist_file)
        if not args.dry_run and not args.force:
            if args.min_interval_hours > 0:
                allowed, elapsed = blog_history.can_post_with_interval(args.min_interval_hours)
                if not allowed:
                    logger.info(
                        f"[{args.min_interval_hours:g}時間間隔ガード] {platform_jp} の前回投稿から "
                        f"{elapsed:.1f}時間しか経過していないため今回はスキップします。"
                    )
                    return
            elif blog_history.has_posted_today():
                today_str = datetime.now(JST).strftime("%Y-%m-%d")
                logger.warning(
                    f"[1日1回安全ガード] 本日 ({today_str} JST) はすでに{platform_jp}へ投稿済みのためスキップします。"
                    "（強制送信する場合は --force を指定してください）"
                )
                return

        post = select_next_article_for_hatena(
            catalog_mgr=catalog_mgr,
            history_mgr=blog_history,
            article_id=args.article_id,
            force=args.force,
        )
        if post is None:
            logger.info(f"No unposted stocked articles available for {platform_jp}.")
            return

        sender = HatenaMailSender(config, platform=platform)
        if args.preview_html or args.dry_run:
            preview_html = (
                sender.sanitize_html_for_blogger(post.html_body)
                if platform == "blogger"
                else post.html_body
            )
            preview_path = Path(preview_name)
            preview_path.write_text(preview_html, encoding="utf-8")
            logger.info(f"Saved {platform_jp} HTML preview: {preview_path.resolve()}")

        res = sender.send_post(post, dry_run=args.dry_run)
        if not res.get("success"):
            logger.error(f"{platform_jp} email dispatch failed: {res.get('error')}")
            sys.exit(1)

        if not args.dry_run:
            blog_history.record_post(post)
            logger.info(f"Recorded {platform_jp} post history for '{post.article_id}' in {blog_history.history_path}")
        return

    if args.status_report:
        print_status_report(catalog_mgr)
        return

    if args.build_pages:
        build_github_pages(catalog_mgr)
        if args.push:
            git_sync_and_push([Path("docs/index.html")])
        print_status_report(catalog_mgr)
        return

    generator = ArticleGenerator(
        ollama_host=config.ollama_host,
        planner_model=config.planner_model,
        writer_model=config.writer_model,
        draw_things_host=config.draw_things_host,
        image_width=config.image_width,
        image_height=config.image_height,
        image_steps=config.image_steps,
        image_guidance_scale=config.image_guidance_scale,
    )

    if args.generate_images:
        dt = generator.check_draw_things_connection()
        if not dt.get("online"):
            logger.error(f"Cannot reach Draw Things at {config.draw_things_host}: {dt.get('error')}")
            sys.exit(1)
        generated_imgs: List[Path] = []
        for entry in catalog_mgr.get_stocked_articles():
            item = entry["item"]
            if args.article_id and item["id"] != args.article_id:
                continue
            img_path = entry["md_path"].with_suffix(".png")
            if img_path.exists() and not args.force:
                continue
            cat_meta = catalog_mgr.get_category_by_num(item["cat_num"])
            saved_img, _ = generator.generate_illustration(item, img_path, category_meta=cat_meta)
            if saved_img:
                generated_imgs.append(saved_img)
                build_github_pages(catalog_mgr)
                if args.push:
                    git_sync_and_push([saved_img])
        print_status_report(catalog_mgr)
        return

    if args.stock_count > 0 or args.article_id:
        ollama_conn = generator.check_ollama_connection()
        if not ollama_conn.get("online"):
            logger.error(f"Cannot reach Ollama at {config.ollama_host}: {ollama_conn.get('error')}")
            sys.exit(1)

        if args.article_id:
            targets = [x for x in catalog_mgr.catalog if x["id"] == args.article_id]
            if not targets:
                logger.error(f"Article ID not found in catalog: {args.article_id}")
                sys.exit(1)
        else:
            targets = catalog_mgr.select_next_articles(count=args.stock_count, cat_num=args.category)
            if len(targets) < args.stock_count:
                shortage = args.stock_count - len(targets)
                next_cats = (
                    [args.category] * shortage
                    if args.category is not None
                    else catalog_mgr.get_next_rotation_cat_nums(count=max(shortage, 3))
                )
                logger.info(f"Replenishing catalog via Ollama for categories {next_cats}...")
                new_items = generator.generate_new_rotation_themes(
                    existing_catalog=catalog_mgr.catalog,
                    categories=catalog_mgr.categories,
                    target_cat_nums=next_cats,
                )
                if new_items:
                    catalog_mgr.append_articles(new_items)
                    targets = catalog_mgr.select_next_articles(count=args.stock_count, cat_num=args.category)

        generated_all: List[Path] = []
        for idx, item in enumerate(targets, start=1):
            existing = catalog_mgr.find_stock_file(item["id"])
            if existing and not args.force:
                logger.info(f"Already exists, skipping: {existing}")
                continue

            cat_meta = catalog_mgr.get_category_by_num(item["cat_num"])
            logger.info(
                f"\n=== [{idx}/{len(targets)}] Generating #{item['article_num']:02d} "
                f"(分類{item['cat_num']:02d}: {item['category']}) ==="
            )
            full_md, final_title = generator.generate_article(item, category_meta=cat_meta)
            today_str = datetime.now(JST).strftime("%Y-%m-%d")
            safe_id = item["id"].replace("-", "_")
            out_md = Path(f"content/{today_str}_{safe_id}.md")
            out_md.parent.mkdir(parents=True, exist_ok=True)
            out_md.write_text(full_md, encoding="utf-8")
            logger.info(f"Saved Markdown: {out_md} ('{final_title}')")

            assets: List[Path] = [out_md]
            out_img = out_md.with_suffix(".png")
            saved_img, _ = generator.generate_illustration(item, out_img, category_meta=cat_meta)
            if saved_img:
                assets.append(saved_img)

            generated_all.extend(assets)
            build_github_pages(catalog_mgr)
            if args.push:
                git_sync_and_push(assets)

        print_status_report(catalog_mgr)
        return

    print_status_report(catalog_mgr)


if __name__ == "__main__":
    main()
