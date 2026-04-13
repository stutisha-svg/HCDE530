# HCDE530 — week demo project context

This file is for **you, your instructor, and your TA** (and for Cursor) so everyone shares the same mental model: what the demo is for, how the files connect, and how the **`Dashboard.html`** view maps onto the Python script and CSV.

---

## What this repository is for

**Course intent:** HCDE530 explores **computational ideas** that support **human-centered design** practice, using approaches that are recognizable in industry.

**This repo’s job (this week):** A **class demo** where you:

- Read and discuss **code structure** in the main script (`demo_word_count.py`).
- Practice giving Cursor strong context via **`.cursorrules`** plus this **`context.md`**.
- Reinforce **readable code**: inline comments, clear control flow (**conditionals**, **loops**, **lists**), and small, named pieces of logic.
- Show results as a **polished, static `Dashboard.html`** (open in the browser **without** running a server—double-click or “Open with…”).

The CSV holds **synthetic demo quotes** (not real participant data). Treat it as teaching material.

---

## Intro: what this dashboard is doing (`demo_word_count.py` → `Dashboard.html`)

**Purpose of the analysis (plain language):**  
This week’s demo is a **small text-metrics exercise**, not a full qualitative study. For each row in the dataset, `demo_word_count.py` counts **how many words** appear in the free-text `response` field (split on whitespace). That number is a simple **length proxy**—useful for practicing **loops, lists, conditionals**, and for seeing the same results in the **terminal** and in a **browser dashboard**. The dashboard also shows **cohort-level summaries**: how many responses you have, and the **shortest, longest, and average** word count across the set.

**What `Dashboard.html` is showing:**  
The page is a **read-only report**: a short header explaining the demo, a row of **summary cards** (the same statistics printed under “Summary” in the console), and a **table** of every synthetic participant (ID, role, word count, and an expandable snippet of the response text). Regenerating the HTML overwrites the file so the page always matches the CSV + script you just ran.

**Source of the data (important for HCD ethics framing):**  
All text comes from **`demo_responses.csv`**. The lines are **fabricated for class**: they are written to *sound* like anonymous practitioners reflecting on research and design work, but they are **not real interview transcripts**. Treat them as **paraphrased, anonymous-style demo responses**—no real individuals, companies, or study sessions are represented. IDs like `P01` are **placeholders**, not participants you could re-identify. Use this dataset only to learn **workflow and code structure**; if you later analyze **real** qualitative data, you would follow your institution’s ethics process, consent, and retention rules.

**Why this matters for the assignment:**  
The story for your instructor is: **synthetic CSV → readable Python → static HTML**, with a clear note that the **content is instructional**, not evidence about any real population.

---

## Audience and how they should experience your work

| Audience | What they need |
|----------|----------------|
| **Instructor / TA** | Run your script, then open a **generated `.html` dashboard** in a browser and quickly see: overview metrics, a readable table, and evidence the pipeline is **CSV → Python → HTML**. |
| **You (author)** | A place to remember *why* each dashboard region exists and *which* lines of Python implement it—especially when revising for clarity or grading feedback. |
| **Cursor** | Enough product and pedagogy context to suggest changes that match a **patient-tutor** tone (see below), not “senior engineer shorthand.” |

---

## Collaboration style you want from Cursor

**Preferred mode: patient tutor**

- Define jargon when it first appears (e.g. *DictReader*, *list*, *f-string*).
- Prefer **small, reversible steps** and point to **exact files** and **what changed**.
- When suggesting code, **keep inline comments** that explain *intent* (“why”) not only *mechanics* (“what”).
- It’s fine to move slowly: you are an **HCD practitioner** learning computational tooling, not training to be a software engineer.

---

## Files in this pipeline (data → code → output)

| File | Role |
|------|------|
| **`demo_responses.csv`** | Source data: one row per synthetic “participant,” with columns described below. |
| **`demo_word_count.py`** | Reads the CSV, builds in-memory structures, computes word counts, **prints** a terminal table + summary, and **writes** `Dashboard.html` (no local server). |
| **`Dashboard.html`** | Static dashboard (self-contained CSS in the file). Regenerate by running the script; open the file in any browser (double-click or drag into a tab). |
| **`.cursorrules`** | Short, durable rules for Cursor about Python/CSV habits and repo hygiene. |
| **`context.md`** (this file) | Human-readable map: course goals, audience, constraints, and **dashboard ↔ script ↔ CSV**. |

