# The Query Console

The "Query this page" section: a small SQL console whose tables are the page itself.

## Why it reads the page

Every table is built from the HTML when the page loads. Nothing is typed in twice, so a copy edit to a card changes its table with it, and a query can never disagree with what a visitor reads above it. The same idea runs through the owner's work on lineage: an answer should be traceable to where it came from. Each result row keeps a pointer to the element it was read from, and the Trace button follows it.

Nothing is fetched and nothing leaves the browser.

## Tables

| Table | Columns | Read from |
| --- | --- | --- |
| `writing` | outlet, kind, title, date, url | Published Writing cards: the masthead, the heading, the date line, the link |
| `talks` | venue, kind, title, date, status | Speaking cards. `status` is `delivered` before today's date and `upcoming` after |
| `featured` | outlet, kind, title, date, url | Featured In captions |
| `spans` | label, result, date, kind | The 2026 trace rows. The year comes from the section heading |
| `roles` | company, title, start, end, months, location | Experience. `end` is NULL for the current role; `months` counts inclusively, as LinkedIn does |
| `education` | school, degree, start, end | Education |
| `case_files` | slug, title, area, years, headline | Engineering Work case files. `headline` is the first impact figure |
| `skills` | name | What I work on |

Dates are ISO text (`2026-09-16`, or `2026-10` when the page gives only a month), so they compare and sort correctly as text.

If a section's markup changes shape, its table comes back empty rather than breaking the console. `tests/test_query.py` compares every table's row count with the page, so a silent empty table fails the suite.

## What it understands

```
SELECT [DISTINCT] columns FROM table
  [WHERE condition] [GROUP BY expressions]
  [ORDER BY expressions [ASC|DESC]] [LIMIT n]
SHOW TABLES
DESCRIBE table
HELP
```

- Conditions: `= != <> < <= > >=`, `[NOT] LIKE` (with `%` and `_`), `[NOT] IN (...)`, `IS [NOT] NULL`, `AND`, `OR`, `NOT`, and parentheses.
- Aggregates: `COUNT(*)`, `COUNT([DISTINCT] x)`, `MIN`, `MAX`, `SUM`, `AVG`.
- Functions: `LOWER`, `UPPER`, `LENGTH`, `YEAR`.
- `ORDER BY` accepts an output column's name or alias, its position (`ORDER BY 2`), or any expression.

Semantics follow SQL where a reader would rely on them. NULL compares as unknown, so it never matches `=` or `LIKE`. Text compares without regard to case. NULLs sort last in both directions. In a grouped query, a bare column must be in `GROUP BY` or inside an aggregate. When `= NULL` is the reason a result is empty, the console says so and points to `IS NULL`.

## Errors

Every error says what went wrong and how to fix it. A misspelled table or column gets a "Did you mean" suggestion, using an edit distance that counts a swapped pair of letters as one edit, so `titel` suggests `title`.

## Around the editor

- **Keys.** Enter runs the query, Shift + Enter adds a line, and the up and down arrows walk the history, restoring an unsent draft. Tab completes keywords, table names, and the FROM table's columns. When there is nothing to complete, Tab moves focus as usual, so keyboard users are never trapped in the editor.
- **Examples.** Canned queries with plain titles ("Longest roles"), after Datasette's canned queries. Hovering one shows its SQL.
- **The URL.** Every successful run writes the query into the address bar as `#q=<url-encoded SQL>`, so the address is always a link to what is on screen. It uses `replaceState`, not `pushState`, so running ten queries does not trap the Back button. A `#q=` link runs its query on arrival, and when the hash changes while the page is open.
- **The palette.** SQL typed into the Cmd or Ctrl + K palette becomes its first command, "Run SQL: ...", which runs it here.
- **Trace.** Scrolls to the source element and outlines it. A grouped row outlines every member of its group. A featured quote first brings its carousel slide forward. "Back to your query" returns focus to the exact Trace button.

## Safety

Everything renders through `textContent` and `createElement`. Nothing a visitor types is ever parsed as HTML. `tests/test_query.py` checks this with an image-tag payload, looking for both the element and its side effect.

## Adding a table

Add a `defineTable(name, about, columns, build)` call in the "Tables" part of the console in `app.js`. `build` returns one object per row, keyed by column name, with `_src: [element]` for Trace. Read values from the page with the `txt`, `parts`, and `isoDate` helpers next to it. Then add the table to the row-count test in `tests/test_query.py` and to the table above.
