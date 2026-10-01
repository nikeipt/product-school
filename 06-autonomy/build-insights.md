# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

Anticipating where failure could happen was difficult. Using agents is new, so there were many unexpected failures. Designing the right system to avoid future failures without creating too much overhead was a challenge.

A particularly difficult failure point was diagnosing what went wrong when the agent ran. It was hard to trace the failure back to its underlying cause and establish whether a change would prevent the same class of failure in future runs, rather than just patch the output from one run. Getting past this required testing one fix at a time and checking whether it addressed the systemic cause.

Choosing the right gates and understanding how to evaluate the results were also difficult. Memory was tricky too: differentiating working context from long-term memory.

## Learning

- I now understand when to use subagents. The framing helped me distinguish parallel activities from situations that need orchestration. I also have a clearer idea of where to get leverage: subagents, memory and tool selection.
- The agent line in Module 1 was a useful rubric for deciding where agents can operate and where a human needs to stay in the loop.
- The autonomy lesson was useful, but applying it at an enterprise level is still tricky.

## Aha moment

My biggest aha moment was seeing the diagram of the five tools agents can access. I work best with mental models. From there, I could start breaking these down to understand how to apply leverage.

Agents are relatively new. It is difficult to understand the boundary conditions in which they operate and where they break.

## What you'd do differently

I would start with one tool retrieval and an update, then see whether I could build a heuristic that applies to all tool retrievals. This would give me less surface area to oversee, while hopefully allowing the learnings to carry over as I expand.
