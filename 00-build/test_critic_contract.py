"""Regression tests for the POC critic's deliberately narrow authority."""

import json
import unittest
from types import SimpleNamespace

import agent
from critic import review


class FakeCompletions:
    def __init__(self, payload):
        self.payload = payload

    def create(self, **_kwargs):
        return SimpleNamespace(
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
            choices=[SimpleNamespace(message=SimpleNamespace(
                content=json.dumps(self.payload)))],
        )


def fake_client(payload):
    return SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions(payload)))


class CriticContractTests(unittest.TestCase):
    def test_critic_cannot_fail_an_operational_permission_check(self):
        result = review(fake_client({
            "claims_match_sources": True,
            "no_confidential_content": True,
            "no_unauthorised_action": False,
            "failure": {
                "check": "no_unauthorised_action",
                "draft_claim": "queued for review",
                "source_evidence": "no publishing",
                "mismatch": "incorrectly treated queuing as publishing",
            },
        }), "gpt-4o-mini", "queued for review", "source")

        self.assertEqual("pass", result["verdict"])
        self.assertEqual([], result["reasons"])

    def test_code_accepts_allowed_queue_workflow(self):
        result = agent.validate_operational_checks(
            {
                "project_id": "P-NORTH",
                "leadership_update": "Draft update",
                "story_proposal_status": "queued_for_approval",
            },
            "done",
            {"project_id": "P-NORTH"},
            stories_requested=True,
            stories_queued=True,
            tools_called=["get_project", "propose_stories"],
        )

        self.assertEqual("pass", result["verdict"])
        self.assertTrue(result["no_unauthorised_action"])


if __name__ == "__main__":
    unittest.main()
