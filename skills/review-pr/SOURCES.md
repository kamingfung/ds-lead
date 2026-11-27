# Sources: review-pr

The wording of `review-pr` is new. This table says which idea, number or quote comes from which source. A quote is at most 15 words. The skill files carry no citations, so they stay short for the agent.

## Where each source is used

| Idea, number or quote                                                                                                    | Where in the skill                              | Source                                                             | How used               |
| ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- | ------------------------------------------------------------------ | ---------------------- |
| Approve a change once it clearly makes the code base better, even if it is not flawless                                  | references/standard.md, Review Standard         | Google, "The Standard of Code Review"                              | idea, paraphrased      |
| Review like a journal referee: value and soundness before style; weigh the limits the author admits                      | references/standard.md, Review Like a Referee   | "The good referee", _Nature Methods_ 15, 91 (2018)                 | idea, paraphrased      |
| Read the full file for context, not only the diff                                                                        | references/standard.md                          | Google, "What to look for in a code review"                        | idea, paraphrased      |
| Start a polish-level finding with "Nit:"                                                                                 | references/standard.md, Review Like a Referee   | Google, "How to write code review comments"                        | quote, 1 word          |
| Address the work, not the author; raise grammar only when it hides meaning                                               | references/standard.md                          | Google, "How to write code review comments"                        | idea, paraphrased      |
| Explain why each finding matters and give a concrete fix                                                                 | references/format.md                            | Google, "How to write code review comments"                        | idea, paraphrased      |
| Group the checklist by review category: design, functionality, complexity, tests, naming, comments, style, documentation | references/checklist.md                         | Google, "What to look for in a code review"                        | structure, paraphrased |
| Reviewer process and etiquette                                                                                           | references/checklist.md; references/standard.md | Microsoft, "Reviewer Guidance"                                     | idea, paraphrased      |
| Check each comment before you act, and reply to every comment                                                            | references/answering-a-review.md                | "How to write a rebuttal letter", _Nature Methods_ 23, 1919 (2026) | idea, paraphrased      |

## References

- "The good referee", _Nature Methods_ 15, 91 (2018). https://doi.org/10.1038/nmeth.4603
- "How to write a rebuttal letter", _Nature Methods_ 23, 1919 (2026).
- Google. "The Standard of Code Review", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/reviewer/standard.html (CC BY 3.0)
- Google. "How to write code review comments", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/reviewer/comments.html (CC BY 3.0)
- Google. "What to look for in a code review", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/reviewer/looking-for.html (CC BY 3.0)
- Microsoft. "Reviewer Guidance", Code-With Engineering Playbook. https://microsoft.github.io/code-with-engineering-playbook/code-reviews/process-guidance/reviewer-guidance/ (CC BY 4.0)
