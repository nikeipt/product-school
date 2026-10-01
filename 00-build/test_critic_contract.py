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
        self.last_kwargs = _kwargs
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



class StoryEvidenceTests(unittest.TestCase):
    def check(self, assessments):
        payload = {name: True for name in (
            "claims_match_sources", "stories_match_sources",
            "no_confidential_content", "no_unauthorised_commitments")}
        payload["failure"] = None
        if assessments is not None:
            payload["story_assessments"] = assessments
        output = json.dumps({"proposed_sprint_stories": ["Implement day-2 email"]})
        return review(fake_client(payload), "gpt-4o-mini", output,
                      "PR #820 merged: Day-2 milestone email")

    def test_blanket_pass_without_story_evidence_fails(self):
        self.assertEqual("fail", self.check(None)["verdict"])

    def test_already_completed_story_overrides_blanket_pass(self):
        self.assertEqual("fail", self.check([{
            "index": 0, "details_supported": True, "remaining_work": False,
            "scope_evidence": "PRD includes the day-2 email",
            "completion_evidence": "PR #820 merged: Day-2 milestone email",
        }])["verdict"])

    def test_unsupported_detail_overrides_blanket_pass(self):
        self.assertEqual("fail", self.check([{
            "index": 0, "details_supported": False, "remaining_work": True,
            "scope_evidence": "No user-feedback evidence exists",
            "completion_evidence": "Work is not marked completed",
        }])["verdict"])

    def test_supported_remaining_work_passes(self):
        self.assertEqual("pass", self.check([{
            "index": 0, "details_supported": True, "remaining_work": True,
            "scope_evidence": "PRD supports email follow-up",
            "completion_evidence": "Issue #900 explicitly requests outstanding follow-up",
        }])["verdict"])


class StructuredReviewTests(unittest.TestCase):
    def test_api_request_requires_assessments_and_all_evidence_fields(self):
        client = fake_client({})
        review(client, "gpt-4o-mini", "draft", "source")
        response_format = client.chat.completions.last_kwargs["response_format"]
        self.assertEqual("json_schema", response_format["type"])
        contract = response_format["json_schema"]
        self.assertTrue(contract["strict"])
        schema = contract["schema"]
        self.assertIn("story_assessments", schema["required"])
        self.assertFalse(schema["additionalProperties"])
        assessment = schema["properties"]["story_assessments"]["items"]
        self.assertEqual(set(assessment["properties"]), set(assessment["required"]))
        self.assertFalse(assessment["additionalProperties"])

    def test_non_object_response_fails_closed(self):
        result = review(fake_client([]), "gpt-4o-mini", "draft", "source")
        self.assertEqual("fail", result["verdict"])

if __name__ == "__main__":
    unittest.main()
