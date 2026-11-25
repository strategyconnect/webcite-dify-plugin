# Webcite for Dify

Webcite is one evidence suite for AI apps and agents: document parsing and OCR to Markdown, claim verification with verdicts, citations bound to source passages, and source search. This plugin adds three Webcite tools to Dify workflows, chatflows and agents.

- Author: Webcite
- Version: 0.0.1
- Type: tool
- Source: https://github.com/strategyconnect/webcite-dify-plugin
- Contact: support@webcite.co

## Tools

| Tool | What it does | Credits |
|---|---|---|
| Verify claim | Checks one factual claim against web sources (or the URLs you give) and returns a verdict, a summary and citations with the quoted source passages | 4 per claim |
| Parse document to Markdown | Reads a PDF, scan, image, spreadsheet or office file from a direct link and returns Markdown with page provenance | Charged per page |
| Search sources | Finds web sources for a query, with titles, URLs and snippets, no verdict | 2 per search |

Credit prices are listed at https://webcite.co/pricing. The Free plan includes 100 credits.

## Setup

1. Create a Webcite account and an API key at https://webcite.co/api-keys.
2. In Dify, install the Webcite plugin from the Marketplace (or upload the `.difypkg` file under Plugins, Install from local package file).
3. Open the plugin, choose Authorize, and paste the API key. Dify checks the key with Webcite's free credit balance call; no credits are spent.

## Usage

- Workflow or chatflow: add a Tool node, pick Webcite, then one of the three tools. Each tool returns text (the verdict summary, the Markdown, or a source list) and a JSON object with the full API response.
- Agent: enable the Webcite tools in the agent's tool list. The model fills in the claim, document URL or query.

Example: an agent that answers a question can call Search sources, write its answer, then call Verify claim on each factual sentence and show the citations next to it.

## Requirements and connection

- Network: the plugin calls `https://api.webcite.co` over HTTPS only. Your Dify instance must be able to reach it.
- Parse document to Markdown needs a direct link to the file that Webcite's servers can download. Webcite fetches the file; the plugin does not.
- Long documents can take a few minutes; the request stays open until every page is read.

## Privacy

See [PRIVACY.md](PRIVACY.md).

## Development

```bash
uv venv -p 3.12 .venv && uv pip install -p .venv -r requirements.txt pytest
.venv/bin/pytest -q                                # saved API responses, no network
WEBCITE_LIVE_401=1 .venv/bin/pytest -q tests/test_live_401.py   # live call with a placeholder key, expects 401
dify plugin package .                              # builds webcite.difypkg
```

## License

MIT
