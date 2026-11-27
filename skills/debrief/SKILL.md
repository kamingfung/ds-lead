---
name: debrief
description: Use when writing anything a stakeholder reads to decide or act (a recommendation, a decision ask, a status or progress update, a readout, an email, a chat reply, a page summary, slide titles), when building presentation slides, or when answering a hard question.
---

# Debrief

A busy reader needs to make a fast, well-informed decision. Lead with the answer, back it with evidence, then state the request. By line three, the reader should know the facts, your suggestion and the action they must take.

## Steps

1. **Identify the reader and their decision.** Note who reads the text and what they decide. When they decide nothing, state how their work changes.
2. **Phrase the question in one sentence.** Name the people or items, the measure and the time window. Good: _Which regions cut weekly order volume by more than 5% from January to March?_ Poor: _How are sales doing?_
3. **Lead with the answer.** Write one sentence that contains the headline number. For a recommendation, open with "I recommend" and name the option.
4. **List two to four proofs.** Order them from strongest to weakest. Attach a number and a source to each one, and link the source the first time it appears.
5. **Close with the request.** Give one decision or action per line, each with an owner and a due date, formatted as described under Decision asks.
6. **Trim roughly a quarter.** Reread the draft and remove about 25% of the words. Then work through Before you send.

## Shape

```text
Answer: [one sentence with the headline number]
Why: [two to four points, each with its number and source]
Ask: [per decision: gist, recommendation, alternatives; owner, date]
Not checked and risks: [what remains unverified and what could go wrong]
```

The identical layout suits an email, a chat reply, a page summary and a spoken answer. A page or slide title should state the conclusion as a complete sentence, not a label or a question, for example _Regional sales held steady after the spring price change._

## Recommend, then support

- Offer one recommendation. Give each rejected option one line explaining why it lost.
- State the fallback that takes effect if no one responds by the deadline.
- Spell out what waits on the decision, such as a release, a budget or a test.
- Separate the decision (owner, options, deadline) from background material.
- Deliver bad news first and in full: scope, impact and open verification items. State the number as it is; do not round it toward comfort.

## Decision asks

- Pose one decision per question.
- Structure each ask in three parts: the gist (what is being decided and why now), the recommendation with its reason, and every alternative with a one-line reason it loses.
- Where a tool offers answer buttons, the question holds the gist, the first button holds the recommendation and the rest hold the alternatives.
- Label options by their substance, not by letters such as (a) or (b). Examples: _Ship the price cut on June 1_ and _Keep current prices until the Q3 review_.
- Place the ask at the end. It must make sense to someone who reads only it, and repeat it wherever the reader acts: the question box, the pull request or the ticket.

## Numbers and evidence

- Pair every number with a baseline, a metric and a period. Example: the return rate dropped from 4.8% in March 2025 to 3.9% in March 2026, where returns are counted as a share of shipped orders.
- Attach a unit to every quantity, and keep one unit system throughout a document.
- Calculate figures from the raw data at drafting time, not from recall.
- Hyperlink the source on first mention.
- Separate what you verified personally from what colleagues reported.
- Call a cause a hypothesis until code, a measurement or the data owner confirms it.

## Plain words

- Keep sentences short and active: about 20 words per step and 25 per description.
- Start each step with an imperative verb, one action per step.
- Spell out each term and acronym on first use, and keep using the team's wording.
- Use one label per concept. Do not swap in synonyms.
- Reference tickets by key plus two or three keywords, for example `PROJ-123 (invoice export fix)`.
- Strip filler and hedges such as "in order to", "it is worth noting that", "basically", "somewhat" and "I think".
- Choose a table, a formula or a diagram when it reads faster.

## Audience

- Colleagues and engineers: open with the change and the test result. Technical terms, code names and file paths are fine. Drop background they already hold, and link the detailed logs instead.
- Leaders and external partners: use everyday words. Put the decision, the headline number and the business effect in the opening three lines. Explain the method only when they ask, and link to it.
- Passing a message on for someone: keep the same order, recommendation first and the ask last. Quote the approver's exact words for any sign-off, with the speaker and the date.

## Status update

```text
Headline: [on track, at risk or blocked, plus the cause in one clause]
Completed and upcoming: [finished items; next items, each with owner and date]
Request: [one decision or action, formatted as under Decision asks]
Unverified: [what you did not confirm]
```

For several workstreams, follow [references/progress-update.md](references/progress-update.md).

## Before you send

- [ ] The opening sentence answers the question.
- [ ] Every ask names an owner, a date and its options.
- [ ] Every number shows its baseline, metric, period and unit.
- [ ] Each term is defined once, and each concept carries one name.
- [ ] Filler, hedges and unexplained jargon are gone.
- [ ] Unchecked items are listed.

## Slides and storylines

- Write every slide title as a full sentence before you write any slide body. Confirm the titles alone summarize the story.
- Sequence the deck as cover, summary, section dividers, then numbered evidence slides. Each topic moves from framing to evidence, one insight per slide, then implications. Place the options-by-criteria scorecard near the front.
- For titles, use these shapes. Trend: [metric] [rose or fell] by [amount] in [period]. Comparison: [option A] beats [option B] on [criterion] by [amount]. Impact: [change] moves [metric] by [amount] before [date].
- The subtitle names the data lens and the unit. Keep each title short enough to fit two lines in the slide frame. Prose slides use a bold lead-in followed by one or two lines.
- Cap the main deck near 12 slides, with four bullets per card at most and about six words per bullet.

## References

- [references/progress-update.md](references/progress-update.md) covers status updates across several workstreams.
- [references/summaries-and-qa.md](references/summaries-and-qa.md) holds summary patterns, ways to turn tables into charts, and answers to hard questions.
- Slide layout lives in [../make-deck/SKILL.md](../make-deck/SKILL.md), and problem framing lives in [../solve/SKILL.md](../solve/SKILL.md).
