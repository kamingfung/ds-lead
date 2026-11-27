# Sources: coding

The wording of `coding` is new. This table says which idea, number or quote comes from which source. A quote is at most 15 words. The skill files carry no citations, so they stay short for the agent.

## Where each source is used

| Idea, number or quote                                                                                   | Where in the skill              | Source                                                 | How used          |
| ------------------------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------ | ----------------- |
| Prefer the shorter version when a much shorter one works                                                | Build Only What Was Asked       | PEP 20 (Peters, 2004): "simple is better than complex" | quote, 5 words    |
| Add no feature, option or abstraction that nobody asked for; flag code more generic than the task needs | Build Only What Was Asked       | Google, "What to look for in a code review"            | idea, paraphrased |
| Match the style of the file; follow PEP 8 where the file is silent                                      | Change Only What the Task Needs | PEP 8 (van Rossum, Warsaw and Coghlan, 2001)           | named standard    |
| About 100 changed lines is reasonable; about 1000 is usually too many                                   | Change Only What the Task Needs | Google, "Small CLs"                                    | number            |
| Check that each test fails when the code it covers is broken                                            | Prove It Works                  | Google, "What to look for in a code review"            | idea, paraphrased |
| Put new tests in the same change as the logic they cover                                                | Prove It Works                  | Google, "Small CLs"                                    | idea, paraphrased |

## References

- Peters, T. PEP 20, "The Zen of Python" (2004). https://peps.python.org/pep-0020/
- van Rossum, G., Warsaw, B. and Coghlan, N. PEP 8, "Style Guide for Python Code" (2001). https://peps.python.org/pep-0008/
- Google. "Small CLs", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/developer/small-cls.html (CC BY 3.0)
- Google. "What to look for in a code review", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/reviewer/looking-for.html (CC BY 3.0)
