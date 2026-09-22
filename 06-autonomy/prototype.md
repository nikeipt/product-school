# Prototype: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 1, the working agent demo
>
> ✅ **What this validates:** the agent actually runs end to end, by the end you'll have proven it with real screenshots of your Cortex across the six required moments (M2 to M6).

## What it does

_One paragraph: the agent in action, end to end._

## How you built it

- **Coding agent:** _which one you directed (Claude Code / Cursor / Codex)_
- **Model + bounds:** _model used, max iterations, cost cap, queue cap_
- **Repo / config:** _path to your build in `00-build/`_
- **Live link:** _[shareable URL, optional bonus]_

## Screenshots (required, collected M2 to M6)

Real screenshots of *your* Cortex running. These are the `00-build/CORTEX-ANATOMY.md` set and they are required, a link alone is not enough.

| # | Screenshot | What it shows | From |
|---|---|---|---|
| 1 | _[img]_ | happy-path run: a real drafted update + the HITL checkpoint (queued, not posted) | M2 |
| 2 | [Transcript below](#m3-critic-rejection-transcript) | the critic rejecting an unsupported sprint story, returning it once, then escalating at the revision cap | M3 |
| 3 | _[img]_ | a grounded update citing pulled activity + a caught hallucination | M4 |
| 4 | _[img]_ | jailbreak refused + escalated | M5 |
| 5 | _[img]_ | an iteration/cost/queue bound halting a runaway | M5 |
| 6 | _[img]_ | end-to-end run | M6 |

### M3 critic-rejection transcript

Live run caption: the independent validator rejected an unsupported referral-programme story, returned it to Cortex for the single permitted revision, then blocked and escalated when the structured story proposal still failed validation. Nothing was posted.

```text
CRITIC, independent validation
{
  "claims_match_sources": true,
  "stories_match_sources": false,
  "no_confidential_content": true,
  "no_unauthorised_commitments": true,
  "failure": {
    "check": "stories_match_sources",
    "draft_claim": "Launch a referral rewards programme",
    "source_evidence": "PRD-Northstar-v3 includes the activation checklist, instrumentation, empty-state guidance, contextual tips, and a day-2 milestone email.",
    "mismatch": "The proposed referral programme is not in the PRD and is outside the supported scope."
  },
  "verdict": "fail"
}

CRITIC CHECKLIST FAILED. Returning to Cortex for revision 1/1.

CRITIC, independent validation
{
  "stories_match_sources": false,
  "verdict": "fail"
}

CRITIC CHECKLIST FAILED AGAIN. REVISION CAP hit (1); escalating to a human.
LAST DRAFT: held, NOT posted, escalated to a human.
```

## How to run it

_Minimal steps for someone to reproduce the demo (env vars, and the command or the coding-agent prompt you used)._
