# Design before building

Use before you build something new or change behavior. The design is done when the owner has approved a written note that a builder could work from without asking them anything.

## Steps

1. **Check what you know.** If the request names everything that matters ("make the icon blue"), do it and say what you did. Otherwise continue.
2. **Look before you ask.** Read the files, specs and earlier decisions the request touches, until you can explain how the relevant parts work today. Ask nothing the project already answers.
3. **Play the request back** in your own words: what is wanted, for whom, and why. Add what you found that changes it: a constraint, a conflict, a cheaper path.
4. **Ask one question at a time,** only when the answer changes what gets built. Ask for the why first, open, with no options attached. Otherwise state your call and your reason, and move on.
5. **Lay out two or three approaches** in a message of their own, each concrete enough to picture, with what it trades off. Recommend one. Wait for the owner's pick.
6. **Write the design note:** intent and why; goals, non-goals and what would make it a failure; constraints; the approaches and the pick; what the owner decided; what is left to the builder. A few lines each for a small change.
7. **Get the note approved.** Build nothing before that: no code, no scaffolding, no installs. Reading and exploring are fine.

## Reference

- A throwaway spike is allowed when the owner agrees to one. Keeping what it produced is a new request that goes back through step 7.
- Anything you filled in goes into the note as your call, never as something the owner agreed to.
- When the work turns out to be several independent projects, say so, agree an order, and design one at a time.
- Show a sketch when seeing helps more than reading: a layout, a flow, options that look different.
