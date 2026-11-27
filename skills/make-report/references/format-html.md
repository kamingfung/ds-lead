# One-pager layout

Use this layout for an HTML (HyperText Markup Language) one-pager. It follows a report titled "Forecasts will use each field's values as they were known that week; the field-info tables other teams read stay the same".

## Layout, in order

1. `<title>`: a short name of two to five words.
2. A kicker line: the topic and the scope, joined by " · ".
3. `<h1>`: the answer as a statement.
4. The summary, as three cards side by side, each with an `<h3>`: What changes, What stays the same, Why it matters. Together the cards meet `standard.md`, "Front matter": 150 to 200 words, the question, the answer and what changes.
5. The ownership line, then the outcome block, right under the cards. See `standard.md`, "Outcome block".
6. `<h2>` sections. Each heading states a finding, not a label. Write "Early weeks take the budget: a small effect", not "Results".
7. One figure: an inline SVG (scalable vector graphics) or an embedded PNG (portable network graphics). Its caption starts "Figure 1." and explains every color and line style.
8. One table: units in the headers, and a row count.
9. A "Good to know" section for limits and caveats.
10. Asks last. Include asks to other people. The owner shares the page and tells them.

## Rules

- Write one self-contained `.html` file.
- Load no external fonts or scripts. Load one pinned CDN (content delivery network) library only when a chart needs it.
- Set colors in CSS (cascading style sheets) variables.
- Keep the page readable at phone width, and printable.
- Name the file by the report's short title. Add no date and no version suffix.
- Save the file in the task folder the team uses for drafts.
- Use one script to compute the numbers. It feeds the HTML and any later deck or wiki page, so the versions cannot drift.

## Skeleton

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Short name</title>
    <style>
      :root {
        --ink: #1d1d1f;
        --accent: #1f5fa8;
      }
      body {
        color: var(--ink);
        font-family: system-ui, sans-serif;
        max-width: 46rem;
        margin: 2rem auto;
        padding: 0 1rem;
      }
      .cards {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
      }
      .cards > div {
        flex: 1 1 12rem;
      }
      @media print {
        body {
          margin: 0;
        }
      }
    </style>
  </head>
  <body>
    <p class="kicker">Topic · scope</p>
    <h1>The answer as a statement, with its key number</h1>
    <div class="cards">
      <div>
        <h3>What changes</h3>
        <p>Two or three sentences.</p>
      </div>
      <div>
        <h3>What stays the same</h3>
        <p>Two or three sentences.</p>
      </div>
      <div>
        <h3>Why it matters</h3>
        <p>Two or three sentences.</p>
      </div>
    </div>
    <p class="owner">Author or team · date · ticket link</p>
    <!-- outcome block table -->
    <h2>A finding, stated as a sentence</h2>
    <figure>
      <!-- inline SVG -->
      <figcaption>Figure 1. What is plotted, unit, window.</figcaption>
    </figure>
    <table></table>
    <h2>Good to know</h2>
    <p>Limits and caveats.</p>
    <!-- asks -->
  </body>
</html>
```
