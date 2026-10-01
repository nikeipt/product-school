"""Independent validator (M3) for update and sprint-story content."""

from __future__ import annotations

import json

from prompts import CRITIC_SYSTEM



CHECK_NAMES = (
    "claims_match_sources", "stories_match_sources",
    "no_confidential_content", "no_unauthorised_commitments",
)


def _object_schema(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


# Structured output makes assessments mandatory; code still checks count,
# ordering, evidence and verdicts because shape alone cannot establish truth.
REVIEW_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "cortex_content_review",
        "strict": True,
        "schema": _object_schema({
            **{name: {"type": "boolean"} for name in CHECK_NAMES},
            "failure": {"anyOf": [
                {"type": "null"},
                _object_schema({
                    "check": {"type": "string", "enum": list(CHECK_NAMES)},
                    "draft_claim": {"type": "string"},
                    "source_evidence": {"type": "string"},
                    "mismatch": {"type": "string"},
                }),
            ]},
            "story_assessments": {
                "type": "array",
                "items": _object_schema({
                    "index": {"type": "integer"},
                    "details_supported": {"type": "boolean"},
                    "remaining_work": {"type": "boolean"},
                    "scope_evidence": {"type": "string"},
                    "completion_evidence": {"type": "string"},
                }),
            },
        }),
    },
}


def review(client, model: str, proposed_output: str, source_data: str) -> dict:
    """Run four content checks; code owns objective workflow enforcement."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM},
            {"role": "user", "content":
                f"SOURCE DATA Cortex used:\n{source_data}\n\n"
                f"CORTEX PROPOSED OUTPUT:\n{proposed_output}"},
        ],
        response_format=REVIEW_RESPONSE_FORMAT,
        temperature=0,
    )
    usage = resp.usage
    try:
        result = json.loads(resp.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        result = {}

    check_names = CHECK_NAMES
    if not isinstance(result, dict):
        result = {}

    malformed = [name for name in check_names if not isinstance(result.get(name), bool)]
    failed = [name for name in check_names if result.get(name) is False]
    failure = result.get("failure")

    reasons = []
    if malformed:
        reasons.append(f"critic omitted boolean checks: {', '.join(malformed)}")
    if failed:
        if not isinstance(failure, dict):
            reasons.append(f"failed checks without evidence: {', '.join(failed)}")
        else:
            reasons.append(
                f"{failure.get('check', ', '.join(failed))}: "
                f"claim={failure.get('draft_claim', 'not supplied')}; "
                f"source={failure.get('source_evidence', 'not supplied')}; "
                f"mismatch={failure.get('mismatch', 'not supplied')}")

    # A blanket pass is insufficient when stories were actually proposed.
    # Require a separate evidence-backed assessment for every queued story.
    try:
        output = json.loads(proposed_output)
    except (json.JSONDecodeError, TypeError):
        output = {}
    stories = output.get("proposed_sprint_stories", []) if isinstance(output, dict) else []
    if stories:
        assessments = result.get("story_assessments")
        if not isinstance(assessments, list) or len(assessments) != len(stories):
            reasons.append("stories_match_sources: missing per-story evidence assessments")
        else:
            for index, assessment in enumerate(assessments):
                if not isinstance(assessment, dict) or assessment.get("index") != index:
                    reasons.append(f"stories_match_sources: invalid assessment for story {index}")
                    continue
                evidence_fields = ("scope_evidence", "completion_evidence")
                if any(not isinstance(assessment.get(field), str) or
                       not assessment[field].strip() for field in evidence_fields):
                    reasons.append(f"stories_match_sources: missing evidence for story {index}")
                if assessment.get("details_supported") is not True:
                    reasons.append(f"stories_match_sources: unsupported details in story {index}: "
                                   f"{assessment.get('scope_evidence', '')}")
                if assessment.get("remaining_work") is not True:
                    reasons.append(f"stories_match_sources: completed or unproven remaining work "
                                   f"in story {index}: {assessment.get('completion_evidence', '')}")

    result["verdict"] = "pass" if not reasons else "fail"
    result["reasons"] = reasons
    result["_usage"] = {"prompt": usage.prompt_tokens, "completion": usage.completion_tokens}
    return result
