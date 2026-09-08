from __future__ import annotations

from dataclasses import dataclass

from sharextract.http import SafeHttpClient, validate_public_url
from sharextract.models import ExtractedContent

from .extractors import (
    BilibiliVideoExtractor,
    BlueskyPostExtractor,
    ChatGPTShareExtractor,
    ClaudeShareExtractor,
    DeepSeekShareExtractor,
    DoubaoShareExtractor,
    DouyinVideoExtractor,
    GenericWebExtractor,
    GrokShareExtractor,
    KimiShareExtractor,
    LinkedInPostExtractor,
    KuaishouAtlasExtractor,
    KuaishouVideoExtractor,
    GeminiShareExtractor,
    MastodonStatusExtractor,
    ThreadsPostExtractor,
    InstagramPostExtractor,
    FacebookPostExtractor,
    TikTokOEmbedExtractor,
    VimeoOEmbedExtractor,
    XPostOEmbedExtractor,
    YouTubeOEmbedExtractor,
    PinterestPinExtractor,
    QwenShareExtractor,
    RedditPostExtractor,
    TelegramPostExtractor,
    YtDlpExtractor,
    WeiboStatusExtractor,
    XiaohongshuNoteExtractor,
    ZhihuAnswerExtractor,
    ZhihuArticleExtractor,
)
from .extractors.base import Extractor


class ExtractionFailure(RuntimeError):
    pass


@dataclass(slots=True)
class ExtractionAttempt:
    extractor: str
    error: str


def extract(
    url: str,
    *,
    strategy: str = "auto",
    timeout: float = 20.0,
    max_bytes: int = 8 * 1024 * 1024,
) -> ExtractedContent:
    """Extract public content from *url* using the safest highest-fidelity route."""
    validate_public_url(url)
    client = SafeHttpClient(timeout=timeout, max_bytes=max_bytes)
    extractors = _extractors_for_strategy(strategy, client)
    attempts: list[ExtractionAttempt] = []

    for extractor in extractors:
        if not extractor.supports(url):
            continue
        try:
            result = extractor.extract(url)
            if result.has_body or result.title or result.media:
                if attempts:
                    result.warnings.extend(
                        f"Fallback after {attempt.extractor} failed: {attempt.error}"
                        for attempt in attempts
                    )
                return result
            attempts.append(ExtractionAttempt(extractor.name, "empty extraction"))
        except Exception as exc:
            attempts.append(ExtractionAttempt(extractor.name, str(exc)))

    details = "; ".join(f"{a.extractor}: {a.error}" for a in attempts) or "no extractor matched"
    raise ExtractionFailure(f"Could not extract public content from {url}. {details}")


def _extractors_for_strategy(strategy: str, client: SafeHttpClient) -> list[Extractor]:
    token = strategy.strip().lower()
    if token not in {"auto", "native", "media", "web"}:
        raise ValueError("strategy must be one of: auto, native, media, web")

    native: list[Extractor] = sorted(
        [
            DeepSeekShareExtractor(client),
            DoubaoShareExtractor(client),
            ChatGPTShareExtractor(client),
            ClaudeShareExtractor(client),
            GeminiShareExtractor(client),
            GrokShareExtractor(client),
            KimiShareExtractor(client),
            QwenShareExtractor(client),
            BlueskyPostExtractor(client),
            MastodonStatusExtractor(client),
            XPostOEmbedExtractor(client),
            YouTubeOEmbedExtractor(client),
            VimeoOEmbedExtractor(client),
            TikTokOEmbedExtractor(client),
            RedditPostExtractor(client),
            TelegramPostExtractor(client),
            PinterestPinExtractor(client),
            ThreadsPostExtractor(client),
            InstagramPostExtractor(client),
            FacebookPostExtractor(client),
            LinkedInPostExtractor(client),
            BilibiliVideoExtractor(client),
            ZhihuAnswerExtractor(client),
            ZhihuArticleExtractor(client),
            WeiboStatusExtractor(client),
            DouyinVideoExtractor(client),
            XiaohongshuNoteExtractor(client),
            KuaishouVideoExtractor(client),
            KuaishouAtlasExtractor(client),
        ],
        key=lambda extractor: extractor.priority,
    )
    media = [YtDlpExtractor(client)]
    web = [GenericWebExtractor(client)]

    if token == "native":
        return native + web
    if token == "media":
        return media + web
    if token == "web":
        return web
    return native + media + web
