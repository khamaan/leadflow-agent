import unittest
from unittest.mock import patch
import json

from leadflow.agent import AgentError, GeminiTransport, qualify_lead, validate_lead, ENDPOINT
from leadflow.catalog import search_services


LEAD = {"name": "Priya Shah", "company": "BrightPath Academy", "message": "Need a CRM for enquiries and WhatsApp follow-ups."}


class FakeTransport:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.payloads = []

    def create(self, payload):
        self.payloads.append(payload)
        return next(self.responses)


def call(call_id, name, arguments):
    return {"type": "function_call", "id": call_id, "name": name, "arguments": arguments}


class LeadFlowTests(unittest.TestCase):
    def test_catalog_search(self):
        self.assertEqual(search_services("CRM enquiry WhatsApp")[0]["id"], "crm-automation")

    def test_model_driven_tool_loop_and_review_gate(self):
        answer = '{"recommendation":"pursue","service_id":"crm-automation","confidence":"medium","reason":"Relevant CRM request","evidence":["Education enquiry workflow"],"questions":["How many users?"],"draft_reply":"Hi Priya, I can discuss the CRM workflow. How many users need access?"}'
        fake = FakeTransport([
            {"id": "r1", "steps": [call("c1", "search_services", {"query": "CRM enquiry WhatsApp"})]},
            {"id": "r2", "steps": [call("c2", "get_case_study", {"service_id": "crm-automation"})]},
            {"id": "r3", "steps": [{"type": "model_output", "content": [{"type": "text", "text": answer}]}]},
        ])
        result = qualify_lead(LEAD, fake)
        self.assertEqual(result["recommendation"], "pursue")
        self.assertTrue(result["human_review_required"])
        self.assertEqual([x["tool"] for x in result["tool_audit"]], ["search_services", "get_case_study"])
        self.assertEqual(fake.payloads[1]["previous_interaction_id"], "r1")
        self.assertEqual(fake.payloads[1]["input"][0]["call_id"], "c1")

    def test_cannot_claim_unconsulted_case_study(self):
        answer = '{"recommendation":"pursue","service_id":"crm-automation","confidence":"high","reason":"x","evidence":[],"questions":[],"draft_reply":"Hi"}'
        fake = FakeTransport([
            {"id": "r1", "steps": [call("c1", "search_services", {"query": "CRM"})]},
            {"id": "r2", "steps": [{"type": "model_output", "content": [{"type": "text", "text": answer}]}]},
        ])
        with self.assertRaises(AgentError):
            qualify_lead(LEAD, fake)

    def test_invalid_lead_rejected(self):
        with self.assertRaises(ValueError):
            validate_lead({"name": "", "company": "Acme", "message": "hello"})

    def test_gemini_transport_uses_key_header_and_interactions_endpoint(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self, *_):
                return b'{"id":"test","steps":[]}'

        with patch("leadflow.agent.urllib.request.urlopen", return_value=Response()) as opened:
            result = GeminiTransport(api_key="test-key", model="gemini-test").create({"input": "hello"})
        request = opened.call_args.args[0]
        self.assertEqual(request.full_url, ENDPOINT)
        self.assertEqual(request.get_header("X-goog-api-key"), "test-key")
        self.assertEqual(json.loads(request.data)["model"], "gemini-test")
        self.assertEqual(result["id"], "test")


if __name__ == "__main__":
    unittest.main()
