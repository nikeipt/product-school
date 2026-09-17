"""Independent validator (M3) with a fixed, five-check POC contract."""

from __future__ import annotations

import json

from prompts import CRITIC_SYSTEM


def review(client, model: str, proposed_output: str, source_data: str) -> dict:
    """Run the fixed checklist; code computes pass/fail from its five booleans."""
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM},
            {"role": "user", "content":
                f"SOURCE DATA Cortex used:\n{source_data}\n\n"
                f"CORTEX PROPOSED OUTPUT:\n{proposed_output}"},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    usage = resp.usage
    try:
        result = json.loads(resp.choices[0].message.content)
    except (json.JSONDecodeError, TypeError):
        result = {}

    check_names = (
        "correct_project",
        "claims_match_sources",
        "no_confidential_content",
        "no_unauthorised_action",
        "requested_outputs_present",
    )
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

    result["verdict"] = "pass" if not malformed and not failed else "fail"
    result["reasons"] = reasons
    result["_usage"] = {"prompt": usage.prompt_tokens, "completion": usage.completion_tokens}
    return result
