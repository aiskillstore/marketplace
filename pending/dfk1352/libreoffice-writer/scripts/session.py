"""Shared session primitives for LibreOffice skills."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal, Self

from exceptions import SessionClosedError


class BaseSession(ABC):
    """Minimal shared protocol for long-lived skill sessions."""

    def __init__(
        self,
        closed_error_type: type[Exception] = SessionClosedError,
    ) -> None:
        self._closed = False
        self._closed_error_type: type[Exception] = closed_error_type

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> Literal[False]:
        self.close(save=True)
        return False

    @abstractmethod
    def close(self, save: bool = True) -> None:
        """Persist changes if requested, then release session resources."""

    def _require_open(self) -> None:
        if self._closed:
            raise self._closed_error_type("Session is already closed")
