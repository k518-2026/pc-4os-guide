import io
import json
import logging
import os
import re
import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import markdown

from src.catalog_manager import CatalogManager
from src.config import AppConfig

JST = timezone(timedelta(hours=9))
logger = logging.getLogger(__name__)


@dataclass
class HatenaFormattedPost:
    article_id: str
    article_num: int
    title: str
    html_body: str
    plain_body: str
    md_path: Path
    image_path: Optional[Path]


class HatenaHistoryManager:
    """Tracks articles already emailed to Hatena Blog (`data/posted_hatena.json`)."""

    def __init__(self, history_path: Path = Path("data/posted_hatena.json")):
        self.history_path = Path(history_path)
        self.records: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if not self.history_path.exists():
            return []
        try:
            data = json.loads(self.history_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Failed to read {self.history_path}: {e}")
            return []

    def save(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(
            json.dumps(self.records, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def posted_ids(self) -> set:
        return {r.get("article_id", "") for r in self.records if r.get("article_id")}

    def has_posted_today(self, now: Optional[datetime] = None) -> bool:
        today_str = (now or datetime.now(JST)).strftime("%Y-%m-%d")
        return any(str(r.get("posted_at", ""))[:10] == today_str for r in self.records)

    def record_post(self, post: HatenaFormattedPost, now: Optional[datetime] = None) -> None:
        ts = (now or datetime.now(JST)).isoformat()
        self.records.append(
            {
                "article_id": post.article_id,
                "article_num": post.article_num,
                "title": post.title,
                "md_path": str(post.md_path).replace("\\", "/"),
                "posted_at": ts,
            }
        )
        self.save()


def format_markdown_for_hatena(
    item: Dict[str, Any],
    md_path: Path,
    image_path: Optional[Path] = None,
) -> HatenaFormattedPost:
    """
    Converts a stocked Markdown article into a clean HTML email suitable for
    Hatena Blog's '見たままモード' email posting (title goes in Subject, body skips duplicate H1).
    """
    raw_md = md_path.read_text(encoding="utf-8", errors="ignore")
    clean_md = re.sub(r"^\s*<!--.*?-->\s*", "", raw_md, count=1, flags=re.DOTALL).strip()

    lines = clean_md.splitlines()
    title = item.get("title", item["id"])
    body_lines = lines
    if lines and lines[0].strip().startswith("# "):
        title = lines[0].strip()[2:].strip()
        body_lines = lines[1:]

    body_md = "\n".join(body_lines).strip()
    html_body = markdown.markdown(
        body_md,
        extensions=["tables", "fenced_code", "nl2br"],
    )

    # Lightweight inline styles so tables and code blocks render cleanly in Hatena Blog
    html_body = html_body.replace(
        "<table>",
        '<table style="border-collapse:collapse;width:100%;margin:16px 0;font-size:14px;">',
    )
    html_body = html_body.replace(
        "<th>",
        '<th style="border:1px solid #cbd5e1;padding:8px;background:#f1f5f9;text-align:left;">',
    )
    html_body = html_body.replace(
        "<td>",
        '<td style="border:1px solid #cbd5e1;padding:8px;vertical-align:top;">',
    )
    html_body = html_body.replace(
        "<pre>",
        '<pre style="background:#0f172a;color:#e2e8f0;padding:12px;border-radius:6px;overflow-x:auto;font-size:13px;">',
    )

    return HatenaFormattedPost(
        article_id=item["id"],
        article_num=int(item.get("article_num", 0)),
        title=title,
        html_body=html_body,
        plain_body=body_md,
        md_path=md_path,
        image_path=image_path if (image_path and image_path.exists()) else None,
    )


def select_next_article_for_hatena(
    catalog_mgr: CatalogManager,
    history_mgr: HatenaHistoryManager,
    article_id: Optional[str] = None,
    force: bool = False,
) -> Optional[HatenaFormattedPost]:
    stocked = catalog_mgr.get_stocked_articles()
    posted = history_mgr.posted_ids()

    for entry in sorted(stocked, key=lambda e: int(e["item"].get("article_num", 99999))):
        item = entry["item"]
        if article_id:
            if item["id"] != article_id:
                continue
            if item["id"] in posted and not force:
                logger.info(f"Article '{article_id}' was already posted to Hatena Blog (use --force to repost).")
                return None
            return format_markdown_for_hatena(item, entry["md_path"], entry["img_path"])
        if item["id"] not in posted:
            return format_markdown_for_hatena(item, entry["md_path"], entry["img_path"])

    return None


class HatenaMailSender:
    """Sends a formatted article + ASCII-named JPEG eyecatch to Hatena Blog via SMTP."""

    def __init__(self, config: AppConfig):
        self.config = config

    @staticmethod
    def _compress_image_jpeg(path: Path, max_bytes: int = 180_000) -> Tuple[bytes, str]:
        raw = path.read_bytes()
        try:
            from PIL import Image

            img = Image.open(io.BytesIO(raw)).convert("RGB")
            for quality in (86, 78, 68, 56):
                buf = io.BytesIO()
                img.save(buf, "JPEG", quality=quality, optimize=True)
                if buf.tell() <= max_bytes:
                    return buf.getvalue(), "jpeg"
            return buf.getvalue(), "jpeg"
        except Exception as e:
            logger.warning(f"Pillow JPEG conversion failed ({e}); attaching raw PNG.")
            return raw, "png"

    def build_mime_message(self, post: HatenaFormattedPost) -> MIMEMultipart:
        attach_img = (
            post.image_path is not None
            and post.image_path.exists()
            and os.getenv("ATTACH_IMAGE_HATENA", "true").strip().lower() in ("1", "true", "yes")
        )

        if attach_img:
            msg = MIMEMultipart("mixed")
            alt_part = MIMEMultipart("alternative")
            msg.attach(alt_part)
        else:
            msg = MIMEMultipart("alternative")
            alt_part = msg

        msg["Subject"] = Header(post.title, "utf-8")
        try:
            self.config.mail_from_name.encode("ascii")
            from_display = self.config.mail_from_name
        except UnicodeEncodeError:
            from_display = Header(self.config.mail_from_name, "utf-8").encode()
        msg["From"] = f"{from_display} <{self.config.smtp_user}>"
        msg["To"] = self.config.hatena_post_email
        msg["Date"] = formatdate(localtime=True)

        alt_part.attach(MIMEText(post.plain_body, "plain", "utf-8"))
        alt_part.attach(MIMEText(post.html_body, "html", "utf-8"))

        if attach_img and post.image_path is not None:
            img_bytes, subtype = self._compress_image_jpeg(post.image_path)
            ext = "jpg" if subtype == "jpeg" else "png"
            # Strictly ASCII filename (Hatena Blog email posting can fail on Japanese filenames)
            ascii_name = f"art{post.article_num:02d}_eyecatch.{ext}"
            img_part = MIMEImage(img_bytes, _subtype=subtype)
            img_part.add_header("Content-Disposition", "attachment", filename=ascii_name)
            msg.attach(img_part)

        return msg

    def send_post(self, post: HatenaFormattedPost, dry_run: bool = False) -> Dict[str, Any]:
        if dry_run:
            logger.info(
                f"[DRY-RUN] Would email '{post.title}' ({post.article_id}) to "
                f"'{self.config.hatena_post_email or '(HATENA_POST_EMAIL unset)'}'"
            )
            return {"success": True, "dry_run": True}

        if not self.config.hatena_post_email:
            return {"success": False, "error": "HATENA_POST_EMAIL is not configured."}
        if not self.config.smtp_user or not self.config.smtp_password:
            return {"success": False, "error": "SMTP_USER or SMTP_PASSWORD is not configured."}

        msg = self.build_mime_message(post)
        try:
            context = ssl.create_default_context()
            if self.config.smtp_use_ssl or self.config.smtp_port == 465:
                with smtplib.SMTP_SSL(self.config.smtp_host, self.config.smtp_port, context=context, timeout=30) as server:
                    server.login(self.config.smtp_user, self.config.smtp_password)
                    server.sendmail(self.config.smtp_user, [self.config.hatena_post_email], msg.as_string())
            else:
                with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port, timeout=30) as server:
                    server.ehlo()
                    if self.config.smtp_use_tls:
                        server.starttls(context=context)
                        server.ehlo()
                    server.login(self.config.smtp_user, self.config.smtp_password)
                    server.sendmail(self.config.smtp_user, [self.config.hatena_post_email], msg.as_string())
            logger.info(f"Successfully emailed '{post.title}' to Hatena Blog!")
            return {"success": True, "dry_run": False}
        except Exception as e:
            return {"success": False, "error": str(e)}
