from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._common import client_from


def overview(doc: dict[str, Any]) -> dict[str, Any]:
    """The document result without the page units, which repeat the Markdown."""
    return {k: v for k, v in doc.items() if k not in ("units", "markdown")}


class ExtractDocumentTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        url = str(tool_parameters.get("document_url") or "").strip()
        if not url.startswith(("http://", "https://")):
            yield self.create_text_message("Enter a direct http or https link to the document.")
            return
        client = client_from(self.runtime.credentials)
        try:
            doc = client.extract_url(url)
        finally:
            client.close()
        markdown = str(doc.get("markdown") or "")
        if markdown:
            yield self.create_text_message(markdown)
        yield self.create_json_message(overview(doc))
