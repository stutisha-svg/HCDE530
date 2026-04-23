# Week 2 — Competency 2 reflections

**Competency 2 (course framing):** *Code literacy and documentation* — reading code well enough to explain what it does, change it when needed, and document it for others; writing commit messages, docstrings, and README-style material so the work stays legible.

This note captures observations from this week’s work in this repository (demo + Dickens scripts, Cursor context, and Git history).

---

## Where I spent the most “reading” time

I focused most on **`dickens_word_count.py`**. In my own words, the script:

- Defines **`count_words`** and uses it to turn each quote string into a **numeric word count** (by splitting on whitespace).
- Uses **lists** and **row dictionaries** (from `csv.DictReader`) to load all quotes before analyzing them.
- Uses **`for` loops** to walk each row, accumulate counts, and build the per-row output.
- Prints **per-row** results, then ends with a **summary** (total count, min, max, average word length).

The **hardest line to read** at first was the typed empty list:

`quotes: list[dict[str, str]] = []`

It encodes useful information (each CSV row becomes a dictionary with string keys and string values), but it reads like jargon until you connect it back to `DictReader` and the column names in the CSV.

---

## How I made the work legible for others (not only “working code”)

- **Inline comments:** I used Cursor’s commenting affordances to walk through structure **step by step** in the Python files, so a reader can follow intent without decoding everything from syntax alone.
- **Outputs as documentation:** I extended scripts so results are visible **outside the REPL**—for example writing **`dickens_word_counts.csv`** (not only terminal printing) and, in the demo track, generating **`Dashboard.html`** so instructors can open a browser view without running a server.
- **Repo intent files:** I created **`.cursorrules`** and **`context.md`** to spell out the **thought process**, constraints, and how files connect (data → script → outputs), especially because **GitHub + Cursor** are relatively new surfaces for me and I want graders to see *why* the repo is organized the way it is.

---

## Commit messages: what I did, and what I’d improve

Examples of messages I actually used:

- *“Extended the script to write the results to a new CSV file instead of just printing them.”*
- *“Updating the per-row print format and aligning the summary labels with wording”*

These commits communicate **what changed**, but if I were grading myself on message quality alone, I would:

- Make messages **shorter** and **more specific to the project direction** (less generic phrasing).
- Use **more frequent commits** with **tighter scope** so each commit tells a clearer story on GitHub.

That matters for Competency 2 because commit history is a form of **documentation for collaborators**—especially instructors/TAs scanning a repo quickly.

---

## If I had 15 more minutes before submitting

I would prioritize **making `context.md` more concise and crisp** for a fast reader, **and** improving **commit frequency + specificity** so GitHub reflects intent more faithfully.

Both target the same problem: **instructor/TA comprehension** through formats (GitHub + Cursor) that are still new to me.

---

## Competency 2 “so far” (honest snapshot)

**Stronger:** connecting code structure to outputs people can open (CSV / HTML), and using repo-level context files plus inline narration.

**Still building:** type-hint literacy on first read, commit craft (brevity + scoped commits), and tightening long-form context so it stays welcoming without becoming heavy.

---

## Critical Evaluation — Week 2

Moving from **synthetic classroom CSVs** to anything that represents **real people or decisions** changes what a “simple word count” can responsibly claim. These prompts are for **risk-aware practice**, not to dismiss the exercise.

### Prompt A — Real data instead of the demo file

**What would happen if you ran this script on a real dataset instead of the demo CSV?**

### Prompt B — Risk and detection

**What could go wrong? How would you know?**

### My responses

**Prompt A — real vs demo**

If this script ran on a real dataset instead of the demo CSV, the **variable names (column keys) might not match** what the code expects, and the **functions would not run** (or they would fail when reading fields). If that were fixed—**hypothetically**, with the **correct file name** and **matching variable/column names**—then the same counting logic *might* still work as a mechanical length measure.

**Prompt B — what could go wrong; how you’d know**

Same core point as **Prompt A**: the script depends on a **stable schema** (and the expected input file). You would often **know** from **errors** (for example missing files or missing columns) or from **outputs that don’t line up** with what you believe is in the dataset.

> **Practitioner checkpoint — read before acting on results**  
>  
> **Question:** What would a thoughtful practitioner question about this output *before* acting on it?  
>  
> **My response:**  
>  
> A thoughtful practitioner would **evaluate the complexity of the dataset** and make that explicit for collaborators and tools—for example by updating **`.cursorrules`** so Cursor (and humans) understand **which variables exist**, **what analyses are in scope**, and **what the output is not claiming**. I would also question whether **average** and **min/max** summaries could be **skewed** or misleading depending on outliers, mixed text types, or what “a word” is allowed to mean in real materials.
