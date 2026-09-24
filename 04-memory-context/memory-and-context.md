# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

Each run receives, in priority order:

1. **Team norms**, the whole playbook, loaded first (system prompt). Hard rules; must never be missed.
2. **Task brief**, whole. It's the job.
3. **Roadmap section** for this project only. No confidential detail.
4. **Activity** for this project, fetched fresh every run.
5. **Past updates**, the last 2, plus all active decisions: for the format and the prior metric.

If the budget runs short, cut from the bottom up. Norms and brief are never cut.

## 2. Retrieve vs. long-context: per source

For each data source, decide: **retrieve** (narrow a large/changing corpus to the relevant slice) or **long-context** (just include a bounded set you can reason over).

| Source | Size / volatility | Decision | Why (deciding factor) |
|---|---|---|---|
| `get_activity` | Grows; changes daily | Retrieve | **Volatility:** "this will change every run" |
| `search_past_updates` | Unbounded; grows weekly | Retrieve: last 2 updates + all active decisions | **Size:** unbounded; old decisions stay binding until superseded |
| `get_roadmap` | Medium; has confidential items | Retrieve: this project's section only | **Citation/audit:** confidential detail never enters the prompt; the confidential list comes from the norms |
| `get_norms` | Small, bounded; must stay current | Long-context, reloaded each run | **Size:** small and bounded, and every rule must always apply |
| `get_task` | One small, static doc | Long-context | "It's the task brief, you need it" |

## 3. Retrieval quality plan

_Which of these apply, and how? (This is what separates modern agentic retrieval from naive "embed → top-k → stuff".)_

| Source | Routing | Grading | Reranking | Self-verification | Caching | Failure it stops |
|---|---|---|---|---|---|---|
| `get_activity` | | ✅ | | ✅ | | Grading: mis-tagged PRs from other projects. Self-verification: claims no fetched item supports (e.g. "positively influenced activation") |
| `search_past_updates` | | | ✅ | | | An overruled decision outranking the current one |
| `get_roadmap` | | ✅ | | ✅ | | Grading: wrong section, or confidential lines in this project's section. Self-verification: a confidential name leaking from any source, including ones added later |

Every retrieved source has at least one move; no naive-RAG rows.

## 4. Memory map (your PM brain)

| Memory type | What Cortex stores | Scope / TTL | Read / write |
|---|---|---|---|
| **Working** (in-loop) | This run's retrieved data, draft, check results | Wiped at end of run: "don't pollute working memory" | Cortex reads and writes |
| **Episodic** (past runs) | Approved updates only | 12 weeks: "drafts might go in a wrong direction; approved ones are a working body" | Cortex reads; written only on human approval |
| **Semantic** (durable facts/prefs) | Stated style preferences only; changing facts stay in their sources | Until replaced, plus a 90-day review | Cortex reads; human writes |
| **Shared** (across agents) | Norms, confidential list, gold-standard update | Until a human changes them | Cortex and critic read; only a human writes |

Read/write scope follows the M1 agent line (a human approves and writes); TTLs feed M5 bounds.

## 5. Memory risks & mitigations

| Risk | Where it bites Cortex | Mitigation |
|---|---|---|
| **Drift** | Updates slowly change by copying the previous one | Gold-standard update in the norms: Cortex drafts from it, the critic checks against it |
| **Poisoning** | Malicious brief, or a wrong number copied forward | Only human-approved content is stored; briefs are data, not instructions. Relies on genuine review before approval |
| **Staleness** | Outdated preferences or prior metrics | Episodic 12-week TTL, 90-day preference review, changing facts read fresh each run |
| **PII / retention** | PR authors' names or pasted notes stored | Names stripped before storing, working memory wiped each run, confidential items blocked by the final check |
