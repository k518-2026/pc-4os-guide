import base64
import io
import json
import logging
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.reference_verifier import format_references_markdown, get_verified_references

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """あなたはWindows 11・macOS・iOS（iPhone/iPad）・Androidおよびネットワークに精通したIT技術記事の構成作家（テクニカルエディター）です。
初心者から中級者の日常・仕事のPC＆スマホトラブルを解決できる、正確で分かりやすい「4OS実例比較記事」の構成案（アウトライン）を設計してください。

【ハルシネーション厳禁ルール】
1. 実在する標準機能・ショートカットキー・公式アプリ操作のみを記載すること（Linuxは対象外）。
2. 確証がないメニュー階層や架空の設定項目を絶対に作らないこと。標準機能に無いことは「標準機能では非対応（代替手段は〇〇）」と正直に明記すること。
3. 4OSすべてを公平かつ具体的に扱うこと（Windows 11 / macOS / iOS / Android）。Androidは機種（Pixel / Galaxy等）による名称差にも配慮すること。
4. よくある失敗・エラーと解決策（トラブルシューティング）を必ず3つ以上盛り込むこと。
5. 出力は簡潔な箇条書きの構成メモとし、余計な前置きや挨拶を入れないこと。"""

WRITER_SYSTEM_PROMPT = """あなたはGoogle Bloggerおよび技術ブログで高い読了率と検索評価を得るプロのITライターです。
構成案と公式ドキュメント情報をもとに、初心者にも分かりやすく実践的な「4OS徹底比較ガイド記事」をMarkdown形式で執筆してください。

【執筆ルール】
1. 以下の見出し構成を必ず守ること：
   - 記事タイトル（`# タイトル` を1行目に1つだけ）
   - 導入文（読者の悩みに共感し、この記事で分かることを簡潔に提示）
   - `## 4OS比較早見表`（Markdownの表形式で Windows / macOS / iOS / Android を比較）
   - `## 1. Windows 11 での実例手順`（具体的なGUI手順）
   - `## 2. macOS での実例手順`
   - `## 3. iOS（iPhone / iPad）での実例手順`
   - `## 4. Android での実例手順`
   - `## よくあるトラブルと解決チェックリスト`（実際にハマりやすいエラー原因と対処法を3〜4点）
   - `## まとめ：快適なマルチOS環境を作るポイント`（関連する便利な周辺機器・ツールの選び方も自然に紹介）
2. 存在しないメニュー項目や設定名を創作しないこと。標準機能でできないことは正直に「標準機能のみでは制限あり」と明記し、公式推奨アプリ・ツール（PowerToys、ショートカットアプリ、Google公式アプリ等）を案内すること。
3. 参考文献セクションはシステム側で実在検証済みURLを自動追記するため、本文中に架空のURLを捏造しないこと。
4. メタ発言（「はい、記事を作成します」など）は一切書かず、記事本文のみを出力すること。"""


def _hex_to_rgb(hex_color: str, fallback: Tuple[int, int, int] = (2, 132, 199)) -> Tuple[int, int, int]:
    h = (hex_color or "").strip().lstrip("#")
    if len(h) == 6:
        try:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        except ValueError:
            pass
    return fallback


