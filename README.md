# LeadFlow Agent

A local browser app for qualifying incoming software project leads. Gemini decides when to search a service catalog and read a relevant case study, then creates a recommendation and reply draft for a person to review. The app shows those tool calls as they happen.

Built from scratch with **Codex** as the AI coding collaborator. The runtime agent uses the **Gemini Interactions API**. Its tools are read-only; it never emails a lead or changes a CRM record.

## Run the browser app on Windows

1. Install Python 3.11 or newer.
2. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
3. Open the Desktop project folder, `C:\Users\Aaman Khan\Desktop\LeadFlow Agent`.
4. Double-click **Start LeadFlow.bat**. Your browser opens at `http://127.0.0.1:8765`.
5. Click **Load example** or enter your own enquiry. Paste your key into the form and click **Run agent**.
6. Watch the activity panel. When the run finishes, review the recommendation, evidence, questions, and draft reply. You can copy the draft, but the app does not send it.

Keep the launcher window open while using the app; close it to stop the local server. The server listens only on `127.0.0.1`. The key is used for the current run and is not written to a project file or browser storage. You may alternatively set `GEMINI_API_KEY` in the environment before starting the server, then leave the key field empty.

If the launcher cannot find Python, open PowerShell in this folder and run `py -3 -m leadflow.web`. On Linux/macOS, run `python3 -m leadflow.web`. The default model is the faster `gemini-3.5-flash-lite`; set `GEMINI_MODEL` in the server environment if your key needs another compatible Gemini model.

Gemini calls can take a few minutes. The app uses a foreground interaction with a four-minute read timeout for each model step. The browser remains responsive and shows the current step while the server waits. This avoids a current Gemini background-status retrieval error; a slow or unavailable provider can still cause a timeout, which the UI will show.

## What makes it agentic

1. Gemini interprets the lead and chooses its own catalog search query.
2. It requests a case study for a returned service when useful.
3. Python executes only the allowlisted `search_services` and `get_case_study` functions, then returns their results to Gemini.
4. Gemini decides whether to pursue, clarify, or decline, and writes a reply draft. The app validates the answer and displays a tool audit.

The catalog and case studies are sample data. Replace them with accurate offerings before use with real clients. A lead is sent to Gemini when you run the agent. Use personal data only when you have permission to process it. Model requests may use your Gemini API quota or incur charges.

## Optional CLI and tests

The browser app is the main interface. The CLI remains available for automation:

```powershell
python -m leadflow examples/sample_lead.json
python -m unittest discover -s tests -v
```

The CLI uses `GEMINI_API_KEY` from the environment. Tests use fake Gemini responses and do not need a key or network access. The `leads/` folder is ignored by Git for private local input files.

API design follows the [Gemini function calling guide](https://ai.google.dev/gemini-api/docs/function-calling/).

