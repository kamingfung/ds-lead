# Bug or incident report

Give the full picture before any ask. Use this section order.

1. **What happens.** The observed behavior, with numbers, and where it shows.
2. **Impact.** Who or what reads the broken output, and the size of the effect.
3. **Steps to reproduce.** The version or commit, the data, the command, and the expected result next to the actual result.
4. **Where to look.** The files, functions, dashboards or queries that hold the fault.
5. **Suspected mechanism.** Label it "hypothesis" until code or data confirms it.
6. **Fixes.** Each fix with its owner, in the order to apply them.
7. **Done when.** The mechanism is confirmed. A test reproduces the bug and passes. Damaged data is repaired, with before and after counts.
8. **Evidence.** The query ids, run ids and attached data slices.
9. **Asks.** Last. Include asks to other people.

## Rules

- Name the owner of the broken code before you plan the fix.
- Attach the smallest data slice that proves the point. Never attach credentials.
- Hold every action ask until the write-up is complete.
- Write expected and actual results with their numbers. Do not write "it looks wrong".
- State the window the bug covers, with the first and last affected dates.
