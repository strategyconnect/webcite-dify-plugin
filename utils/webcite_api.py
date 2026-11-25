"""Small client for the public Webcite REST API (https://api.webcite.co/api/v1/openapi.json)."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import httpx

BASE_URL = "https://api.webcite.co"
USER_AGENT = "webcite-dify-plugin/0.0.1"
# Extraction keeps the request open until every page is read, so allow long reads.
TIMEOUT = httpx.Timeout(880.0, connect=15.0)

_STATUS_ACTIONS = {
    401: "Webcite rejected the API key. Create or copy a key at https://webcite.co/api-keys "
    "and save it in the plugin credentials.",
    402: "The Webcite account has no credits left. Add credits at https://webcite.co/pricing.",
    403: "The Webcite API key is not allowed to call this endpoint. Check the key's permissions.",
    429: "Webcite rate limit reached. Wait a moment and run the tool again.",
}


class WebciteError(Exception):
    """A Webcite API call failed. The message says what to do next and never contains the key."""

    def __init__(self, message: str, status: Optional[int] = None) -> None:
        super().__init__(message)
        self.status = status


def _message(response: httpx.Response) -> str:
    action = _STATUS_ACTIONS.get(response.status_code)
    if action:
        return f"{action} (HTTP {response.status_code})"
    detail = ""
    try:
        body = response.json()
        if isinstance(body, dict):
            detail = str(body.get("message") or body.get("error") or "")
    except ValueError:
        detail = response.text[:200]
    return f"Webcite API returned HTTP {response.status_code}. {detail}".strip()


class WebciteClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        key = (api_key or "").strip()
        if not key:
            raise WebciteError("Add a Webcite API key in the plugin credentials.")
        self._http = httpx.Client(
            base_url=base_url,
            timeout=TIMEOUT,
            transport=transport,
            headers={"x-api-key": key, "User-Agent": USER_AGENT, "Accept": "application/json"},
        )

    def _request(self, method: str, path: str, body: Optional[Mapping[str, Any]] = None) -> Any:
        try:
            response = self._http.request(method, path, json=body)
        except httpx.TimeoutException as exc:
            raise WebciteError(
                "The Webcite request did not finish in time. Run the tool again; "
                "repeated extractions of the same document reuse the stored result."
            ) from exc
        except httpx.HTTPError as exc:
            raise WebciteError(f"Could not reach the Webcite API: {type(exc).__name__}.") from exc
        if response.status_code >= 400:
            raise WebciteError(_message(response), response.status_code)
        return response.json()

    def balance(self) -> Any:
        """Free call used to check the key."""
        return self._request("GET", "/api/v1/payment/credits/balance")

    def verify(self, claim: str, source_urls: Optional[list[str]] = None) -> Any:
        body: dict[str, Any] = {"claim": claim}
        if source_urls:
            body["source_urls"] = source_urls
        return self._request("POST", "/api/v1/verify", body)

    def extract_url(self, url: str) -> Any:
        return self._request("POST", "/api/v1/extract", {"asset_url": url})

    def search(self, query: str, limit: Optional[int] = None) -> Any:
        body: dict[str, Any] = {"query": query}
        if limit:
            body["limit"] = limit
        return self._request("POST", "/api/v1/sources/search", body)

    def close(self) -> None:
        self._http.close()
