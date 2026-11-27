# Experiment report

Use this section order. Keep the section names, so readers find each part in the same place.

1. **Summary.** The problem, the hypothesis, the key result with its number, and the recommendation: launch, iterate or abandon.
2. **Outcome block.** See [standard.md](standard.md), "Outcome block".
3. **Key results.** One decision figure. Then a table of baseline against arm, with the metric, the change and the window. Then the business impact in plain words.
4. **Method.** Name the arms, the baseline, the metric with its formula, the window, and the data source with its pull date.
5. **Decision and next steps.** The decision, the owner and the date.
6. **Appendix.** The branch and commit, the run ids, the notebook or script, and the rerun command.

## Rules

- List the baseline first, then the arm, in every table and chart.
- Name each arm with a two to five word descriptive name. Give its code label once, in parentheses, where Method first names it.
- Write the decision rule before you show the result.
- State the strongest rival explanation. Name the check that separates it from your hypothesis.
- Call a result "no change" when it sits inside the noise you measured. Give the size of that noise.
- Write each metric formula in words first. Then give the symbols, each with its unit.
- Build the decision figure under the rules in `standard.md`, "Figures and tables".
- Put the reproducibility items from `standard.md`, "Body", in the Appendix, not in the summary.
- Choose one recommendation: launch, iterate or abandon. Give its reason in one sentence.
