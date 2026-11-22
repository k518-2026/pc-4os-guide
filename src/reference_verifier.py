import logging
import urllib.error
import urllib.request
from typing import Dict, List

logger = logging.getLogger(__name__)

# Curated official documentation pools per category (1..17) for Windows / macOS / iOS / Android
CATEGORY_OFFICIAL_REFS: Dict[int, List[Dict[str, str]]] = {
    1: [
        {"os": "Windows", "title": "Microsoft Edge 印刷・PDF関連ポリシー公式ドキュメント | Microsoft Learn", "url": "https://learn.microsoft.com/ja-jp/deployedge/microsoft-edge-policies#printing"},
        {"os": "macOS", "title": "Macの「プレビュー」でPDFを結合する - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/preview/prvw43696/mac"},
        {"os": "macOS", "title": "Macの「プレビュー」でPDFのサイズを減らす - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/preview/prvw1509/mac"},
        {"os": "iOS", "title": "iPhoneの「ファイル」でファイルやフォルダを変更する - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/iphone/iphc61044c11/ios"},
        {"os": "iOS", "title": "ショートカット ユーザガイド - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/shortcuts/welcome/ios"},
        {"os": "Android", "title": "Google ドライブでドキュメントをスキャンする（PDF保存） - Google ドライブ ヘルプ", "url": "https://support.google.com/drive/answer/3145835?hl=ja"},
        {"os": "Android", "title": "Chrome から印刷（PDF として保存・ページ範囲指定） - Google Chrome ヘルプ", "url": "https://support.google.com/chrome/answer/1069693?hl=ja"},
    ],
    2: [
        {"os": "Windows", "title": "OneDrive に保存されている以前のバージョンのファイルを復元する - Microsoft サポート", "url": "https://support.microsoft.com/ja-jp/office/onedrive-%E3%81%AB%E4%BF%9D%E5%AD%98%E3%81%95%E3%82%8C%E3%81%A6%E3%81%84%E3%82%8B%E4%BB%A5%E5%89%8D%E3%81%AE%E3%83%90%E3%83%BC%E3%82%B8%E3%83%A7%E3%83%B3%E3%81%AE%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%82%92%E5%BE%A9%E5%85%83%E3%81%99%E3%82%8B-159cad6d-d76e-4981-88ef-de6e96c93893"},
        {"os": "Windows", "title": "OneDrive の同期の問題を解決する - Microsoft サポート", "url": "https://support.microsoft.com/ja-jp/office/onedrive-%E3%81%AE%E5%90%8C%E6%9C%9F%E3%81%AE%E5%95%8F%E9%A1%8C%E3%82%92%E8%A7%A3%E6%B1%BA%E3%81%99%E3%82%8B-0899b115-05f7-45ec-95b2-e4cc8c4670b2"},
        {"os": "macOS / 共通", "title": "パソコン版 Google ドライブを使用する - Google ドライブ ヘルプ", "url": "https://support.google.com/drive/answer/10838124?hl=ja"},
        {"os": "iOS", "title": "iPhoneの「ファイル」でファイルやフォルダを変更する - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/iphone/iphc61044c11/ios"},
        {"os": "Android", "title": "Google ドライブにファイルやフォルダをアップロードする - Google ドライブ ヘルプ", "url": "https://support.google.com/drive/answer/2424368?hl=ja"},
        {"os": "Android / 共通", "title": "操作履歴とファイル バージョンを確認する - Google ドライブ ヘルプ", "url": "https://support.google.com/drive/answer/2409045?hl=ja"},
    ],
    3: [
        {"os": "Windows", "title": "Snipping Tool を使ってスクリーンショットをキャプチャする・画面録画する - Microsoft サポート", "url": "https://support.microsoft.com/ja-jp/windows/snipping-tool-%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E3%82%B9%E3%82%AF%E3%83%AA%E3%83%BC%E3%83%B3%E3%82%B7%E3%83%A7%E3%83%83%E3%83%88%E3%82%92%E3%82%AD%E3%83%A3%E3%83%97%E3%83%81%E3%83%A3%E3%81%99%E3%82%8B-00246869-1843-655f-f220-97299b865f6b"},
        {"os": "macOS", "title": "Macでスクリーンショットを撮る - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/102646"},
        {"os": "macOS", "title": "Macで画面を収録する方法 - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/102618"},
        {"os": "iOS", "title": "iPhoneでスクリーンショットを撮る（フルページ保存を含む） - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/iphone/iphc872c0115/ios"},
        {"os": "iOS", "title": "iPhone、iPad、iPod touchで画面を録画する - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/102653"},
        {"os": "Android", "title": "Android デバイスで画面の画像（スクリーンショット）または動画を撮影する - Android ヘルプ", "url": "https://support.google.com/android/answer/9075928?hl=ja"},
    ],
    4: [
        {"os": "Windows", "title": "Image Resizer Windowsのユーティリティ - PowerToys | Microsoft Learn", "url": "https://learn.microsoft.com/ja-jp/windows/powertoys/image-resizer"},
        {"os": "macOS", "title": "Macの「プレビュー」で画像を切り取る/サイズ変更する/回転する - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/preview/prvw2015/mac"},
        {"os": "macOS", "title": "MacのFinderでクイックアクションを実行する（イメージを変換） - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/mac-help/mchl97ff9142/mac"},
        {"os": "iOS", "title": "Apple製のデバイスでHEIF／HEVCメディアを扱う - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/116944"},
        {"os": "iOS", "title": "ショートカット ユーザガイド - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/shortcuts/welcome/ios"},
        {"os": "Android", "title": "写真を編集する - Google フォト ヘルプ", "url": "https://support.google.com/photos/answer/6128850?hl=ja"},
        {"os": "共通", "title": "cwebp | WebP Official Documentation | Google for Developers", "url": "https://developers.google.com/speed/webp/docs/cwebp"},
    ],
}

