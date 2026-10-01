# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

_Autonomy is a product decision per user, not one global setting._

| Segment | Desired autonomy | Why |
|---|---|---|
| PMs | Supervised — full validated draft, then human review | "If we find that there are gaps we'll increase the number of gates." |
| Engineering leads | Supervised — full validated draft, then human review | "Still need to review the output." |
| Executive stakeholders | Supervised — full validated draft, then human review | "They don't have time for gated drafts." |

Context pulled and language used in the update vary by segment. Human context selection and publication approval remain required under the M1 agent line.

## Trust Ladder

- **Current rung:** Supervised. "Let it produce the full validated draft and review at the end."
- **Eval gate to reach bounded-autonomous preparation:** Over four weeks with at least 20 supervised runs, achieve a pass rate of at least 95% for each of EV-1 (tool-call accuracy), EV-2 (recovery), EV-5 (unconfirmed date), and EV-6 (task completion), and 100% for EV-3 (safety / jailbreak) and EV-4 (confidential leak), using the M5 eval definitions. Publication and other human-owned decisions remain gated under the M1 agent line.
- **Why this gate:** "I imagine that there will be mistakes and additional gates and evals. This is the testing period to get it right and ensure reliability."
- **Clean incident record for the window:** Documented non-safety mistakes are permitted within the agreed pass thresholds, with corrective actions tracked. Any jailbreak, confidential leak, or unauthorised action fails the clean-window requirement.
- **Incident record so far:** The four-week observation window and its results have not yet been verified. This is an agreed gate, not an achieved result.

## Deployment plan

- **Runtime:** Managed platform supporting the M2 Friday 5 pm cron and Slack/Teams hooks. Nick chose this for less infrastructure and expected greater observability. Platform logs, runtime metrics and alerts must be supplemented with Cortex-level eval, escalation, cost and incident logging. This is a deployment plan; local mock fixtures and planned connectors must not be presented as live integrations.
- **Operator / on-call owner:** Nick Ngoh is the primary operator and accountable for Cortex's output. A technical lead will help troubleshoot, but nobody is assigned yet. Technical backup and the escalation route are open deployment gaps.
- **Rollback:** Pause new runs, preserve incident evidence, and keep failed-run output out of approved memory pending Nick's review. Investigate whether the failure is systemic; revert the prompt/version or disable the affected tool before resuming as appropriate. Nick: "I need to make sure it doesn't pollute future runs and see if these errors are systemic."
- **Monitoring:** Dashboard plus alerts for eval pass rates, escalation rate, cost per run and trust incidents; immediate alerts for safety failures or breached bounds. Nick: "This is how I'm familiar with modelling metrics and data." Dashboard and alert implementation are planned, not verified.

## ROI metrics (beyond adoption & tokens)

| Metric | Target | Capture |
|---|---|---|
| Outcome: drafts accepted without substantive edits | At least 95% over the four-week supervised pilot; drafts must meet Nick's quality gate | Record the human review decision and edit reason against each draft |
| Hands-on time saved | At least 90% compared with manual preparation | Establish a manual-time baseline; log context selection, review and correction time with Cortex |
| Cost-to-serve and payback | Recoup upfront build cost within six months; value Nick's time at $1/minute ($60/hour) | Track API/platform spend plus review and troubleshooting minutes per accepted draft; cumulative net savings = manual-work cost avoided minus ongoing human time and API/platform costs; compare with upfront build time at $1/minute plus upfront cash costs |
| Trust incidents | Zero safety incidents: confidential leaks, unauthorised actions or successful jailbreaks; log other errors and near misses separately | Maintain an incident register linked to each run, with severity, cause and corrective action |

Nick's rationale: "The whole purpose is to have me time to do this busy work. So it has to meet my quality gate and save me at least 90% of my time when doing this." He also wants to recoup the upfront work over a long enough period. For trust: "We can't have rogue actions on sensitive materials."

**Measurement gaps:** Upfront build time, manual preparation baseline, update frequency and platform pricing are not yet established, so six-month payback is a target, not a demonstrated result.

## Widen-autonomy decision rule

Increase preparation autonomy only after four weeks and at least 20 supervised runs meet every agreed M5 threshold, at least 95% of drafts are accepted without substantive edits, hands-on time falls by at least 90%, and no safety incidents occur. The six-month payback target is a separate ROI measure.

Passing the gate does not automatically remove an M1 approval requirement. The future exception-based review policy requires explicit revision of M1's every-draft review gate before activation; publication and other human-owned decisions remain gated.

## Governance & forward strategy

- **Compliance:** Pre-sanitised project data only. Remove personal identifiers, credentials, and confidential/embargoed material before model access. Retain only human-approved memory under M4's scope and retention rules. Nick: "Pre sanitised - less chance of an error or inappropriate pull of data."
- **Safety:** Current operation remains supervised. Human context selection, escalation decisions and publication approval remain required for everyone. Nick and the designated technical lead may disable new runs and revoke tokens; until a lead is assigned, Nick is the sole named owner. Nick: "We are the ones responsible for this." M5's `CORTEX_ENABLED=false` kill switch is documented as not yet enforced in the build.
- **Reliability:** Retain M5 bounds: maximum 3 iterations, tool failure retried once then flagged, maximum 5 stories per run, $0.50 per run and $2 per day, a 2-minute timeout, read-only access by default and single-use approval-scoped tokens. Preserve M3's one-revision validation cap and escalate on stuck work or unresolved evidence conflicts. M5 documents the timeout and daily cost cap as not yet enforced; other implementation claims require verification before deployment. If the model is unavailable, stop, preserve available evidence, mark the run incomplete and hand back to Nick for manual preparation. Nick remains responsible for the agent and its output.
- **Strategy:** Future bounded-autonomous scope is routine weekly-update preparation for PMs only; story proposals and publication are excluded. Plan toward exception-based review of qualifying validated drafts and sample audits, subject to the agreed pilot gate and explicit M1 revision. This future policy is not active. Qualifying scope, exception criteria, audit frequency and the detailed authority bounds still need definition before activation.
