# Week 3 — Interview reflection (C2 & C3)

Short interview about this week’s work in **`week3/`** (especially `week3_analysis_buggy.py`, CSVs, and how you read errors and outputs).

**C2 — Code literacy and documentation:** reading and changing code, plus commit messages and docstrings that make work legible.

**C3 — Data cleaning and file handling:** loading messy tables, interpreting errors, and writing scripts you can run again on similar data.

---

## Interview — questions and your answers

### 1. Where did the code “click” for you?

**Question:** When you look at what you built this week, what is one moment where you felt you actually *understood* the code or the data—not just that it ran, but *why* it behaved that way? What file or function was that about?

**Your answer (summary):** Most time went to `week3_analysis_buggy.py`. Building the satisfaction list with `.strip()` and `.append()` felt clear. Structuring **`rank_tools_by_reviews`** also made sense: using lists, then tuples mixing **string, float, and int**, with **`scores_by_key`** and **`label_for_key`** so scores aggregate under one key while the printed label stays human-readable (e.g. merging `figma` / `Figma`).

---

### 2. The `'fifteen'` problem and what you do with a “bad” row

**Question:** What was going wrong with `experience_years`, and why not handle it by deleting that row from the CSV for every statistic?

**Your answer (summary):** The field was the **string** `"fifteen"` instead of something `int()` can parse (like `"15"`), so averaging broke. At first, dropping the whole row threw off other outcomes (e.g. satisfaction). You wanted **accurate** summaries everywhere they still make sense, so the code **checks** which rows have numeric experience and only uses those values in the **average**; other columns for that respondent can still count elsewhere. *(Precision for your write-up: the helper validates with `int()`; it does not spell English words into numbers unless you add that separately.)*

---

### 2b. The sorting bug in “Top 5 satisfaction scores”

**Question:** You said the top-five output was still off at one point. What was the bug, how did you notice it, and how did you debug and fix it?

**Your answer (summary):** The script was sorting satisfaction scores in **ascending** order and then taking the first five rows, which returned the **lowest** scores instead of the highest. I noticed this because the “Top 5” section looked inconsistent with expectations from the rest of the summary output. I switched into Plan mode first to reason through what the code *should* do, then carefully checked terminal output and the relevant lines around the `sort()` + slice logic. The fix was to sort in **descending** order (`reverse=True`) before slicing to five, and to add an inline comment explaining why this change was necessary so the bug is easy to spot later.

---

### 3. What should a stranger read first?

**Question:** If someone opened the repo next month and only read **one** thing besides the code—a commit message or a docstring—what should it say about this script?

**Your answer:** You’d use a commit message like:

> Refactor week3_analysis_buggy into functions with docstrings  
> Extract load_survey_rows, experience_is_numeric, count_responses_by_role, and rank_tools_by_reviews; move flow under main() and resolve CSV path from the script directory. Keep numeric-only averaging for experience years and add tool rankings from primary_tool + satisfaction_score.

That tells a reader **what was extracted**, **where paths resolve**, and **two behaviors** (experience averaging vs tool rankings).

---

## Critical analysis

> **Purpose:** These two are about **trusting output** and **real-world fragility**—not whether the code runs without errors.

### 4. When the terminal looks “fine” but the story is wrong

> **Question:** What is one output that could look legitimate but still mislead you if you acted on it without thinking?

**Your answer (summary):** **Average satisfaction as a single number** can hide **sample size**. Example: **Sketch** can show **5.0** while only having **one** review—so the rank is less meaningful than a tool with more reviews and a slightly lower mean.

---

### 5. Running this on a real export tomorrow

> **Question:** On a bigger, messier real survey file, what is the first thing you would change or add so you still trust the summaries—and how would you know it worked?

**Your answer (summary):** **Surface unusual rows** instead of letting them disappear: collect them (e.g. append to a **flag list**) and **print** (or log) them so they demand attention. *(Implementation note: in Python, **`pop`** removes an item; a QA pattern is **`append`** odd rows to a separate list, then print that list after the main pass.)*

---

*If you extend this for a portfolio or assignment, add one concrete pointer per answer (function name, column name, or CSV row id) so evidence is easy to check.*
