"""Regression tests for the M3 validator contract and objective checks."""

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
            "stories_match_sources": True,
            "no_confidential_content": True,
            "no_unauthorised_commitments": True,
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

    def test_critic_rejects_story_without_source_support(self):
        result = review(fake_client({
            "claims_match_sources": True,
            "stories_match_sources": False,
            "no_confidential_content": True,
            "no_unauthorised_commitments": True,
            "failure": {
                "check": "stories_match_sources",
                "draft_claim": "Launch a referral programme",
                "source_evidence": "No referral work appears in the PRD or roadmap",
                "mismatch": "The proposed story is outside the supported scope",
            },
        }), "gpt-4o-mini", "proposed stories", "source")

        self.assertEqual("fail", result["verdict"])
        self.assertIn("stories_match_sources", result["reasons"][0])

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

    def test_code_rejects_wrong_project_missing_output_and_unknown_tool(self):
        result = agent.validate_operational_checks(
            {
                "project_id": "P-WRONG",
                "leadership_update": "",
                "story_proposal_status": "not_requested",
            },
            "done",
            {"project_id": "P-NORTH"},
            stories_requested=True,
            stories_queued=False,
            tools_called=["get_project", "publish_update"],
        )

        self.assertEqual("fail", result["verdict"])
        self.assertFalse(result["correct_project"])
        self.assertFalse(result["requested_outputs_present"])
        self.assertFalse(result["no_unauthorised_action"])
        self.assertEqual(3, len(result["reasons"]))

    def test_revision_cap_matches_approved_m3_policy(self):
        self.assertEqual(1, agent.MAX_REVISIONS)


if __name__ == "__main__":
    unittest.main()
