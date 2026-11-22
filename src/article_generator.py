import base64
import json
import logging
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """あなたはWindows・macOS・Linux（Ubuntu系）・iPadOSおよびネットワークに精通したIT技術記事の構成作家（テクニカルエディター）です。
読者の実務や日常のPCトラブルを解決できる、正確で具体的な「4OS実例比較記事」の構成案（アウトライン）を設計してください。

【絶対ルール】
1. 技術的正確性：実在する標準機能、ショートカットキー、コマンド（PowerShell/CMD、macOSターミナル、Ubuntu/bash）、iPadOSの標準アプリ操作のみを記載し、架空のコマンドや存在しないメニューを作らないこと。
2. 4OSすべてを公平かつ具体的に扱うこと（Windows 11 / macOS / Linux(Ubuntu) / iPadOS）。
3. よくある失敗・エラーと解決策（トラブルシューティング）を必ず3つ以上盛り込むこと。
4. 出力は簡潔な箇条書きの構成メモとし、余計な前置きや挨拶を入れないこと。"""

WRITER_SYSTEM_PROMPT = """あなたはGoogle Bloggerおよび技術ブログで高い読了率と検索評価を得るプロのITライターです。
構成案をもとに、初心者にも分かりやすく、中級者にも役立つ実践的な「4OS徹底比較ガイド記事」をMarkdown形式で執筆してください。

【執筆ルール】
1. 以下の見出し構成を必ず守ること：
   - 記事タイトル（`# タイトル` を1行目に1つだけ）
   - 導入文（読者の悩みに共感し、この記事で分かることを簡潔に提示）
   - `## 4OS比較早見表`（Markdownの表形式で Windows / macOS / Linux / iPad を比較）
   - `## 1. Windows での実例手順`（具体的なGUI手順＋必要に応じコマンド例）
   - `## 2. macOS での実例手順`
   - `## 3. Linux（Ubuntu系）での実例手順`（GUIとCLIコマンドの両方または実務的な手順）
   - `## 4. iPad（iPadOS）での実例手順`
   - `## よくあるトラブルと解決チェックリスト`（実際にハマりやすいエラー原因と対処法を3〜4点）
   - `## まとめ：快適なマルチOS環境を作るポイント`（関連する便利な周辺機器・ツールの選び方も自然に紹介）
2. コードやコマンドは必ず適切なコードブロック（```cmd, ```bash, ```powershell など）で囲むこと。
3. メタ発言（「はい、記事を作成します」など）は一切書かず、記事本文のみを出力すること。"""


