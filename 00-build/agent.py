"""Cortex, a minimal, explicit agent loop you (and your coding agent) can read end
to end. This is the agent you ship: your PM chief-of-staff. You build it by
directing your coding agent (Claude Code / Cursor / Codex) to shape this file. You
never have to hand-write it.

Every bound the course talks about is visible right here in code, not buried in a
framework: the max-iteration counter, the cost cap, the revision cap, the
stop/escalate conditions, the auto-queue cap, and the absence of any publish tool.

Usage (ask your coding agent to run these for you, or run them yourself):
    python agent.py                # runs the happy-path task (weekly status update)
    python agent.py missing-data   # the stuck/escalate case
    python agent.py jailbreak       # the prompt-injection refusal case

Every run ends by showing the drafted status update in a FINAL STATUS UPDATE block
(or LAST DRAFT, held, if a bound trips), and saves it to run-output/. That file is
always a draft held for a human, it is never posted, there is no publish tool.

Requires OPENAI_API_KEY in your environment (see .env.example). Model and bounds
are read from env so you can tune them, that tuning is your M5 deliverable.

The loop is deliberately transparent (hand-written tool-calling on the openai
client) so a grader can see the machinery. Keep the bounds explicit if you rework it.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from openai import OpenAI

import tools
from critic import review
from budget import BudgetClient, BudgetExceeded
from prompts import CORTEX_SYSTEM

try:  # load .env if python-dotenv is installed; harmless if it isn't
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Bounds (your M5 deliverable: tune these and justify them) ----------------
MODEL = os.environ.get("CORTEX_MODEL", "gpt-4o-mini")
MAX_ITERATIONS = int(os.environ.get("CORTEX_MAX_ITERATIONS", "8"))
MAX_REVISIONS = int(os.environ.get("CORTEX_MAX_REVISIONS", "2"))
COST_CAP_USD = float(os.environ.get("CORTEX_COST_CAP_USD", "0.50"))
MAX_QUEUE_ITEMS = int(os.environ.get("CORTEX_MAX_QUEUE_ITEMS", "10"))
TOOL_RETRY_ATTEMPTS = 3
MAX_NO_PROGRESS_ITERATIONS = 2
# Rough $ per 1M tokens for your chosen model, set to match its pricing.
PRICE_IN = float(os.environ.get("CORTEX_PRICE_IN_PER_M", "0.15"))
PRICE_OUT = float(os.environ.get("CORTEX_PRICE_OUT_PER_M", "0.60"))

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_project", "description": "Look up a project by its ID (status, flags, linked PRD).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"}}, "required": ["project_id"]}}},
    {"type": "function", "function": {
        "name": "get_activity",
        "description": "Pull recent engineering activity for a project (merged PRs, open issues, Sev-1s).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"}}, "required": ["project_id"]}}},
    {"type": "function", "function": {
        "name": "search_past_updates",
        "description": "Search previous status updates and decisions for tone and precedent.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_roadmap",
        "description": "Return the roadmap. Some items are flagged confidential/embargoed.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_norms", "description": "Return the team norms / PM playbook the agent must follow.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "propose_stories",
        "description": "Queue a set of backlog stories for human approval (creates nothing; rejected above the item cap).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"},
            "stories": {"type": "array", "items": {"type": "string"}},
            "reason": {"type": "string"}}, "required": ["project_id", "stories"]}}},
]


class Bounds:
    """Tracks spend and trips the cost cap. This is enforced OUTSIDE the model."""

    def __init__(self):
        self.cost = 0.0

    def add(self, usage) -> None:
        self.cost += (usage.prompt_tokens * PRICE_IN
                      + usage.completion_tokens * PRICE_OUT) / 1_000_000

    def over_cap(self) -> bool:
        return self.cost >= COST_CAP_USD


OUTPUT_DIR = Path(__file__).parent / "run-output"


def banner(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def call_tool_with_retries(name: str, args: dict) -> dict:
    """Retry temporary tool failures, then return a detectable stuck result."""
    for attempt in range(1, TOOL_RETRY_ATTEMPTS + 1):
        try:
            return tools.TOOLS[name](**args)
        except Exception as exc:  # A real connector would narrow this to retryable errors.
            print(f"\nTOOL {name} attempt {attempt}/{TOOL_RETRY_ATTEMPTS} failed: "
                  f"{type(exc).__name__}")
            if attempt == TOOL_RETRY_ATTEMPTS:
                return {
                    "error": "tool_retrieval_failed",
                    "tool": name,
                    "attempts": TOOL_RETRY_ATTEMPTS,
                    "exception": type(exc).__name__,
                }


def validate_status_call(status: str | None, project: dict | None,
                         activity: dict | None) -> dict:
    """Enforce objective traffic-light policy in code, not model judgement."""
    status = str(status or "").lower()
    if status not in {"green", "yellow", "red"}:
        return {"verdict": "fail", "reason": "structured status is missing or invalid"}
    if not project or not activity:
        return {"verdict": "fail", "reason": "status evidence was not retrieved"}

    flags = project.get("flags", [])
    items = activity.get("activity", [])
    has_sev1 = any(str(item.get("severity", "")).lower() == "sev-1"
                   for item in items)
    explicitly_on_track = project.get("status") == "on_track"

    if explicitly_on_track and not flags and not has_sev1:
        if status != "green":
            return {
                "verdict": "fail",
                "reason": ("authoritative status is on_track with no flags or Sev-1; "
                           f"draft reported {status}"),
            }
        return {
            "verdict": "pass",
            "reason": ("Green is supported by project.status=on_track, no flags, "
                       "and no Sev-1 activity"),
        }

    if status == "green" and (flags or has_sev1):
        return {
            "verdict": "fail",
            "reason": "Green is blocked by project flags or Sev-1 activity",
        }
    return {"verdict": "pass", "reason": "status does not violate an objective rule"}


def validate_operational_checks(result: dict, outcome: str,
                                project: dict | None, stories_requested: bool,
                                stories_queued: bool,
                                tools_called: list[str]) -> dict:
    """Validate objective workflow facts from structured state and the tool trace."""
    allowed_tools = {
        schema["function"]["name"] for schema in TOOL_SCHEMAS
    }
    forbidden_tools = sorted(set(tools_called) - allowed_tools)
    expected_project_id = project.get("project_id") if project else None
    reported_project_id = result.get("project_id")

    checks = {
        "correct_project": (
            outcome == "escalate" or
            bool(expected_project_id) and reported_project_id == expected_project_id
        ),
        "requested_outputs_present": (
            outcome == "escalate" or
            bool(str(result.get("leadership_update", "")).strip()) and
            (not stories_requested or (
                stories_queued and
                result.get("story_proposal_status") == "queued_for_approval"
            ))
        ),
        "no_unauthorised_action": not forbidden_tools,
    }
    reasons = []
    if not checks["correct_project"]:
        reasons.append(
            f"reported project {reported_project_id!r} does not match "
            f"retrieved project {expected_project_id!r}")
    if not checks["requested_outputs_present"]:
        reasons.append("required draft or queued story proposal status is missing")
    if forbidden_tools:
        reasons.append(f"forbidden tools were called: {', '.join(forbidden_tools)}")
    return {
        **checks,
        "verdict": "pass" if all(checks.values()) else "fail",
        "reasons": reasons,
    }


def emit_deliverable(which: str, draft: str, *, accepted: bool,
                     reason: str, cost: float) -> None:
    """Surface AND persist Cortex's drafted status update so it can't get lost in
    the scroll-back. This is still a DRAFT held for human review, never a post,
    there is no publish tool, and an escalated run is held on purpose.

    Runs on every exit: an accepted pass prints the FINAL update; a bound trip or
    escalation prints the LAST draft it managed to write plus why it was held.
    """
    saved_path = None
    if draft.strip():
        OUTPUT_DIR.mkdir(exist_ok=True)
        saved_path = OUTPUT_DIR / f"status-update-{which}.md"
        state = "accepted by validator" if accepted else "HELD, escalated"
        saved_path.write_text(
            f"<!-- Cortex draft, {state}; NOT posted. Run cost ~ ${cost:.4f}. -->\n"
            f"<!-- {reason} -->\n\n{draft.rstrip()}\n", encoding="utf-8")

    banner("FINAL STATUS UPDATE (draft, validator-approved, NOT posted)" if accepted
           else "LAST DRAFT (held, NOT posted, escalated to a human)")
    if draft.strip():
        print(draft.rstrip())
    else:
        print("(Cortex stopped before it produced a draft, nothing to show.)")
    if not accepted:
        print(f"\nWhy it was held: {reason}")

    if saved_path:
        print(f"\nSaved draft -> {saved_path.relative_to(Path(__file__).parent)}  "
              f"(for your review, nothing was posted)")


def run(which: str = "happy") -> None:
    client = BudgetClient(OpenAI(max_retries=0), cap=COST_CAP_USD, model=MODEL)
    bounds = Bounds()
    task = tools.get_task(which)
    if "error" in task:
        print(task)
        return

    banner(f"CORTEX RUN, fixture: task-{which}  (auto-queue cap {MAX_QUEUE_ITEMS} items)")
    print(task["body"])

    messages = [
        {"role": "system", "content": CORTEX_SYSTEM},
        {"role": "user", "content": f"PM task brief:\n\n{task['body']}"},
    ]
    source_log: list[str] = [task["body"]]
    revisions = 0
    last_draft = ""
    stories_requested = "propos" in task["body"].lower() and "stor" in task["body"].lower()
    stories_queued = False
    evidence_seen: set[str] = set()
    no_progress_iterations = 0
    primary_project: dict | None = None
    primary_activity: dict | None = None
    tools_called: list[str] = []

    for step in range(1, MAX_ITERATIONS + 1):
        if bounds.over_cap():
            reason = f"cost cap ${COST_CAP_USD} hit at ${bounds.cost:.4f}"
            banner(f"BOUND TRIPPED, {reason}. Halting and escalating to a human.")
            emit_deliverable(which, last_draft, accepted=False,
                             reason=reason, cost=bounds.cost)
            return

        try:
            resp = client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOL_SCHEMAS,
                response_format={"type": "json_object"})
        except BudgetExceeded as exc:
            emit_deliverable(which, last_draft, accepted=False,
                             reason=str(exc), cost=float(client.spent))
            return
        bounds.add(resp.usage)
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            found_new_evidence = False
            for call in msg.tool_calls:
                fn = call.function.name
                tools_called.append(fn)
                args = json.loads(call.function.arguments or "{}")
                result = call_tool_with_retries(fn, args)
                source_log.append(f"{fn}({args}) -> {json.dumps(result)}")
                print(f"\n[step {step}] TOOL {fn}({args})")
                print(f"          -> {json.dumps(result)[:300]}")
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": json.dumps(result)})

                evidence_key = json.dumps(
                    {"tool": fn, "args": args, "result": result}, sort_keys=True)
                if evidence_key not in evidence_seen:
                    evidence_seen.add(evidence_key)
                    found_new_evidence = True

                if result.get("status") == "queued_for_approval":
                    stories_queued = True

                if fn == "get_project" and "error" not in result and primary_project is None:
                    primary_project = result
                if (fn == "get_activity" and "error" not in result and
                        (primary_project is None or
                         result.get("project_id") == primary_project.get("project_id"))):
                    primary_activity = result

                if result.get("error") == "project_not_found":
                    reason = (f"required project {result.get('project_id', 'unknown')} "
                              "was not found in the authoritative project source")
                    banner(f"STUCK, {reason}. Halting and handing off to a human.")
                    emit_deliverable(which, last_draft, accepted=False,
                                     reason=reason, cost=bounds.cost)
                    return

                if result.get("error") == "tool_retrieval_failed":
                    reason = (f"{fn} failed after {TOOL_RETRY_ATTEMPTS} attempts "
                              f"({result.get('exception', 'unknown error')})")
                    banner(f"STUCK, {reason}. Halting and handing off to a human.")
                    emit_deliverable(which, last_draft, accepted=False,
                                     reason=reason, cost=bounds.cost)
                    return

                if result.get("status") == "rejected":
                    reason = (f"tool {fn} rejected the requested action: "
                              f"{result.get('error', 'unspecified reason')}")
                    banner(f"ESCALATE, {reason}. Halting for a human decision.")
                    emit_deliverable(which, last_draft, accepted=False,
                                     reason=reason, cost=bounds.cost)
                    return

            no_progress_iterations = 0 if found_new_evidence else no_progress_iterations + 1
            if no_progress_iterations >= MAX_NO_PROGRESS_ITERATIONS:
                reason = (f"no new evidence or progress across "
                          f"{MAX_NO_PROGRESS_ITERATIONS} consecutive iterations")
                banner(f"STUCK, {reason}. Halting and handing off to a human.")
                emit_deliverable(which, last_draft, accepted=False,
                                 reason=reason, cost=bounds.cost)
                return
            continue

        # No tool calls => Cortex produced its structured result. Validate it.
        try:
            result_payload = json.loads(msg.content or "")
        except (json.JSONDecodeError, TypeError):
            reason = "Cortex returned an invalid structured result"
            if revisions >= MAX_REVISIONS:
                emit_deliverable(which, last_draft, accepted=False,
                                 reason=reason, cost=bounds.cost)
                return
            revisions += 1
            print(f"\n-> structured result invalid; revision "
                  f"{revisions}/{MAX_REVISIONS}")
            messages.append(msg)
            messages.append({"role": "user", "content":
                             f"{reason}. Return the required JSON object."})
            continue

        outcome = str(result_payload.get("outcome", "")).lower()
        reported_status = result_payload.get("status")
        proposed = str(result_payload.get("leadership_update", "")).strip()
        if reported_status and proposed:
            proposed = f"**Status:** {str(reported_status).title()}\n\n{proposed}"
        last_draft = proposed
        print(f"\n[step {step}] STRUCTURED RESULT:")
        print(json.dumps(result_payload, indent=2))
        print(f"\n[step {step}] RENDERED OUTPUT:\n{proposed}")

        operational_verdict = validate_operational_checks(
            result_payload, outcome, primary_project, stories_requested,
            stories_queued, tools_called)
        banner("OBJECTIVE WORKFLOW CHECKS")
        print(json.dumps(operational_verdict, indent=2))
        if operational_verdict["verdict"] == "fail":
            reason = "objective workflow checks failed: " + "; ".join(
                operational_verdict["reasons"])
            emit_deliverable(which, last_draft, accepted=False,
                             reason=reason, cost=bounds.cost)
            return

        if outcome not in {"done", "escalate"}:
            status_verdict = {
                "verdict": "fail",
                "reason": "structured outcome must be done or escalate",
            }
        elif outcome == "escalate":
            status_verdict = {"verdict": "pass", "reason": "human escalation requested"}
        else:
            status_verdict = validate_status_call(
                reported_status, primary_project, primary_activity)
        banner("OBJECTIVE POLICY CHECK, project status")
        print(json.dumps(status_verdict, indent=2))
        if status_verdict["verdict"] == "fail":
            if revisions >= MAX_REVISIONS:
                reason = f"objective status check failed: {status_verdict['reason']}"
                banner(f"REVISION CAP hit ({MAX_REVISIONS}). Escalating to a human.")
                emit_deliverable(which, last_draft, accepted=False,
                                 reason=reason, cost=bounds.cost)
                return
            revisions += 1
            print(f"\n-> objective policy rejected; revision "
                  f"{revisions}/{MAX_REVISIONS}")
            messages.append(msg)
            messages.append({"role": "user", "content":
                             "The objective status policy rejected the draft: "
                             f"{status_verdict['reason']}. Correct it or escalate."})
            continue

        banner("CRITIC, independent validation")
        try:
            critic_sources = (
                "\n".join(source_log) +
                "\n\nAUTHORITATIVE OBJECTIVE WORKFLOW CHECKS -> " +
                json.dumps(operational_verdict) +
                "\nAUTHORITATIVE OBJECTIVE STATUS CHECK -> " +
                json.dumps(status_verdict))
            verdict = review(client, MODEL, proposed, critic_sources)
        except BudgetExceeded as exc:
            emit_deliverable(which, last_draft, accepted=False,
                             reason=str(exc), cost=float(client.spent))
            return
        # Estimate critic spend too.
        bounds.cost += (verdict["_usage"]["prompt"] * PRICE_IN
                        + verdict["_usage"]["completion"] * PRICE_OUT) / 1_000_000
        print(json.dumps({k: v for k, v in verdict.items() if k != "_usage"}, indent=2))

        if verdict["verdict"] == "pass":
            if outcome == "escalate":
                requested_escalation = str(
                    result_payload.get("escalation_reason") or
                    "Cortex requested human review")
                banner(f"HITL ESCALATION, {requested_escalation}. "
                       f"Nothing posted, no commitments made. "
                       f"Run cost ≈ ${bounds.cost:.4f}")
                emit_deliverable(which, proposed, accepted=False,
                                 reason=requested_escalation, cost=bounds.cost)
                return

            if stories_requested and not stories_queued:
                reason = "requested story proposals were not queued for human review"
                if revisions >= MAX_REVISIONS:
                    banner(f"REVISION CAP hit before the success conditions were met. "
                           f"Escalating to a human. Run cost ≈ ${bounds.cost:.4f}")
                    emit_deliverable(which, proposed, accepted=False,
                                     reason=reason, cost=bounds.cost)
                    return
                revisions += 1
                print(f"\n-> success condition not met; revision "
                      f"{revisions}/{MAX_REVISIONS}: {reason}")
                messages.append(msg)
                messages.append({"role": "user", "content":
                                 f"The validator passed the draft, but {reason}. "
                                 "Queue the requested stories or escalate."})
                continue

            banner(f"HITL CHECKPOINT, status update + any proposed stories queued for "
                   f"your review. Nothing posted, no commitments made. "
                   f"Run cost ≈ ${bounds.cost:.4f}")
            emit_deliverable(which, proposed, accepted=True,
                             reason="validator passed", cost=bounds.cost)
            return

        reason = "critic checklist failed: " + "; ".join(verdict["reasons"])
        banner("CRITIC CHECKLIST FAILED. Holding for human review instead of "
               f"starting a rewrite loop. Run cost ≈ ${bounds.cost:.4f}")
        emit_deliverable(which, last_draft, accepted=False,
                         reason=reason, cost=bounds.cost)
        return

    banner(f"MAX ITERATIONS ({MAX_ITERATIONS}) reached without finishing. "
           f"Escalating. Run cost ≈ ${bounds.cost:.4f}")
    emit_deliverable(which, last_draft, accepted=False,
                     reason=f"max iterations ({MAX_ITERATIONS}) reached",
                     cost=bounds.cost)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "happy")
