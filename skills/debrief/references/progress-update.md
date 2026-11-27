# Progress Across Workstreams

Use this reference from skill `debrief` when you report several workstreams at once, for a huddle, a "where are we" question or an end-of-day recap. An update exists to move work forward, so it starts with what the reader must decide, then what changed, then what runs without them.

## Check Before You Write

- Re-check each status live: pull request and CI state, ticket status, whether a draft is published, and branch heads. If you cannot re-check an item, mark it "not re-checked" in its row.
- Look at what the reader did since the last update, so you do not ask for something they already finished.

## Order

1. **Headline**: One sentence on overall progress against the goal, plus the single most important point now.
2. **Decisions**: Number each decision. Give its gist, your recommendation, the alternatives named by content, what it blocks, and the default if nobody answers. Leave this part out when there are no decisions.
3. **Workstreams**: One table with the same rows each time, so change stays visible. Add or close rows on purpose, never by accident.

   | Workstream              | Status              | Consequence                                      | Next step, owner, date                                     |
   | ----------------------- | ------------------- | ------------------------------------------------ | ---------------------------------------------------------- |
   | Regional sales forecast | On track            | Planning call can use regional numbers on Friday | Check holiday totals, regional analyst, Thursday 12:00     |
   | Customer churn model    | Blocked (data team) | Retention list stays at last quarter's version   | Restore the missing weekly feed, data team lead, Wednesday |

   Status is one of Done, On track, At risk, or Blocked (on whom). The consequence column says what the status means for the goal, not what work was done.

4. **Changed since last time**: Only items that move a decision, a date or a risk. Leave out routine progress.
5. **Waiting on others**: Each open wait, with who it is, what they owe, and since when.

## Rules

- **Headings and rows state the implication.** Write "Forecast misses the holiday peak by 5%", not "Forecast status". A topic label hides the point.
- **Every next step has an owner and a date or a concrete trigger.** Never write "soon", "next week" or "when ready".
- **Decide or inform.** A decision lives only in the Decisions part. Do not hide an ask inside a status row or a changed item.
- **Report outcomes, not activity.** Write "Orders now match the ledger to the cent", not "Spent three days on reconciliation".
- **Each number comes with its baseline.** "Conversion 3.1%, up from 2.8% last quarter" is complete. A bare percentage is not.
- **Say which facts you checked and which were reported to you.** Mark the reported facts, so the reader knows where to press for proof.
- **Keep it to one screen and link the detail.** Put the full analysis, query or ticket behind a link, not in the update itself.
