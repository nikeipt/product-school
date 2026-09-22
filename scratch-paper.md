# Scratch Paper

Use this file for temporary notes, questions, prompt ideas, and working thoughts while completing the Product School labs.

## Current focus

- 

## Notes

### Ways to ping or start an agent

There are four common ways to get an agent loop moving:

- **Heartbeat:** The agent checks in every so often, looks at the current state, and acts only if something needs attention. For example: every 15 minutes, check whether a task is stuck.
- **Cron:** The agent runs at a fixed time or on a fixed schedule. For example: generate the weekly project update every Friday at 3 pm.
- **Hook:** An event triggers the agent. Something happens and the agent reacts. For example: a Jira ticket changes status, GitHub merges a PR, or a user clicks a button. A webhook is one way for another system to send that event to the agent.
- **Goal:** Give the agent an outcome to achieve and let it keep working until the outcome is validated or it becomes stuck and needs a human.

Heartbeat, cron, and hook mainly decide **when the agent starts or checks in**. A goal decides **when the agent is finished**. A goal is the option that creates a real iterative loop, so it also needs the clearest limits, validation, and human handoff rules.

## Questions

### Draft from gut feel

1. What should make Cortex start? On an event, a clock, continuously? Write what feels right.

   **Answer:** I think it should run at a scheduled time. It allows the leg work to be done ahead of time 

2. What does "done" mean for one run? One sentence.

   **Answer:**  There are 4 main areas 
   - Pull various updates
   - Drafts a leadership update
   - Proposes suitable backlog stories
   - Checks the work with an indepedent critic 


4. When should it stop or hand off to a human? List every "stop if..." you can think of.

   **Answer:**

   - Stop at the update
   - Stop at the leadership update for review
   - Stop at proposal of suitable backlog stories
   - Final stop at the end 

6. What does Cortex need? List the tools, data, helpers. Then re-run on `task-happy` and `missing-data` and adjust.

   **Answer:** It needs access to

   - Jira
   - Confluence
   - Metrics dashboard
   - Miro - roadmap details?
   - Previous updates 
