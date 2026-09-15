# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner, by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| _Pull project state + recent GitHub/Jira activity_ | H | L | H | Below | · |
| _Draft the weekly leadership status update_ | H | M | M | Below | spot-check |
| _Propose next sprint's stories from the PRD (within cap)_ | M | M | M | Below | spot-check |
| _Post the update to a channel / commit a ship date_ | L | H | M | Above | required |
| _Mark a launch gate green / merge or close a ticket_ | L | H | M | Above | required |
| _…_ | | | | | |

## Steps 2–3: Agreed workflow scores and ownership

These are Nick's agreed scores and final Step 3 decisions. The example table above is retained as template reference. HITL means human-in-the-loop: Cortex performs the delegated work, with the stated human review or approval gate. Below with required HITL does not mean independent authority.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| Pull project state + activity | H | L | H | Below — agent owns | No; authorised read-only access |
| Decide relevant context | H | M | L | Above — human owns | Human selects relevant context |
| Draft the update | H | L | M | Below — human approval | Required; Cortex drafts, human reviews before use |
| Decide tone / commitment level | H | M | L | Below — human approval | Required before publication |
| Flag risks / potential escalations | H | H | M | Below — human approval | Required; human checks flags and possible omissions |
| Choose what to escalate | L | H | M | Above — human owns | Human decides what warrants escalation |
| Propose a capped story batch | H | L | M | Below — human approval | Required before proposals become work |
| Post an update | L | H | H | Below — human approval | Required; exact message and audience approved before posting |
| Approve a company-wide update | L | H | L | Above — human owns | Human makes the final approval decision |

### Scoring notes

- Nine actions are listed because posting and company-wide approval were split into separate actions.
- Flag risks, high blast radius — Nick: "Risk that are missed derail projects and can affect multiple teams".
- Choose what to escalate, low reversibility — Nick: "Once you've escalated it's difficult to walk it back". This score includes the escalation itself.
- Tone / commitment reversibility is scored before publication; posting is scored separately.
- Company-wide approval reversibility assumes approval triggers publication.

## Agent anatomy (sketch)

- **Model:** Use a strong default model. Escalate to a stronger model when data reports conflict or the model still misses a clear task requirement after one revision. Human approval gates remain in place.
- **Tools:** Authorised project/activity lookup, past-update search, roadmap and team-norm lookup, capped story proposals, and posting only after a human approves the exact message and audience.
- **Memory:** Retain approved durable context plus an evaluation history. Working memory includes the roadmap, decisions, team norms, approved writing examples, and confirmed preferences used to produce drafts. Evaluation history retains retrieved source snapshots, context selected or excluded, drafts and revisions, model/version used, escalation triggers, human approvals or edits, and posting outcomes. Record observable inputs, outputs, and decisions, not hidden internal reasoning. Keep unverified conclusions labelled as unverified.
- **Loop:** _placeholder, defined in M2 loop-spec.md_
- **Bounds:** _placeholder, defined in M5 bounds-and-evals.md_
- **Evals:** _placeholder, defined in M5 bounds-and-evals.md_

## The golden rule, applied

1. **Pull project state + activity:** Pulling project state and activity sits below the line because retrieval is highly reversible, authorised read-only access keeps the blast radius low, and results are easy to verify against sources; the deciding factor is the limited impact of read-only access.

2. **Decide relevant context:** Deciding relevant context sits above the line because selection is highly reversible, has a medium blast radius, and has low measurability; the deciding factor is blast radius, because choosing the wrong context impacts decision-making.

3. **Draft the update:** Cortex drafts the update using previous writing styles as a reference, with human review because drafts are highly reversible, have a low blast radius before publication, and have medium measurability; the deciding factor for the review gate is medium measurability, since matching a writing style does not guarantee the intended message.

4. **Decide tone / commitment level:** Cortex proposes tone and commitments with human approval because wording is highly reversible before publication, has a medium blast radius, and has low measurability; the deciding factor is low measurability, so a human must confirm the intended tone and promises before publication.

5. **Flag risks:** Cortex flags risks with human review because flags are highly reversible, have a high blast radius, and have medium measurability; the deciding factor is high blast radius, because missed risks can derail projects and affect multiple teams, so review must check both flags and possible omissions.

6. **Choose what to escalate:** Choosing what to escalate stays human-owned because escalation has low reversibility, a high blast radius, and medium measurability; the deciding factor is low reversibility, because once an escalation is made, it is difficult to walk back.

7. **Propose a capped story batch:** Cortex proposes a capped story batch with human approval because proposals are highly reversible, have a low blast radius while gated by review, and have medium measurability; the deciding factor for approval is medium measurability, because generating plausible alternatives does not establish which work should proceed.

8. **Post an update:** Cortex posts only after a human approves the exact message and audience because posting has low reversibility, a high blast radius, and high measurability; the deciding factor is low reversibility, because verifying delivery cannot undo what others have read or acted on.

9. **Approve a company-wide update:** Company-wide approval stays human-owned because it has low reversibility, a high blast radius, and low measurability; the deciding factor is high blast radius, because the message can affect decisions across the company and cannot reliably be walked back.

## Hardest call

The hardest call was deciding relevant context. Context is hard to measure and is constantly evolving. While tempting to delegate because it is a big part of the work, I think it falls in the domain of the human.
