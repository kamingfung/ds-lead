# Review Format

Reached from skill `review-pr`, at steps 9 and A5. The meaning of each severity is in [standard.md](standard.md), Review Like a Referee, and the check labels are in [verification.md](verification.md). Rules marked (gate) are checked by `scripts/check_drafts.py`.

## Drafts

- Write the drafts to a folder outside the repository: a `summary.md` and one `.md` file per inline comment.
- An inline draft starts with its anchor on one line, in the API form from the next section. The next line is its severity line (gate).

## Inline Comments

- Post each finding at the line or range it concerns. Never post a general comment that names `file.py:123`.
- Keep the general (top-level) comment for the summary of the whole PR: the verdict, the counts by severity and what you could not check.
- Write the anchor as one JSON line. For one line: `{"inline": {"path": "<file>", "to": <line>}}`. For a range: `{"inline": {"path": "<file>", "start_to": <first>, "to": <last>}}`.
- Use new-side line numbers at the PR head, and anchor only inside changed hunks.
- A finding about an unchanged file goes on the changed line that causes it, with a pointer to the other file.
- A finding that appears in several places is written in full once. Each other place gets a one-line pointer.
- Give every must-fix and should-fix a concrete fix. If the fix replaces the anchored lines, use a `suggestion` block on exactly those lines. Where the host does not support suggestions, give a short code sketch.
- Say why the finding matters and offer a direction, as the guidance in [Sources](#sources) advises.
- The first line after the anchor starts with the icon and severity: `❌ must-fix`, `⚠️ should-fix` or `🤔 nice-to-have` (gate).
- Then comes "new in this PR" or "pre-existing" in parentheses, a semicolon, and the check label: "read in code", "traced", "ran" or "ran on data" (gate). Then a colon and the claim (gate).
- A must-fix needs the check label "ran" or "ran on data" (gate). Post a finding checked only by reading or tracing as a question.
- Put each icon next to its word. Do not mark a severity with a colored circle (gate).
- Link every commit sha, for example `[abc1234](https://git.example.com/org/repo/commits/abc1234)` (gate).

The example fence uses four backticks so the inner `suggestion` block fits.

````text
{"inline": {"path": "orders/sync.py", "start_to": 42, "to": 47}}
⚠️ should-fix (new in this PR; read in code): the retry loop has no upper bound, so a failing API call retries forever.

Cap the attempts and wait longer after each failure. The suggestion replaces lines 42 to 47.

```suggestion
    for attempt in range(MAX_ATTEMPTS):
        try:
            return fetch_page(url)
        except TransientError:
            time.sleep(2**attempt)
    raise RuntimeError(f"gave up on {url} after {MAX_ATTEMPTS} tries")
```
````

## Summary Comment

- Open with exactly one verdict on the first non-blank line (gate). The four verdicts are:
  - `✅ **Ready to merge**`: the worst finding is a nice-to-have, or there are none.
  - `🔧 **Ready to merge after small fixes**`: the worst finding is a should-fix.
  - `🛑 **Changes needed**`: the worst finding is a must-fix.
  - `⏸️ **Not ready: waiting on <what>**`: a blocker or a running check stops the review.
- The verdict must match the worst severity among the inline comments (gate). A must-fix allows only changes or waiting. A should-fix allows only small fixes or waiting. A nice-to-have, or no finding, allows only ready or waiting.
- Verdict icons and severity icons never share a symbol. Use no colored circle (gate).
- Put the linked head sha next to the verdict, for example `([abc1234](https://git.example.com/org/repo/commits/abc1234))` (gate).
- End the verdict line with `Tier N: <reason>`, where N is the tier from [SKILL.md](../SKILL.md), step 2 (gate). The waiting verdict has no tier.
- Lay out the summary as one paragraph per part, in this order: the verdict line; `**Evidence:**`, a blank line, then bullets for the data source, query or run ids and CI state; `**Good:**`; `**Key fix:**`; `**Not run:**` (gate). Write `**Good:**` and `**Key fix:**` as one or two plain lines each.
- A waiting summary needs only `**Evidence:**` and `**Not run:**` (gate).
- Keep the detail inline. Post at most 15 inline comments (gate), and summarize the rest in the summary with a note.

```text
🔧 **Ready to merge after small fixes** ([abc1234](https://git.example.com/org/repo/commits/abc1234)) Tier 2: the change touches a shared data sync.

**Evidence:**

- Data: order sync log, 2026-01 to 2026-03, run `run-0412`.
- CI: green.

**Good:** The new tests cover both regions.

**Key fix:** Cap the retry loop in `orders/sync.py`.

**Not run:** A live outage of the API; the test stubs the failure.
```

## Replies

- Post the round summary as a reply under the reviewer's own summary comment, or as a top-level comment when there is none.
- Shape the summary: head sha first, one bullet per finding with its fix commit, then whether outputs change (with evidence), the test count and the CI state. See [answering-a-review.md](answering-a-review.md), section 4.
- Keep replies short. Skip thanks for each comment, say how you read an unclear comment, and point to the change (commit, `file:line` or doc section) instead of pasting it.

## Sources

- Google. "How to write code review comments", Google Engineering Practices Documentation. https://google.github.io/eng-practices/review/reviewer/comments.html (CC BY 3.0)
