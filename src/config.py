import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = val


@dataclass
class AppConfig:
    ollama_host: str
    planner_model: str
    writer_model: str
    draw_things_host: str
    image_width: int
    image_height: int
    image_steps: int
    image_guidance_scale: float
    site_base_url: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_use_tls: bool
    smtp_use_ssl: bool
    mail_from_name: str
    hatena_post_email: str
    blogger_post_email: str


def get_config() -> AppConfig:
    """Load configuration from environment variables with local LAN and SMTP defaults."""
    smtp_user = os.getenv("SMTP_USER", "").strip()
    raw_smtp_host = os.getenv("SMTP_HOST", "").strip()
    if raw_smtp_host:
        smtp_host = raw_smtp_host
    elif any(smtp_user.lower().endswith(d) for d in ("@outlook.com", "@hotmail.com", "@live.com", "@outlook.jp")):
        smtp_host = "smtp-mail.outlook.com"
    else:
        smtp_host = "smtp.gmail.com"

    return AppConfig(
        ollama_host=os.getenv("OLLAMA_HOST", "http://192.168.128.62:11434").strip().rstrip("/"),
        planner_model=os.getenv("OLLAMA_PLANNER_MODEL", "qwen3.5:9b").strip(),
        writer_model=os.getenv("OLLAMA_WRITER_MODEL", "gemma4:12b").strip(),
        draw_things_host=os.getenv("DRAW_THINGS_HOST", "http://192.168.128.59:7860").strip().rstrip("/"),
        image_width=int(os.getenv("IMAGE_WIDTH", "768")),
        image_height=int(os.getenv("IMAGE_HEIGHT", "512")),
        image_steps=int(os.getenv("IMAGE_STEPS", "16")),
        image_guidance_scale=float(os.getenv("IMAGE_GUIDANCE_SCALE", "4.0")),
        site_base_url=os.getenv("SITE_BASE_URL", "https://k518-2026.github.io/pc-4os-guide/").strip(),
        smtp_host=smtp_host,
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=smtp_user,
        smtp_password=os.getenv("SMTP_PASSWORD", "").strip(),
        smtp_use_tls=os.getenv("SMTP_USE_TLS", "true").strip().lower() in ("true", "1", "yes"),
        smtp_use_ssl=os.getenv("SMTP_USE_SSL", "false").strip().lower() in ("true", "1", "yes"),
        mail_from_name=os.getenv("MAIL_FROM_NAME", "PC 4OS Guide Publisher").strip(),
        hatena_post_email=os.getenv("HATENA_POST_EMAIL", "").strip(),
        blogger_post_email=os.getenv("BLOGGER_POST_EMAIL", "").strip(),
    )
