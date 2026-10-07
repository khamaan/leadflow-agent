import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from leadflow.web import Handler, JOBS, LOCK


class WebTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        with LOCK:
            JOBS.clear()

    def test_serves_browser_app_and_requires_key(self):
        with urllib.request.urlopen(self.base) as response:
            self.assertIn(b"LeadFlow Agent", response.read())
        data = json.dumps({"lead": {"name": "A", "company": "B", "message": "CRM"}}).encode()
        request = urllib.request.Request(self.base + "/api/jobs", data=data,
                                         headers={"Content-Type": "application/json"})
        with patch.dict("os.environ", {"GEMINI_API_KEY": ""}):
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
        self.assertEqual(error.exception.code, 400)

    def test_job_returns_result_without_key(self):
        lead = {"name": "A", "company": "B", "message": "CRM"}
        data = json.dumps({"lead": lead, "api_key": "test-secret"}).encode()
        request = urllib.request.Request(self.base + "/api/jobs", data=data,
                                         headers={"Content-Type": "application/json"})
        with patch("leadflow.web.GeminiTransport") as transport, \
             patch("leadflow.web.qualify_lead", return_value={"recommendation": "clarify"}):
            with urllib.request.urlopen(request) as response:
                job_id = json.load(response)["id"]
            with urllib.request.urlopen(self.base + "/api/jobs/" + job_id) as response:
                job = json.load(response)
        self.assertEqual(job["status"], "complete")
        self.assertEqual(job["result"]["recommendation"], "clarify")
        self.assertNotIn("test-secret", json.dumps(job))
        transport.assert_called_once()


if __name__ == "__main__":
    unittest.main()
