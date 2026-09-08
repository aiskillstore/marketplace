from __future__ import annotations

from abc import ABC, abstractmethod
from urllib.parse import urlsplit

from sharextract.http import SafeHttpClient
from sharextract.models import ExtractedContent


class ExtractorError(RuntimeError):
    pass


class Extractor(ABC):
    name = "base"
    priority = 100

    def __init__(self, client: SafeHttpClient | None = None) -> None:
        self.client = client or SafeHttpClient()

    @abstractmethod
    def supports(self, url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def extract(self, url: str) -> ExtractedContent:
        raise NotImplementedError

    @staticmethod
    def hostname(url: str) -> str:
        return (urlsplit(url).hostname or "").lower()
