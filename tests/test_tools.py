"""Tool tests against saved Webcite API responses. No network access, no credits."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import httpx
import pytest

from tools import _common
from tools.extract_document import ExtractDocumentTool
from tools.search_sources import SearchSourcesTool
from tools.verify_claim import VerifyClaimTool
from utils.webcite_api import WebciteClient, WebciteError

FIXTURES = Path(__file__).parent / "fixtures"
SEEN: list[httpx.Request] = []


def load(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text())


def use_transport(monkeypatch: pytest.MonkeyPatch, answer: Callable[[httpx.Request], httpx.Response]) -> None:
    SEEN.clear()

    def handler(request: httpx.Request) -> httpx.Response:
        SEEN.append(request)
        return answer(request)

    def factory(credentials: dict[str, Any]) -> WebciteClient:
        return WebciteClient(credentials["webcite_api_key"], transport=httpx.MockTransport(handler))

    monkeypatch.setattr(_common, "client_from", factory)
    for module in ("tools.verify_claim", "tools.extract_document", "tools.search_sources"):
        monkeypatch.setattr(f"{module}.client_from", factory)


def run(tool_cls: Any, params: dict[str, Any]) -> list[Any]:
    tool = tool_cls.from_credentials({"webcite_api_key": "fixture-key"})
    return list(tool.invoke(params))


def test_verify_returns_verdict_and_citations(monkeypatch: pytest.MonkeyPatch) -> None:
    use_transport(monkeypatch, lambda r: httpx.Response(200, json=load("claim-great-wall.json")))
    messages = run(VerifyClaimTool, {
        "claim": "The Great Wall of China is visible from the Moon with the naked eye.",
        "source_urls": "https://www.nasa.gov/image-article/great-wall/, not-a-url",
    })
    text = messages[0].message.text
    assert "Verdict: contradicted" in text
    assert "https://www.nasa.gov/image-article/great-wall/" in text
    assert "Credits used: 4" in text
    assert messages[1].message.json_object["claim_groups"][0]["verdict"]["result"] == "contradicted"
    sent = json.loads(SEEN[0].content)
    assert SEEN[0].url.path == "/api/v1/verify"
    assert SEEN[0].headers["x-api-key"] == "fixture-key"
    assert sent == {
        "claim": "The Great Wall of China is visible from the Moon with the naked eye.",
        "source_urls": ["https://www.nasa.gov/image-article/great-wall/"],
    }


def test_extract_returns_markdown(monkeypatch: pytest.MonkeyPatch) -> None:
    use_transport(monkeypatch, lambda r: httpx.Response(201, json=load("doc-irs-w9.json")))
    messages = run(ExtractDocumentTool, {"document_url": "https://www.irs.gov/pub/irs-pdf/fw9.pdf"})
    assert messages[0].message.text.startswith("Form **W-9**")
    summary = messages[1].message.json_object
    assert "units" not in summary and "markdown" not in summary
    assert summary["usage"]["credits"] == load("doc-irs-w9.json")["usage"]["credits"]
    assert json.loads(SEEN[0].content) == {"asset_url": "https://www.irs.gov/pub/irs-pdf/fw9.pdf"}


def test_extract_rejects_non_http_input_without_a_call(monkeypatch: pytest.MonkeyPatch) -> None:
    use_transport(monkeypatch, lambda r: httpx.Response(500))
    messages = run(ExtractDocumentTool, {"document_url": "file:///etc/passwd"})
    assert "direct http or https link" in messages[0].message.text
    assert SEEN == []


def test_search_lists_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    # Search answers with the same claim_groups citation shape as verify (SearchResponseDto).
    saved = load("claim-great-wall.json")
    body = {"claim_groups": [{"citations": saved["claim_groups"][0]["citations"]}]}
    use_transport(monkeypatch, lambda r: httpx.Response(200, json=body))
    messages = run(SearchSourcesTool, {"query": "Great Wall visible from Moon", "limit": 3})
    assert "https://www.nasa.gov/image-article/great-wall/" in messages[0].message.text
    assert SEEN[0].url.path == "/api/v1/sources/search"
    assert json.loads(SEEN[0].content) == {"query": "Great Wall visible from Moon", "limit": 3}


def test_401_becomes_an_action_without_the_key(monkeypatch: pytest.MonkeyPatch) -> None:
    use_transport(monkeypatch, lambda r: httpx.Response(401, json={"message": "Unauthorized"}))
    with pytest.raises(WebciteError) as err:
        run(VerifyClaimTool, {"claim": "x"})
    assert err.value.status == 401
    assert "webcite.co/api-keys" in str(err.value)
    assert "fixture-key" not in str(err.value)


def test_empty_key_is_refused_before_any_call() -> None:
    with pytest.raises(WebciteError, match="Add a Webcite API key"):
        WebciteClient("  ")
