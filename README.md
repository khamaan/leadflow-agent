# LeadFlow Agent

A small agentic AI assistant for incoming software project enquiries. It reads one lead, chooses which local tools to call, matches the request against a service catalog and case studies, then prepares a qualification note and a follow-up draft for human review.

Built from scratch with **OpenAI Codex** as the AI coding collaborator. The runtime agent uses the OpenAI Responses API function-calling loop. It does **not** send email, edit CRM records, or contact a lead.

## What makes it agentic

1. The model selects a catalog search query from the lead's request.
2. It can request a relevant case study before deciding what to recommend.
3. The application executes only two allowlisted, read-only functions and returns their results to the model.
4. The model produces a structured recommendation and draft. The CLI validates and displays it for a person to review.

The catalog and case studies are sample data; replace them with your own accurate offerings before using this for real leads. A lead is sent to the selected OpenAI model when you run the CLI. Do not use real personal data unless you have permission to process it.

## Quick start

Requires Python 3.11+ and an OpenAI API key. No third-party Python packages are required.

```bash
export OPENAI_API_KEY="your-key"  # PowerShell: $env:OPENAI_API_KEY = "your-key"
python -m leadflow examples/sample_lead.json
```

Optional: set `OPENAI_MODEL` to a Responses API model available to your account. The default is `gpt-5.6-terra`.

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Example input

```json
{
  "name": "Priya Shah",
  "company": "BrightPath Academy",
  "email": "priya@example.com",
  "message": "We need a CRM for enquiries and WhatsApp follow-ups across two branches.",
  "budget_inr": 250000,
  "timeline_weeks": 8
}
```

## Output

The CLI prints JSON with `recommendation`, `service_id`, `confidence`, `reason`, `evidence`, `questions`, and `draft_reply`. The draft is a suggestion; review facts, pricing, and wording before sending.

## Design notes

- Tools are read-only and have strict argument validation.
- The model is limited to four tool rounds and eight total calls.
- Tool calls and recommendation are auditable in the CLI output.
- The application never treats lead text as instructions to change its tools, data, or policies.
- Tests use a fake model transport, so they run without a key or network access.

API design follows the [official OpenAI function calling guide](https://developers.openai.com/api/docs/guides/function-calling).
