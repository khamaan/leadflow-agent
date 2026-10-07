# LeadFlow Agent

A small agentic AI assistant for incoming software project enquiries. It reads one lead, chooses which local tools to call, matches the request against a service catalog and case studies, then prepares a qualification note and a follow-up draft for human review.

Built from scratch with **Codex** as the AI coding collaborator. The runtime agent uses **Gemini's Interactions API** and a Gemini API key. It does **not** send email, edit CRM records, or contact a lead.

The working copy for Aaman is `C:\Users\Aaman Khan\Desktop\LeadFlow Agent`; this repository is its GitHub remote.

## What makes it agentic

1. The model selects a catalog search query from the lead's request.
2. It can request a relevant case study before deciding what to recommend.
3. The application executes only two allowlisted, read-only functions and returns their results to the model.
4. The model produces a structured recommendation and draft. The CLI validates and displays it for a person to review.

The catalog and case studies are sample data; replace them with your own accurate offerings before using this for real leads. A lead is sent to the selected Gemini model when you run the CLI. Do not use real personal data unless you have permission to process it.

## Run end to end on Windows

You need Python 3.11+ and a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey). No third-party Python packages are required. A model request may use your Gemini API quota or incur charges under your Google account.

1. Open PowerShell and go to the Desktop working copy:

```powershell
Set-Location -LiteralPath 'C:\Users\Aaman Khan\Desktop\LeadFlow Agent'
```

2. Set your key for **this PowerShell window only**. Paste your real key between the quotes; do not add it to a file or Git commit:

```powershell
$env:GEMINI_API_KEY = 'paste-your-gemini-api-key-here'
```

3. Run the included sample lead:

```powershell
python -m leadflow examples/sample_lead.json
```

If your Python command is `py`, use `py -3 -m leadflow examples/sample_lead.json` instead. The command makes Gemini API calls. It should print a JSON result with a recommendation, a matched service, evidence, questions, a draft reply, and `tool_audit`. Review the draft before using it.

4. To try your own lead, make a private local copy, edit the fields, and run it:

```powershell
New-Item -ItemType Directory -Path leads -Force | Out-Null
Copy-Item examples/sample_lead.json leads/my_lead.json
notepad leads/my_lead.json
python -m leadflow leads/my_lead.json
```

The `leads/` directory is ignored by Git. Do not commit real lead data or your key.

5. Run the local tests (no API key or network needed):

```powershell
python -m unittest discover -s tests -v
```

The default model is `gemini-3.8-flash`. If your key lacks access to it, set a supported Gemini model in the same PowerShell window, for example `$env:GEMINI_MODEL = 'your-supported-model-id'`, then rerun. To clear the key from that window, run `Remove-Item Env:GEMINI_API_KEY`.

On Linux/macOS, use `export GEMINI_API_KEY='your-key'` and the same `python -m leadflow ...` command.

## What happens during a run

The lead is sent to Gemini. Gemini can call `search_services` to look up local offerings, and `get_case_study` to read one relevant proof point. The Python application runs those read-only functions and returns their results to Gemini. Gemini then prepares a structured qualification decision and reply draft. The application checks the result and prints it. A person decides whether to act on the draft.

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

The CLI prints JSON with `recommendation`, `service_id`, `confidence`, `reason`, `evidence`, `questions`, `draft_reply`, `tool_audit`, and `human_review_required`. The draft is a suggestion; review facts, pricing, and wording before sending.

## Design notes

- Tools are read-only and have strict argument validation.
- The model is limited to four tool rounds and eight total calls.
- Tool calls and recommendation are auditable in the CLI output.
- The application instructs Gemini to treat lead text as data, and the tool dispatcher rejects unknown tools and invalid arguments.
- Tests use a fake model transport, so they run without a key or network access.

API design follows the [official Gemini function calling guide](https://ai.google.dev/gemini-api/docs/function-calling/) and [Gemini API authentication reference](https://ai.google.dev/api).
