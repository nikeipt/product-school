# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** Cron + hook

- Cron runs every Friday at 5 pm so the preparation work is completed ahead of time.
- A hook starts Cortex when I ask `@Cortex` in Slack or Teams for an update.
- A hook also starts Cortex when Person A sends a message containing "update" and refers to a known project. If the project is unclear, Cortex asks me before starting the full run.
- Cortex deduplicates hook events using the Slack or Teams event ID so one message cannot create two runs.

Cortex does not use a heartbeat because it does not need to check continuously. It does not use a goal loop because cron and hooks define how each run starts.

## 2. Goal / definition of done

One Cortex run is done when it has retrieved the required project data, drafted a grounded leadership update, proposed suitable backlog stories, passed independent validation, and queued everything for human review without publishing it.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | The critic returns `pass`; the leadership update and any story proposals are saved and queued for human review; nothing has been published or committed. | Stop successfully at the human-review checkpoint. |
| **Stuck / give up** | A required project or source is confirmed missing; a temporary retrieval failure continues after three attempts; or two consecutive iterations produce no new evidence or progress. | Stop, log what Cortex attempted, preserve the available evidence, and hand the run to a human. |
| **Escalate to human** | The request involves confidential or embargoed information; asks Cortex to publish, commit a date, approve work, or make another human-owned decision; contains conflicting evidence Cortex cannot resolve; a tool rejects an action such as exceeding the story cap; or the critic's revision limit is reached. | Stop the run, preserve the last safe draft and evidence, and state the decision the human needs to make. |

## 4. State

Cortex keeps state separately for each project and treats it as an index rather than a copy of the underlying material.

The index stores identifiers and links for:

- The last approved leadership update and reporting period
- Tickets referenced in previous updates
- Previously proposed stories and their human decisions
- The current trigger event, run status, evidence references, critic result, and retry count

Cortex retrieves the actual content from Jira, Confluence, the metrics dashboard, or another authoritative source only when needed for the current run. Information from one project must not enter another project's context.

## 5. The five things a loop can lean on

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Each new piece of work receives an isolated Git worktree on a branch named for the project and reporting period. Cortex may prepare the draft there, but a human controls merging and publishing. |
| **Skills** (reusable capabilities) | Reusable skills retrieve project evidence, draft the standard leadership update, and propose backlog stories consistently. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | Cortex currently uses local mock fixtures. Jira, Confluence, the metrics dashboard, and Slack/Teams are planned connectors and must not be described as live until they are wired and tested. |
| **Subagents** (independent check when the loop can't grade itself) | An independent critic validates the draft. The detailed orchestration design will be completed in Module 3. |
| **State tracking** | Per-project state stores references and operational metadata. Authoritative content remains in the connected source systems and is retrieved when required. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

[`../00-build/agent.py`](../00-build/agent.py)