class ArticleGenerator:
    """
    Dual-LLM Technical Article Generator + Draw Things Illustration Engine:
    - Text LLM (Ollama): http://192.168.128.62:11434 (qwen3.5:9b planner + gemma4:12b writer)
    - Image Gen (Draw Things): http://192.168.128.59:7860 (FLUX.2 klein 4B, 768x512 landscape)
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
        Generates a full 4-OS comparison Markdown article using:
        1. Planner (qwen3.5:9b): technical facts, exact steps, commands, and pitfalls
        2. Writer (gemma4:12b): polished Japanese technical blog post
        Returns (full_markdown, final_title).
        """
        cat_name = article.get("category", "")
        cat_num = article.get("cat_num", 1)
        topic = article.get("task_topic", "")
        title = article.get("title", "")
        keywords = ", ".join(article.get("keywords", []))
        affiliate_hint = (category_meta or {}).get("affiliate_hint", "関連する便利なPC周辺機器やツール")

        logger.info(f"[Planner: {self.planner_model}] Designing technical blueprint for #{article.get('article_num')} ({cat_name})...")
        plan_prompt = (
            f"カテゴリ#{cat_num}: {cat_name}\n"
            f"テーマ: {topic}\n"
            f"想定タイトル: {title}\n"
            f"狙うキーワード: {keywords}\n"
            f"関連ツール・周辺機器のヒント: {affiliate_hint}\n\n"
            "上記テーマについて、Windows 11 / macOS / Linux(Ubuntu系) / iPadOS それぞれでの"
            "「具体的な実例手順（標準機能・コマンド・アプリ名）」「注意点」「よくあるトラブルと解決法3〜4選」"
            "を技術的に正確に整理した構成メモを作成してください。"
        )
        blueprint = self._clean_markdown(
            self._call_ollama_chat(
                model=self.planner_model,
                messages=[
                    {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                    {"role": "user", "content": plan_prompt},
                ],
                temperature=0.35,
                num_predict=2200,
            )
        )

        logger.info(f"[Writer: {self.writer_model}] Writing full 4-OS comparison article...")
        write_prompt = (
            f"以下の構成メモをもとに、ブログ記事の完成原稿（Markdown形式）を執筆してください。\n"
            f"・カテゴリ: #{cat_num} {cat_name}\n"
            f"・推奨タイトル: {title}\n"
            f"・文字数の目安: 2,500〜4,000文字程度（丁寧で実践的、かつ読みやすく）\n"
            f"・まとめでは「{affiliate_hint}」などの導入メリットも読者目線で自然に触れてください。\n\n"
            f"【構成メモ】\n{blueprint}"
        )
        raw_md = self._call_ollama_chat(
            model=self.writer_model,
            messages=[
                {"role": "system", "content": WRITER_SYSTEM_PROMPT},
                {"role": "user", "content": write_prompt},
            ],
            temperature=0.55,
            num_predict=4500,
        )
        body_md = self._clean_markdown(raw_md)

        # Ensure H1 title exists and extract it
        first_line = body_md.splitlines()[0].strip() if body_md.splitlines() else ""
        if first_line.startswith("# "):
            final_title = first_line[2:].strip()
        else:
            final_title = title
            body_md = f"# {final_title}\n\n{body_md}"

        meta_header = (
            f"<!--\n"
            f"article_id: {article.get('id', '')}\n"
            f"article_num: {article.get('article_num', 0)}\n"
            f"cat_num: {cat_num}\n"
            f"category: {cat_name}\n"
            f"planner_model: {self.planner_model}\n"
            f"writer_model: {self.writer_model}\n"
            f"-->\n\n"
        )
        return meta_header + body_md + "\n", final_title

    def generate_image_prompt(
        self,
        article: Dict[str, Any],
        category_meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Uses planner LLM to craft a clean English prompt for Draw Things (FLUX.2 klein 4B)."""
        motif = (category_meta or {}).get(
            "visual_motif",
            "sleek laptop, desktop monitor, and tablet connected by glowing abstract light trails on a clean modern desk",
        )
        topic = article.get("task_topic", article.get("title", ""))
        prompt_req = (
            "Write ONE concise English image-generation prompt (max 65 words) for a modern horizontal 3:2 tech blog header illustration.\n"
            f"Topic: {topic}\n"
            f"Visual motif hint: {motif}\n"
            "Style: clean modern editorial vector-meets-3D isometric tech illustration, bright crisp daylight studio palette (teal, cobalt blue, soft coral accents), sleek laptop, desktop monitor, Linux workstation, and tablet harmoniously arranged on a minimal desk.\n"
            "STRICT RULE: Explicitly avoid any text, letters, logos, brand names, watermarks, or UI words. Output ONLY the English prompt."
        )
        try:
            en_prompt = self._clean_markdown(
                self._call_ollama_chat(
                    model=self.planner_model,
                    messages=[
                        {"role": "system", "content": "You are an expert prompt engineer for FLUX.2 image generation. Output only a single clean English prompt without quotes or explanations."},
                        {"role": "user", "content": prompt_req},
                    ],
                    temperature=0.5,
                    num_predict=180,
                    timeout=120,
                )
            )
            en_prompt = re.sub(r"\s+", " ", en_prompt).strip().strip('"').strip("'")
            if len(en_prompt) >= 20:
                return f"{en_prompt}, ultra-clean modern tech blog header illustration, crisp lighting, high detail, no text, no letters, no watermark"
        except Exception as e:
            logger.warning(f"Falling back to template image prompt: {e}")

        return (
            f"Modern editorial tech blog header illustration showing {motif}, "
            "sleek laptop, desktop display, and tablet on a clean minimalist workspace desk, "
            "soft teal and cobalt blue studio lighting, isometric digital art style, crisp detail, "
            "no text, no letters, no logos, no watermark"
        )

    def generate_illustration(
        self,
        article: Dict[str, Any],
        output_image_path: Path,
        category_meta: Optional[Dict[str, Any]] = None,
        custom_prompt: Optional[str] = None,
    ) -> Tuple[Optional[Path], str]:
        """Generates a 768x512 landscape tech blog eyecatch via Draw Things HTTP API."""
        dt = self.check_draw_things_connection()
        if not dt.get("online"):
            logger.warning(f"Draw Things ({self.draw_things_host}) is offline: {dt.get('error')}")
            return None, ""

        en_prompt = custom_prompt.strip() if custom_prompt else self.generate_image_prompt(article, category_meta)
        logger.info(
            f"[Draw Things: {self.draw_things_host} ({dt.get('model')})] "
            f"Generating {self.image_width}x{self.image_height} eyecatch..."
        )

        payload = {
            "prompt": en_prompt,
            "negative_prompt": (
                "text, words, letters, typography, alphabet, numbers, kanji, japanese text, chinese characters, "
                "logo, brand mark, apple logo, windows logo, watermark, signature, caption, label, UI text, "
                "blurry, lowres, messy clutter, dark gloomy shadows, distorted screens, ugly, deformed"
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
                    img_bytes = base64.b64decode(b64_str)
                    output_image_path.parent.mkdir(parents=True, exist_ok=True)
                    output_image_path.write_bytes(img_bytes)
                    elapsed = time.time() - start_t
                    logger.info(f"Saved eyecatch: {output_image_path} ({len(img_bytes)} bytes in {elapsed:.1f}s)")
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
            "PC作業をWindows・macOS・Linux・iPadの4OSで実例比較するブログの新しい記事テーマをJSON配列で生成してください。\n"
            "既存テーマと重複しない、検索需要が高くトラブル解決に役立つ実践テーマにしてください。\n\n"
            f"【生成するスロット】\n" + "\n".join(requested_lines) + "\n\n"
            f"【既存テーマ（重複禁止）】\n" + "\n".join(existing_topics) + "\n\n"
            "【出力形式】JSON配列のみ出力（Markdownコードフェンス不要）。各要素のキー:\n"
            '{"id": "artXX-short-english-slug", "article_num": 数値, "cat_num": 数値, "category": "カテゴリ名", '
            '"task_topic": "具体的な作業内容", "title": "【4OS徹底比較】...｜Windows・macOS・Linux・iPad", "keywords": ["kw1", "kw2", "kw3"]}'
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
