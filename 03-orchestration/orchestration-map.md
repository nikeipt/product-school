# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

_Run the default-to-simple check. Do you actually need subagents/a fleet? What's the real reason (separation of concerns · parallelism · independent validation · context-window pressure)? If not, say so and stop here._

Cortex remains one agent for pulling project data, drafting leadership updates, and proposing sprint stories. Separation of concerns, parallelism, and context-window pressure do not justify additional agents at the current scale. Cortex will add one independent validator to review both the leadership update and proposed sprint stories before they reach human review.

## 2. Topology

**Pattern:** Single agent + one sequential validator subagent.

```
[PM task]
    ↓
[Cortex: pull data + draft update + propose stories]
    ↓
[Independent Validator]
    ├─ Pass → [Human review checkpoint]
    └─ Fail → [Cortex revises once]
                    ↓
             [Independent Validator]
                    ├─ Pass → [Human review checkpoint]
                    └─ Fail → [Block + escalate to human]
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| Cortex | Pull project data, draft the leadership update, propose sprint stories, and perform one requested revision | Main M2 loop |
| Independent Validator | Check both outputs against the five approved rules and return a pass or a specific failure | Validation loop |

## 4. Communication & hand-offs

The agents use a structured in-process handoff; MCP and A2A are not required at the current scale.

Cortex sends the original task, project ID, retrieved source evidence, leadership-update draft, proposed sprint stories, queue cap, and revision number. The validator returns a structured verdict containing `verdict`, `failed_rule`, `problem`, `evidence`, and `required_correction`.

## 5. The validator

- **What the critic checks:**
  1. Every factual claim, metric, date, PR, and issue matches the source data.
  2. Every proposed sprint story is traceable to the project's PRD, roadmap, or current issues.
  3. The update and proposed stories relate to the correct project.
  4. No confidential content or unauthorized commitments appear.
  5. The story batch remains within the queue cap and stops for human review.
- **Fail action:** On the first failure, return the output to Cortex with the failed rule and reason for one revision. If the revised output fails validation again, block it and escalate to a human.
- **Revision cap:** Maximum one revision attempt.
- **Pass action:** Advance the validated output to the human-review checkpoint. Nothing is auto-sent.

## 6. State: shared vs isolated

**Shared:** the original PM task, project ID, retrieved source evidence, leadership-update draft, proposed sprint stories, queue cap, and revision number.

**Isolated:** Cortex's internal reasoning, unrelated conversation history, and system instructions; the validator's internal reasoning and system instructions. Relevant user constraints are extracted into the structured handoff rather than sharing raw history. Shared policies live in a separate version-controlled rules source. A human may inspect saved traces and configurations for debugging without adding them to the normal agent handoff.

## 7. Cost & latency budget

A normal run adds one independent critic call. The measured clean run completed in approximately 11 seconds and cost $0.0017. A failed validation permits one Cortex revision and a second critic call; the measured worst-case run completed in approximately 16 seconds and cost $0.0028. After one revision, the workflow blocks and escalates. These measured limits provide the starting bound to enforce in Module 5.
