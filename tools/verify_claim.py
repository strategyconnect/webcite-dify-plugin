from __future__ import annotations

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._common import client_from, split_urls


def summarize(result: dict[str, Any], max_citations: int = 3) -> str:
    lines: list[str] = []
    for group in result.get("claim_groups") or []:
        verdict = group.get("verdict") or {}
        lines.append(f"Claim: {group.get('claim', '')}")
        lines.append(f"Verdict: {verdict.get('result', 'unknown')}")
        if verdict.get("summary"):
            lines.append(f"Summary: {verdict['summary']}")
        for citation in (group.get("citations") or [])[:max_citations]:
            stance = citation.get("stance") or "source"
            lines.append(f"- {stance}: {citation.get('url', '')}")
            snippet = citation.get("snippet")
            if snippet:
                lines.append(f"  \"{snippet[:300]}\"")
        lines.append("")
    credits = (result.get("usage") or {}).get("credits")
    if credits is not None:
        lines.append(f"Credits used: {credits}")
    return "\n".join(lines).strip()


class VerifyClaimTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        claim = str(tool_parameters.get("claim") or "").strip()
        if not claim:
            yield self.create_text_message("Enter a claim to verify.")
            return
        client = client_from(self.runtime.credentials)
        try:
            result = client.verify(claim, split_urls(tool_parameters.get("source_urls")))
        finally:
            client.close()
        yield self.create_text_message(summarize(result))
        yield self.create_json_message(result)