FALLBACK_OFFICIAL_REFS: List[Dict[str, str]] = [
    {"os": "Windows", "title": "Windows のヘルプとラーニング - Microsoft サポート", "url": "https://support.microsoft.com/ja-jp/windows"},
    {"os": "macOS", "title": "macOS ユーザガイド - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/mac-help/welcome/mac"},
    {"os": "iOS", "title": "iPhoneユーザガイド - Apple サポート (日本)", "url": "https://support.apple.com/ja-jp/guide/iphone/welcome/ios"},
    {"os": "Android", "title": "Android ヘルプ - Google サポート", "url": "https://support.google.com/android/?hl=ja"},
]


def verify_url_live(url: str, timeout: int = 8) -> bool:
    """Checks that an official documentation URL resolves cleanly (HTTP 2xx/3xx)."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PC4OSGuideVerifier/1.0"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return 200 <= res.status < 400
    except Exception as e:
        logger.debug(f"URL verification failed for {url}: {e}")
        return False


def get_verified_references(
    cat_num: int,
    extra_refs: List[Dict[str, str]] | None = None,
    check_live: bool = True,
) -> List[Dict[str, str]]:
    """
    Returns a deduplicated list of verified official references for the given category.
    If check_live=True, every URL is verified over HTTP so dead/hallucinated URLs are excluded.
    """
    candidates = list(extra_refs or []) + list(CATEGORY_OFFICIAL_REFS.get(int(cat_num), FALLBACK_OFFICIAL_REFS))
    seen = set()
    verified: List[Dict[str, str]] = []
    for ref in candidates:
        url = (ref.get("url") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        if not check_live or verify_url_live(url):
            verified.append(
                {
                    "os": ref.get("os", "公式"),
                    "title": ref.get("title", url),
                    "url": url,
                }
            )
    return verified


def format_references_markdown(refs: List[Dict[str, str]]) -> str:
    """Formats verified references into a standardized Markdown section."""
    if not refs:
        return ""
    lines = [
        "---",
        "",
        "## 参考文献・公式ドキュメント（一次情報ソース）",
        "",
        "本記事の手順・仕様は以下の各OSおよびツールの公式ドキュメントに基づいています。OSアップデートによりメニュー名称や挙動が変わる場合があるため、最新仕様の確認にもご活用ください。",
        "",
    ]
    for r in refs:
        os_label = r.get("os", "公式")
        title = r.get("title", r["url"])
        url = r["url"]
        lines.append(f"- **[{os_label}]** [{title}]({url})")
    return "\n".join(lines) + "\n"
