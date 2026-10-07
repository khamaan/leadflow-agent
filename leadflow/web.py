"""Local browser interface for LeadFlow Agent."""
from __future__ import annotations

import argparse
import json
import os
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .agent import AgentError, GeminiTransport, qualify_lead, validate_lead

STATIC = Path(__file__).with_name("static")
JOBS: dict[str, dict[str, Any]] = {}
LOCK = threading.Lock()


def _run_job(job_id: str, lead: dict[str, Any], api_key: str | None) -> None:
    def record(event: dict[str, Any]) -> None:
        with LOCK:
            JOBS[job_id]["events"].append(event)

    try:
        transport = GeminiTransport(api_key=api_key, on_event=record)
        result = qualify_lead(lead, transport, on_event=record)
        with LOCK:
            JOBS[job_id].update(status="complete", result=result)
    except (AgentError, ValueError, OSError) as exc:
        with LOCK:
            JOBS[job_id].update(status="error", error=str(exc))
    finally:
        api_key = None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        # Do not log request data or credentials.
        pass

    def _json(self, status: int, body: dict[str, Any]) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._file("index.html", "text/html; charset=utf-8")
        elif self.path == "/app.css":
            self._file("app.css", "text/css; charset=utf-8")
        elif self.path == "/app.js":
            self._file("app.js", "text/javascript; charset=utf-8")
        elif self.path == "/api/config":
            self._json(200, {"key_configured": bool(os.getenv("GEMINI_API_KEY")),
                             "model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash")})
        elif self.path.startswith("/api/jobs/"):
            job_id = self.path.removeprefix("/api/jobs/")
            with LOCK:
                job = JOBS.get(job_id)
                snapshot = json.loads(json.dumps(job)) if job else None
            self._json(200, snapshot) if snapshot else self._json(404, {"error": "Run not found"})
        else:
            self._json(404, {"error": "Not found"})

    def _file(self, name: str, content_type: str) -> None:
        data = (STATIC / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        if self.path != "/api/jobs":
            self._json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 20000:
                raise ValueError("Request must be at most 20 KB")
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError("Request must be a JSON object")
            lead = validate_lead(body.get("lead"))
            api_key = body.get("api_key")
            if api_key is not None and (not isinstance(api_key, str) or len(api_key) > 512):
                raise ValueError("Invalid API key")
            if not api_key and not os.getenv("GEMINI_API_KEY"):
                raise ValueError("Enter a Gemini API key to run the agent")
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return
        job_id = uuid.uuid4().hex
        with LOCK:
            JOBS[job_id] = {"id": job_id, "status": "running", "events": [],
                            "result": None, "error": None}
        threading.Thread(target=_run_job, args=(job_id, lead, api_key), daemon=True).start()
        self._json(202, {"id": job_id})


def main() -> None:
    parser = argparse.ArgumentParser(description="Open the local LeadFlow browser app")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"LeadFlow is running at {url} | close this window to stop it", flush=True)
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
