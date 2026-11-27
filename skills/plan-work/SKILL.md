---
name: plan-work
description: Use before any new ticket, including an epic, multi-step change or investigation, to draft a one-page plan, get the goal approved, walk decisions one at a time, and hand the work to your tracker. Not for writing ticket text itself.
---

# Plan Work

Use a short plan to make the goal, decision owner, trade-offs and delivery steps explicit before work enters a ticket queue. The plan is ready when the approver accepts the goal, chooses an approach, and knows the checks that will show whether it worked.

## Steps

1. **Name the goal and the people.** Write the goal in one sentence. Name the approver: the one person who signs off the goal and the result (the Accountable role in the RACI matrix, a table of Responsible, Accountable, Consulted and Informed roles). Name the people to consult before the decision and the people to inform after it, or write `none`. Stop if the goal or the approver is missing.
2. **Check the cause first.** If the problem or its cause is unknown, frame and test it with `solve` before planning a solution. If the work builds something new or changes behavior, agree the design first: [references/design-before-building.md](references/design-before-building.md).
3. **Draft the one-page plan.** Use [references/plan.md](references/plan.md). Build it with `make-report` when the approver will read it outside the chat.
4. **Compare alternatives.** For every option, state its cost, risk and what happens if nothing changes. Recommend one and explain why.
5. **Walk decisions one at a time.** For each decision, give the gist, your recommendation and the named alternatives in `debrief`'s “Decision asks” format.
6. **Record the answers.** Add the approver's answer and the date to the plan. Keep open decisions marked with their owner.
7. **Hand off to your tracker.** After approval, turn the plan's steps and checks into the work items your team uses. Put the goal first, then one item per step.

## Rules

- Check every number before writing it. Label unchecked numbers as hypotheses.
- Give every step one owner, a date and its anchor. The step owner is the Responsible role.
- State what is out of scope.
- Keep the plan to one page. Link to supporting detail instead of copying it.

## Verify

- Every alternative has a cost and a risk.
- Every open decision has an answer, or the plan names who decides it.
- Every step maps to a work item after approval.
- The done checks are pass-or-fail and can be verified by another reader.
