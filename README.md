# Cortex: PM Chief-of-Staff Agent

Product School · Agentic Loops for PMs · Nick Ngoh

Cortex prepares leadership updates and capped sprint-story proposals from the selected project’s evidence. It checks outputs in code, runs a separate validator and holds all output for human review. **Current rung: supervised.** This is a local mock-data prototype; live integrations and production deployment are planned.

## Submission package

- [HTML pitch deck](06-autonomy/pitch.html) — self-contained, with embedded evidence images; open in a browser, navigate with arrow keys, or print.
- [Working prototype and run screenshots](06-autonomy/prototype.md)
- [Loop specification](02-loop-design/loop-spec.md)
- [Orchestration map](03-orchestration/orchestration-map.md)
- [Build insights](06-autonomy/build-insights.md)
- [Production, autonomy and ROI plan](06-autonomy/production-and-autonomy.md)
- Supporting policies: [agent line](01-agent-line/agent-line-map.md), [context and memory](04-memory-context/memory-and-context.md), [bounds and evals](05-bounds-evals/bounds-and-evals.md).

## Implemented behavior

Code resolves a canonical project ID, retrieves five approved sources once, and passes that fixed evidence into tool-free drafting. Update and stories arrive together. References, project identity, status and queue bounds are checked in code; the validator checks content support, remaining story scope, confidentiality and commitments. One revision is allowed; another failure blocks and escalates. There is no publication or tracker-mutation tool.

Model: OpenAI `gpt-4o-mini`. Maximum 3 drafting iterations, 1 revision, 5 stories and $0.50 USD per run shared with the critic. Retrieval failures receive one retry. Sanitisation blocks known confidential course fixtures and strips configured identifier fields; this does not establish safe handling of arbitrary real data.

## Run locally

From `00-build`, create a virtual environment if needed and install `requirements.txt`. Create `.env` from `.env.example` only if it does not already exist, then supply your own `OPENAI_API_KEY`. Never commit the key. A live run sends mock task and retrieved evidence to the configured OpenAI API endpoint; obtain authorization for any real data.

```powershell
$env:PYTHONIOENCODING = 'utf-8'
& '.\.venv\Scripts\python.exe' -u agent.py happy
```

Other fixtures: `agent.py missing-data` and `agent.py jailbreak`. From the repo root, run offline checks with:

```powershell
& '.\00-build\.venv\Scripts\python.exe' -m unittest discover -s 00-build -p 'test_*.py'
```

## Evidence and limits

The prototype contains screenshots for happy-path review, critic rejection, grounding versus missing source, jailbreak refusal, a cost-bound stop and an end-to-end run. The happy-path row shares the grounded-answer screenshot and explicitly records its current rerun date. The rejection test deliberately injects unsupported referral work; real validator calls reject it and escalate after one revision. The cost probe uses a temporary $0.001 cap to block the first API call; it does not demonstrate an observed runaway. Historical transcripts and current reruns are labelled separately.

Known validator misses include unsupported causal claims and unverified Vega notes entering a held Northstar draft. A validator pass does not replace human review. The 2-minute timeout, shared $2/day cap and kill switch are not enforced. Live connectors, trigger deduplication, isolated run worktrees, durable memory/retention, JIT tokens, dashboard and alerts are design commitments, not production capabilities.

## Trust gate and rollout

PMs, engineering leads and executives receive a full validated draft followed by human review. Context and language vary by segment; publication approval remains required.

Widen routine PM weekly-update preparation only after **four weeks and at least 20 supervised runs** achieve at least 95% for each EV-1, EV-2, EV-5 and EV-6, 100% for EV-3 and EV-4, at least 95% of drafts accepted without substantive edits, at least 90% less hands-on time and zero safety incidents. The gate has not been achieved. Story proposals and publication are outside the proposed future autonomous scope; exception criteria, audits and an explicit M1 policy revision are still required.

Managed deployment is planned. Nick Ngoh is accountable; a technical backup and escalation route remain unassigned. Pause failures, preserve evidence and prevent failed drafts from entering approved memory. Model outages return work to Nick.

## ROI target

Recoup build costs within six months, valuing Nick’s time at $1/minute ($60/hour). Net savings compare avoided manual work against ongoing review/troubleshooting time and API/platform costs. Manual baseline, upfront build effort, run frequency and platform pricing remain unmeasured; payback is a target, not a result.

## Submission status

Deck and documentation prepared for review. Commit, push and learning-platform submission remain pending explicit authorization. The original course README is retained in `06-autonomy/submission/README-template-original.md`.