### How to run (instructors / TAs)

1. From this folder, run: `python demo_word_count.py`
2. Watch the terminal table and summary (useful for in-class discussion).
3. Open **`Dashboard.html`** in a browser to see the same data as a small dashboard (KPI strip + table; long quotes expand with `<details>` — no JavaScript required).

---

## `demo_responses.csv` — columns and meaning

| Column | Meaning | Typical use in the script / dashboard |
|--------|---------|----------------------------------------|
| **`participant_id`** | Stable ID for each row (e.g. `P01`) | Row labels in a table; filters or sorting keys on the dashboard. |
| **`role`** | Stated role label (e.g. UX Researcher) | Second column in the table; useful for “compare roles” views. |
| **`response`** | Free-text answer | Input to **`count_words()`**; in the HTML dashboard, a **preview** appears in the table and the full quote expands via **`<details>` / `<summary>`** (no JS). |

**Design note:** Real study data would need ethics review, consent, and de-identification. This file is **demo-only**.

---

## `demo_word_count.py` — structure (today) and how it ties to pedagogy

Rough flow in the file:

1. **Imports and goal** (`csv`, `html`, top comment) — read data, escape text for the web, print + write HTML.
2. **Load CSV into a list of rows** (`responses`, `csv.DictReader`, loop with `responses.append(row)`) — classic pattern: **read everything, then analyze**. Inline comments call out **lists** + **loops**.
3. **`count_words(response)`** — small **function**: split on whitespace, return length (single rule for terminal + dashboard).
4. **`write_dashboard_html(...)`** — builds one self-contained HTML string (KPI cards + table), uses **`html.escape`** on all user text, writes **`Dashboard.html`**.
5. **Main loop over `responses`** — builds **`table_rows`** and **`word_counts`**; **conditional** for 60-character preview; same data drives **terminal** `print` lines and the **HTML** table.
6. **Terminal summary** — same aggregates as the dashboard KPI row (`len`, `min`, `max`, average). Uses ASCII-only separator lines so **Windows `cp1252` consoles** do not error on Unicode box-drawing characters.

**Course concepts explicitly exercised:** lists, loops, conditionals, string handling, functions, formatted output, basic web safety (`html.escape`).

---

## `Dashboard.html` — sections mapped to CSV and Python

These regions match what instructors see in the browser. Line references point to **`demo_word_count.py`**; update this table if you refactor.

| Dashboard section (UI) | What the viewer learns | CSV source | Python home |
|--------------------------|------------------------|------------|-------------|
| **Page title + intro** | Synthetic demo data; open file locally, no server | — | Copy in `write_dashboard_html` template string; cites `demo_responses.csv` and `demo_word_count.py`. |
| **KPI cards** | Total responses; min / max / average word count | All rows’ `response` | Same `word_counts` as terminal summary; computed in `write_dashboard_html` from passed `word_counts`. |
| **Responses table** | ID, role, word count, expandable quote | `participant_id`, `role`, `response` | Loop building `table_rows` (~215–238); table HTML assembled in `write_dashboard_html` (~40–66) with `html.escape`. |
| **Footer** | How to regenerate the page | — | Closing copy in the HTML template inside `write_dashboard_html`. |

**Stretch (not built yet):** a simple bar or sparkline of word counts using only HTML/CSS or a CDN chart library.

**Linking story for graders (one sentence):**  
*The CSV is the source of truth; the Python script turns each `response` into a number and summaries; the HTML dashboard is the same information in a layout meant for quick reading in a browser.*

---

## How this file works with `.cursorrules`

- **`.cursorrules`**: “How we write Python/CSV in this repo” (style + small conventions).
- **`context.md`**: “What this week’s demo is *for* and how the *product surfaces* (dashboard) connect to the *implementation* (script) and *data* (CSV).”

When something changes (e.g. you rename files or add dashboard sections), update **both** this narrative and, if needed, the **auto-generated tree** in `.cursorrules` by running:

`python tools/update_cursorrules_tree.py`

---

## Open decisions (fill in as your week evolves)

- [x] Generated HTML file name: **`Dashboard.html`**
- [x] Script prints to terminal **and** writes HTML (good for live demo + grading artifact)
- [x] Dashboard polish: self-contained CSS (no CDN required); dark theme + KPI grid + table hover
- [x] Long responses: **`<details>`** expand/collapse (no JavaScript)

Optional next tweaks: CDN fonts/charts, sortable columns, export to PDF for submission.
