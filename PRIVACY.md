# Privacy policy for the Webcite Dify plugin

The plugin itself stores nothing and collects no analytics or telemetry.

## What is sent, and to whom

When a tool runs, the plugin sends the tool input to the Webcite API at `https://api.webcite.co`, authenticated with the API key you saved in Dify:

- Verify claim: the claim text and any source URLs you entered.
- Parse document to Markdown: the document URL. Webcite downloads the file from that URL and processes its contents.
- Search sources: the search query.
- Authorization: a credit balance request, to check the key.

No other data leaves your Dify instance through this plugin. The API key is stored by Dify as a secret credential and is sent only to `api.webcite.co` in the `x-api-key` header. Error messages never include the key.

## How Webcite handles the data

Webcite processes and stores requests and results under its own privacy policy: https://webcite.co/privacy-policy. Results such as verdicts, citations and extracted documents are kept in your Webcite account.

## Contact

support@webcite.co
