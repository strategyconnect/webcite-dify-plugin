from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._common import client_from


def listing(result: dict[str, Any]) -> str:
    groups = result.get("claim_groups") or []
    items = (groups[0].get("citations") if groups else None) or result.get("citations") or []
    lines = []
    for item in items:
        title = item.get("title") or item.get("url", "")
        lines.append(f"- {title}: {item.get('url', '')}")
    return "\n".join(lines)


class SearchSourcesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = str(tool_parameters.get("query") or "").strip()
        if not query:
            yield self.create_text_message("Enter a search query.")
            return
        limit = tool_parameters.get("limit")
        client = client_from(self.runtime.credentials)
        try:
            result = client.search(query, int(limit) if limit else None)
        finally:
            client.close()
        yield self.create_text_message(listing(result))
        yield self.create_json_message(result)