def _load_jp_font(size: int, bold: bool = True):
    from PIL import ImageFont

    candidates = (
        [
            r"C:\Windows\Fonts\BIZ-UDGothicB.ttc",
            r"C:\Windows\Fonts\YuGothB.ttc",
            r"C:\Windows\Fonts\meiryob.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        ]
        if bold
        else [
            r"C:\Windows\Fonts\BIZ-UDGothicR.ttc",
            r"C:\Windows\Fonts\YuGothM.ttc",
            r"C:\Windows\Fonts\meiryo.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    )
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_japanese_text(draw, text: str, font, max_width: int, max_lines: int = 3) -> List[str]:
    lines: List[str] = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = ch
            if len(lines) >= max_lines - 1:
                break
    if current:
        # Append remaining characters if we stopped early, ellipsizing if needed
        consumed = sum(len(l) for l in lines)
        rem = text[consumed:]
        while rem:
            bbox = draw.textbbox((0, 0), rem, font=font)
            if bbox[2] - bbox[0] <= max_width:
                lines.append(rem)
                break
            rem = rem[:-1]
            if len(rem) <= 2:
                lines.append(rem + "…")
                break
            if draw.textbbox((0, 0), rem + "…", font=font)[2] <= max_width:
                lines.append(rem + "…")
                break
    return lines[:max_lines]


def compose_title_card(
    raw_image_bytes: bytes,
    article: Dict[str, Any],
    category_meta: Optional[Dict[str, Any]] = None,
) -> bytes:
    """
    Overlays a sleek, publication-grade Japanese title banner on top of the
    topic-specific Draw Things background artwork (768x512) so every article has
    a visually distinct, 100%-readable blog title image.
    """
    from PIL import Image, ImageDraw

    base = Image.open(io.BytesIO(raw_image_bytes)).convert("RGBA")
    w, h = base.size

    accent = _hex_to_rgb((category_meta or {}).get("accent_hex", "#0284C7"))
    cat_num = int(article.get("cat_num", 1))
    art_num = int(article.get("article_num", 1))
    short_cat = (category_meta or {}).get("short_name") or article.get("category", "PCガイド")

    # Clean display title (strip redundant prefix/suffix so title pops cleanly)
    raw_title = (article.get("title") or article.get("task_topic") or "").strip()
    display_title = re.sub(r"^【4OS徹底比較】\s*", "", raw_title)
    display_title = re.sub(r"\s*[｜|]\s*Windows.*$", "", display_title).strip()
    if not display_title:
        display_title = raw_title

    # Create smooth dark gradient scrim (stronger on left & bottom for crisp typography, clear on right to showcase art)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for x in range(w):
        # Left 58% gets rich slate backdrop fading smoothly to transparent on the right
        t = min(1.0, max(0.0, 1.0 - (x / (w * 0.72))))
        alpha = int(225 * (t ** 1.35))
        odraw.line([(x, 0), (x, h)], fill=(12, 18, 32, alpha))
    for y in range(int(h * 0.55), h):
        t = min(1.0, max(0.0, (y - h * 0.55) / (h * 0.45)))
        alpha = int(165 * (t ** 1.5))
        odraw.line([(0, y), (w, y)], fill=(10, 15, 28, alpha))

    # Top accent bar
    odraw.rectangle([(0, 0), (w, 7)], fill=(*accent, 255))

    composed = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(composed)

    pad_x = 34
    max_text_w = int(w * 0.60)

    # Top pill: Category + Article Number
    font_badge = _load_jp_font(17, bold=True)
    badge_text = f"#{art_num:02d}  分類{cat_num:02d}｜{short_cat}"
    bb = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = (bb[2] - bb[0]) + 28
    bh = (bb[3] - bb[1]) + 14
    badge_y = 34
    draw.rounded_rectangle(
        [(pad_x, badge_y), (pad_x + bw, badge_y + bh)],
        radius=16,
        fill=(*accent, 240),
    )
    draw.text((pad_x + 14, badge_y + 5), badge_text, font=font_badge, fill=(255, 255, 255, 255))

    # Main Japanese Title
    font_title = _load_jp_font(34, bold=True)
    title_lines = _wrap_japanese_text(draw, display_title, font_title, max_width=max_text_w, max_lines=3)
    ty = badge_y + bh + 28
    line_gap = 12
    for line in title_lines:
        # Subtle drop shadow
        draw.text((pad_x + 2, ty + 2), line, font=font_title, fill=(0, 0, 0, 180))
        draw.text((pad_x, ty), line, font=font_title, fill=(255, 255, 255, 255))
        lb = draw.textbbox((0, 0), line, font=font_title)
        ty += (lb[3] - lb[1]) + line_gap

    # Subtitle label
    font_sub = _load_jp_font(16, bold=False)
    sub_text = "4OS 実例比較 ＆ 公式ドキュメント検証ガイド"
    draw.text((pad_x, ty + 10), sub_text, font=font_sub, fill=(203, 213, 225, 240))

    # Bottom 4-OS Pills
    os_pills = [
        ("Windows", (0, 120, 212)),
        ("macOS", (71, 85, 105)),
        ("iOS", (14, 165, 233)),
        ("Android", (22, 163, 74)),
    ]
    font_os = _load_jp_font(15, bold=True)
    px = pad_x
    py = h - 58
    for label, col in os_pills:
        ob = draw.textbbox((0, 0), label, font=font_os)
        ow = (ob[2] - ob[0]) + 22
        oh = 30
        draw.rounded_rectangle([(px, py), (px + ow, py + oh)], radius=8, fill=(*col, 230))
        draw.text((px + 11, py + 5), label, font=font_os, fill=(255, 255, 255, 255))
        px += ow + 10

    out_buf = io.BytesIO()
    composed.convert("RGB").save(out_buf, format="PNG", optimize=True)
    return out_buf.getvalue()


class ArticleGenerator:
    """
    Dual-LLM Technical Article Generator + Topic-Faithful Title Image Engine:
    - Text LLM (Ollama): http://192.168.128.62:11434 (qwen3.5:9b planner + gemma4:12b writer)
    - Image Gen (Draw Things): http://192.168.128.59:7860 (FLUX.2 klein 4B, 768x512) + Pillow Title Card
    - References: Live HTTP-verified official docs (Microsoft, Apple, Ubuntu, CLI manuals)
    """

    def __init__(
        self,
        ollama_host: str = "http://192.168.128.62:11434",
        planner_model: str = "qwen3.5:9b",
        writer_model: str = "gemma4:12b",
        draw_things_host: str = "http://192.168.128.59:7860",
        image_width: int = 768,
        image_height: int = 512,
        image_steps: int = 16,
        image_guidance_scale: float = 4.0,
    ):
        self.ollama_host = ollama_host.rstrip("/")
        self.planner_model = planner_model
        self.writer_model = writer_model
        self.draw_things_host = draw_things_host.rstrip("/")
        self.image_width = image_width
        self.image_height = image_height
        self.image_steps = image_steps
        self.image_guidance_scale = image_guidance_scale

    def check_ollama_connection(self) -> Dict[str, Any]:
        url = f"{self.ollama_host}/api/tags"
        try:
            with urllib.request.urlopen(url, timeout=5) as res:
                data = json.loads(res.read().decode("utf-8", errors="ignore"))
                models = [m.get("name", "") for m in data.get("models", [])]
                return {"online": True, "host": self.ollama_host, "models": models}
        except Exception as e:
            return {"online": False, "host": self.ollama_host, "error": str(e), "models": []}

    def check_draw_things_connection(self) -> Dict[str, Any]:
        url = f"{self.draw_things_host}/sdapi/v1/options"
        try:
            with urllib.request.urlopen(url, timeout=5) as res:
                data = json.loads(res.read().decode("utf-8", errors="ignore"))
                model = data.get("model") or data.get("sd_model_checkpoint") or "unknown"
                return {"online": True, "host": self.draw_things_host, "model": model}
        except Exception as e:
            return {"online": False, "host": self.draw_things_host, "error": str(e), "model": ""}

    def _call_ollama_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.5,
        num_predict: int = 4096,
        num_ctx: int = 8192,
        timeout: int = 600,
        max_retries: int = 3,
    ) -> str:
        url = f"{self.ollama_host}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
                "num_ctx": num_ctx,
                "repeat_penalty": 1.1,
            },
        }
        last_err: Optional[Exception] = None
        for attempt in range(1, max_retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=timeout) as res:
                    body = json.loads(res.read().decode("utf-8", errors="ignore"))
                    content = (body.get("message", {}).get("content") or "").strip()
                    if content:
                        return content
                    raise RuntimeError(f"Empty response from Ollama ({model})")
            except Exception as e:
                last_err = e
                logger.warning(f"Ollama call ({model}) attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    time.sleep(3 * attempt)
        raise RuntimeError(f"Ollama call ({model}) failed after {max_retries} attempts: {last_err}")

    @staticmethod
    def _clean_markdown(text: str) -> str:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        if text.startswith("```markdown"):
            text = text[len("```markdown"):].strip()
        elif text.startswith("```"):
            text = text[3:].strip()
        if text.endswith("```"):
            text = text[:-3].strip()
        return text.strip()

    def generate_article(
        self,
        article: Dict[str, Any],
        category_meta: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str]:
        """
        Generates a full 4-OS comparison Markdown article with live-verified official references.
        """
        cat_name = article.get("category", "")
        cat_num = int(article.get("cat_num", 1))
        topic = article.get("task_topic", "")
        title = article.get("title", "")
        keywords = ", ".join(article.get("keywords", []))
        affiliate_hint = (category_meta or {}).get("affiliate_hint", "関連する便利なPC周辺機器やツール")

        verified_refs = get_verified_references(cat_num=cat_num, check_live=True)
        refs_context = "\n".join(f"- [{r['os']}] {r['title']} ({r['url']})" for r in verified_refs)

        logger.info(f"[Planner: {self.planner_model}] Designing verified blueprint for #{article.get('article_num')} ({cat_name})...")
        plan_prompt = (
            f"カテゴリ#{cat_num}: {cat_name}\n"
            f"テーマ: {topic}\n"
            f"想定タイトル: {title}\n"
            f"狙うキーワード: {keywords}\n"
            f"関連ツール・周辺機器のヒント: {affiliate_hint}\n"
            f"参照すべき公式ドキュメント:\n{refs_context}\n\n"
            "上記テーマについて、Windows 11 / macOS / iOS / Android それぞれでの"
            "「公式仕様に基づく正確な実例手順（標準機能・公式アプリ名）」「標準機能の制限事項」「よくあるトラブルと解決法3〜4選」"
            "を整理した構成メモを作成してください。架空のメニューや存在しない設定項目は絶対に書かないこと。"
        )
        blueprint = self._clean_markdown(
            self._call_ollama_chat(
                model=self.planner_model,
                messages=[
                    {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                    {"role": "user", "content": plan_prompt},
                ],
                temperature=0.3,
                num_predict=2200,
            )
        )

        logger.info(f"[Writer: {self.writer_model}] Writing full 4-OS comparison article...")
        write_prompt = (
            f"以下の構成メモをもとに、ブログ記事の完成原稿（Markdown形式）を執筆してください。\n"
            f"・カテゴリ: #{cat_num} {cat_name}\n"
            f"・推奨タイトル: {title}\n"
            f"・文字数の目安: 2,500〜4,000文字程度（丁寧で実践的、かつ読みやすく）\n"
            f"・まとめでは「{affiliate_hint}」などの導入メリットも読者目線で自然に触れてください。\n"
            f"・参考文献セクションは後段で公式URLを自動追記するため、本文中に架空のURLを書かないでください。\n\n"
            f"【構成メモ】\n{blueprint}"
        )
        raw_md = self._call_ollama_chat(
            model=self.writer_model,
            messages=[
                {"role": "system", "content": WRITER_SYSTEM_PROMPT},
                {"role": "user", "content": write_prompt},
            ],
            temperature=0.45,
            num_predict=4500,
        )
        body_md = self._clean_markdown(raw_md)

        first_line = body_md.splitlines()[0].strip() if body_md.splitlines() else ""
        if first_line.startswith("# "):
            final_title = first_line[2:].strip()
        else:
            final_title = title
            body_md = f"# {final_title}\n\n{body_md}"

        refs_md = format_references_markdown(verified_refs)
        meta_header = (
            f"<!--\n"
            f"article_id: {article.get('id', '')}\n"
            f"article_num: {article.get('article_num', 0)}\n"
            f"cat_num: {cat_num}\n"
            f"category: {cat_name}\n"
            f"planner_model: {self.planner_model}\n"
            f"writer_model: {self.writer_model}\n"
            f"verified_refs_count: {len(verified_refs)}\n"
            f"-->\n\n"
        )
        full_md = f"{meta_header}{body_md}\n\n{refs_md}".strip() + "\n"
        return full_md, final_title

    def generate_image_prompt(
        self,
        article: Dict[str, Any],
        category_meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Crafts a topic-faithful, visually distinct English background prompt for Draw Things (FLUX.2 klein 4B).
        Composes the main hero visual on the RIGHT side with dark/calm negative space on the LEFT so the
        Japanese title banner overlays cleanly with maximum visual impact.
        """
        motif = (category_meta or {}).get(
            "visual_motif",
            "sleek abstract geometric objects illustrating digital workflow",
        )
        palette = (category_meta or {}).get(
            "palette",
            "rich navy blue, vibrant cyan, and warm gold studio lighting",
        )
        topic = article.get("task_topic", article.get("title", ""))

        prompt_req = (
            "Write ONE vivid, concrete English image-generation prompt (max 60 words) for a 3:2 editorial blog banner background.\n"
            f"Specific topic to depict literally & symbolically: {topic}\n"
            f"Key visual metaphor: {motif}\n"
            f"Color palette & mood: {palette}\n"
            "Composition rule: Place the main hero illustration prominently on the RIGHT half of the frame, leaving calm dark-toned negative space on the LEFT side for a title overlay.\n"
            "STRICT RULES:\n"
            "- Do NOT draw generic laptops/desks unless the topic specifically requires them; focus on the topic's concrete objects/metaphors!\n"
            "- ZERO text, ZERO letters, ZERO numbers, ZERO brand logos, ZERO watermarks.\n"
            "- Output ONLY the English prompt."
        )
        try:
            en_prompt = self._clean_markdown(
                self._call_ollama_chat(
                    model=self.planner_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an art director writing vivid, distinct FLUX.2 image prompts. Output only the single English prompt.",
                        },
                        {"role": "user", "content": prompt_req},
                    ],
                    temperature=0.65,
                    num_predict=180,
                    timeout=120,
                )
            )
            en_prompt = re.sub(r"\s+", " ", en_prompt).strip().strip('"').strip("'")
            if len(en_prompt) >= 20:
                return (
                    f"{en_prompt}, high-craft 3D editorial illustration, dramatic studio lighting, "
                    "sharp focus, rich depth, no text, no letters, no numbers, no logos, no watermark"
                )
        except Exception as e:
            logger.warning(f"Falling back to template image prompt: {e}")

        return (
            f"High-craft 3D editorial illustration depicting {motif}, {palette}, "
            "main subject positioned on the right side with clean dark atmospheric space on the left, "
            "cinematic studio lighting, crisp detail, no text, no letters, no logos, no watermark"
        )

    def generate_illustration(
        self,
        article: Dict[str, Any],
        output_image_path: Path,
        category_meta: Optional[Dict[str, Any]] = None,
        custom_prompt: Optional[str] = None,
        overlay_title: bool = True,
    ) -> Tuple[Optional[Path], str]:
        """
        Generates a 768x512 topic-faithful illustration via Draw Things HTTP API
        and composites a crisp Japanese blog title card over it.
        """
        dt = self.check_draw_things_connection()
        if not dt.get("online"):
            logger.warning(f"Draw Things ({self.draw_things_host}) is offline: {dt.get('error')}")
            return None, ""

        en_prompt = custom_prompt.strip() if custom_prompt else self.generate_image_prompt(article, category_meta)
        logger.info(
            f"[Draw Things: {self.draw_things_host} ({dt.get('model')})] "
            f"Generating {self.image_width}x{self.image_height} topic-faithful artwork..."
        )

        payload = {
            "prompt": en_prompt,
            "negative_prompt": (
                "text, words, letters, typography, alphabet, numbers, kanji, japanese text, chinese characters, "
                "file extensions, badges with text, labels, UI text, logo, brand mark, watermark, signature, "
                "generic empty desk, blurry, lowres, messy clutter, distorted shapes, ugly, deformed"
            ),
            "width": self.image_width,
            "height": self.image_height,
            "steps": self.image_steps,
            "guidance_scale": self.image_guidance_scale,
            "sampler": "Euler A Trailing",
        }
        url = f"{self.draw_things_host}/sdapi/v1/txt2img"
        start_t = time.time()
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=600) as res:
                body = json.loads(res.read().decode("utf-8", errors="ignore"))
                images = body.get("images", [])
                if images and images[0]:
                    b64_str = re.sub(r"^data:image/[^;]+;base64,", "", images[0])
                    raw_bytes = base64.b64decode(b64_str)
                    final_bytes = (
                        compose_title_card(raw_bytes, article=article, category_meta=category_meta)
                        if overlay_title
                        else raw_bytes
                    )
                    output_image_path.parent.mkdir(parents=True, exist_ok=True)
                    output_image_path.write_bytes(final_bytes)
                    elapsed = time.time() - start_t
                    logger.info(
                        f"Saved topic-faithful title eyecatch: {output_image_path} "
                        f"({len(final_bytes)} bytes in {elapsed:.1f}s)"
                    )
                    return output_image_path, en_prompt
        except Exception as e:
            logger.error(f"Draw Things image generation failed: {e}")

        return None, en_prompt

    def generate_new_rotation_themes(
        self,
        existing_catalog: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
        target_cat_nums: List[int],
    ) -> List[Dict[str, Any]]:
        """Auto-generates fresh article themes for the next 17-category rotation round."""
        cat_map = {int(c["cat_num"]): c for c in categories}
        existing_topics = [f"- (cat#{x.get('cat_num')}) {x.get('task_topic')}" for x in existing_catalog[-50:]]
        next_num = max((int(x.get("article_num", 0)) for x in existing_catalog), default=0) + 1

        requested_lines = []
        for idx, cnum in enumerate(target_cat_nums):
            cname = cat_map.get(cnum, {}).get("name", f"Category {cnum}")
            requested_lines.append(f"{idx + 1}. article_num={next_num + idx}, cat_num={cnum}, category=\"{cname}\"")

        prompt = (
            "PC・スマホ作業をWindows・macOS・iOS・Androidの4OSで実例比較する初心者向けブログの新しい記事テーマをJSON配列で生成してください。\n"
            "既存テーマと重複しない、検索需要が高くトラブル解決に役立つ実践テーマにしてください。\n\n"
            f"【生成するスロット】\n" + "\n".join(requested_lines) + "\n\n"
            f"【既存テーマ（重複禁止）】\n" + "\n".join(existing_topics) + "\n\n"
            "【出力形式】JSON配列のみ出力（Markdownコードフェンス不要）。各要素のキー:\n"
            '{"id": "artXX-short-english-slug", "article_num": 数値, "cat_num": 数値, "category": "カテゴリ名", '
            '"task_topic": "具体的な作業内容", "title": "...｜Windows・macOS・iOS・Android", "keywords": ["kw1", "kw2", "kw3"]}'
        )
        raw = self._clean_markdown(
            self._call_ollama_chat(
                model=self.planner_model,
                messages=[
                    {"role": "system", "content": "You output strictly valid JSON arrays for a Japanese tech blog catalog."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
                num_predict=2500,
            )
        )
        match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
        if not match:
            logger.warning("Failed to parse JSON array for new rotation themes.")
            return []
        try:
            items = json.loads(match.group(0))
            return [x for x in items if isinstance(x, dict) and x.get("id") and x.get("title")]
        except Exception as e:
            logger.warning(f"JSON decode failed for new rotation themes: {e}")
            return []
