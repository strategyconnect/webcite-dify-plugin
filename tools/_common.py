"""Helpers shared by the Webcite tools."""

from __future__ import annotations

from typing import Any

from utils.webcite_api import WebciteClient


def client_from(credentials: dict[str, Any]) -> WebciteClient:
    return WebciteClient(str(credentials.get("webcite_api_key", "")))


def split_urls(raw: Any) -> list[str]:
    """Accept URLs separated by commas, spaces or new lines."""
    if not raw:
        return []
    parts = str(raw).replace(",", " ").split()
    return [p for p in parts if p.startswith(("http://", "https://"))]
