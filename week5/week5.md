# Week 5 reflection — Pokémon (Dark / Ghost) exploratory notebook

This reflection is tied to the Jupyter notebook in this folder that loads `**pokemon_dark_ghost_gen1_4.csv**` and walks through inspection, distributions, a dual-type subset, a grouped comparison, and missing-value checks. The competencies below frame what the notebook is doing and what I would change next.

---

## C5 — Data analysis with pandas

**What the notebook practices.** The workflow uses pandas to *answer questions in order*: load and bound the sample (`read_csv`, `shape`), inspect structure (`head`, `info`), summarize two numeric columns (`describe`), isolate a meaningful subset (boolean filter on `types` with `str.contains`), summarize a column on that subset (`describe` on `base_experience`), compare groups (`assign` + `groupby` + `agg` on `special_attack`), and audit completeness (`isnull().sum()`).

**What felt most useful.** Section 2’s summaries of `**attack`** and `**special_attack**` made the *spread* of the two offensive stats concrete: averages sit in one place, but the distribution is not “one number fits all.” I read it as a mix of low and high values, with **special_attack** not collapsing to a single low cluster—there is a fairly even spread from low to high compared to how **attack** piles up. That kind of comparison is exactly why `describe()` plus a visual (Section 2) belong together: the table states the moments, the plot shows where bodies sit.

**Section 3 (filtering).** The Dark **and** Ghost filter was valuable because it *quantifies rarity*: only a handful of rows qualify, so any story about “dual Dark/Ghost in this slice” is necessarily about a tiny set of forms, not the whole roster. In hindsight I would pair that with a **complementary summary of the largest or most common typing pattern** in the file (for example `value_counts` on `types` or a simple bar of the top combinations) so a reader sees both “the needle” and “the haystack.”

**Section 4 (grouping and summarizing).** I would still point a skimming reader to Section 4 first: mean `**special_attack*`* is higher when typings include **Poison** (~~83.5) than when they do not (~~78)—a modest gap on this scale. The important pandas lesson is *count-aware reading*: only **six** rows carry Poison typings versus **forty-nine** without, so a couple of megas (e.g. Gengar-line forms) can move the group mean. The right operation for that question is exactly what we did—**groupby + mean + count**—but the *interpretation* has to stay “suggestive in this CSV,” not a universal rule about “Poison overlaps are stronger.” Strength here really means “higher mean **special_attack** in this filtered Gen 1–4 slice,” not overall battle performance.

**Missing data.** Checking nulls per column was reassuring for this file: it confirms the aggregates and filters are not silently dropping rows to `NaN`. If the dataset grew messier, the same `isnull().sum()` pattern would tell me where to impute or filter before trusting group means.

**What I would keep vs. redesign first.** I would **keep Section 4 as-is**—the question, the aggregation, and the caveat are aligned. I would **revisit Section 2 first**: either enrich the histogram with **domain context** (another small table comparing overlapping generations or typing families from the same source) or extend the analysis with **height/weight** alongside **attack / special_attack** (e.g. correlation or scatter) so the reader ties stats to *specific Pokémon and physiology*, not only to typings that can skew perception.

---

## C6 — Data visualization and publishing as a notebook

**What the histogram argues.** The overlaid histograms in Section 2 are a **frequency view**: for chosen bins, how many Pokémon fall into each range of **attack** and **special_attack**. That supports a quick visual claim—where species **cluster**, how **wide** the spread is, and which stat’s distribution sits **farther right** on average—without naming every row.

**Limits of that choice.** The chart trades away **identity**: it does not show names or typings inside the bars, so the dataset can feel **abstract** even when the numbers are faithful. A reader who cares about “which Pokémon drive each bump” may want a **second figure**—for example a labeled scatter (`attack` vs `special_attack`, color by `types` or annotate extremes) or a compact correlation view that re-anchors the story in **monsters**, not only bins.

**Notebook as something to publish (e.g. on GitHub).** If someone only skims the repo, I would send them to **Section 4** first for a **comparative takeaway** with an explicit **sample-size warning**, then let Sections 1–3 supply **orientation** (schema, global distributions, rare dual-type slice). Clear section headers, `display` / `print` / `plt.show()` for visible outputs, and plain-English `#` comments in the notebook all support that skim path—those are part of making analysis **legible** outside the author’s machine.

**Next iteration.** I would either (a) add a **comparison table** next to Section 2 that situates Dark/Ghost-adjacent rows against other typings or generations from the same file, or (b) build the **correlation / scatter** idea with **height** and **weight** so readers see *which* Pokémon sit in the corners of the stat space and how body size relates to offense—moving some of the “why” from typology alone to measurable traits.

---

## Closing

The notebook already practices **choosing pandas operations to match questions** (filter for rarity, groupby for contrast, null audit for trust). The main growth edge for me is **pairing every global chart with at least one identity- or subset-aware view** so published analysis on GitHub stays both **statistically careful** and **Pokémon-specific** for a reader who will not run every cell.