# Week 6: Process

## Original questions and where the project went

The three original misinformation-flavored questions:

1. **Propagation.** How does an AI misinformation post propagate across five layers of engagement, and does discourse quality degrade with distance from the root?
2. **News accounts.** To what extent do established news and media accounts contribute to AI-misinformation spread, and which outlet types are most implicated?
3. **Themes.** Which AI themes (job displacement, sentience, deepfakes, etc.) generate the most misinformation-adjacent discourse, and how does engagement vary across themes?

"Misinformation" turned out to be very hard to label rigorously on Bluesky in a week. There is no flag, no fact-check feed, and no consensus taxonomy I could apply confidently to ~30k posts. So the project drifted: instead of classifying truth value, I started measuring **tone, certainty, and framing** as proxies for the *kind of discourse* I was originally curious about. Propagation became "how does sentiment-by-substance degrade as a viral post fans out?", the news-account question became "do outlets sound certain or hedged about AI?", and the themes question became "which emotions dominate which themes month-over-month?".

## Process

I built four Plotly figures on a Bluesky AI-post corpus, enriching the dataset twice when a chart's question outgrew the original collection. `enrich_bsky_threads.py` pulls `getPostThread` and `getQuotes` descendants for the top viral roots so the Sankey has something to trace. `enrich_bsky_news.py` pulls `getAuthorFeed` history for ~20 hand-picked outlets (Atlantic, ProPublica, Fortune, WaPo, local stations) so the news analysis has a real sample. Each enrichment surfaced its own bugs (`NaN` text from thread stubs crashing VADER, AT-protocol URIs and outlet handles polluting the theme dropdowns), and those fixes are now baked into the helpers used across all four charts.

## 4a: Radial sentiment scatter

**What it answers.** Where does each post sit on a continuum from neutral to opinionated, and how does that shift by theme?

**Why a radial scatter.** Radius is `|VADER compound|`, so neutral posts sit in the dead center and the loudest opinions sit out at the rim. Angle is just spread for legibility. Orange / fuchsia / teal reads as negative / neutral / positive at a glance, and opacity scales with intensity so impassioned posts pop and lukewarm ones recede.

**Observation.** The cloud is overwhelmingly teal-heavy with a sparser orange outer ring of strongly negative posts. Neutral posts are rare once you filter to >50-word records, suggesting Bluesky AI discourse skews toward people who already have a take. `ai_creative` is the most teal-saturated theme; `agi_risk` is where most of the orange lives.

**Caveats.**
- VADER misreads sarcasm and technical hedging.
- The >50-word filter biases toward people who already care enough to write a paragraph.
- Angle is purely cosmetic, so don't read clusters into it.

## 4b: Sankey propagation of one viral post

**What it answers.** How does the *quality* of discourse change as a single viral post fans out into reposts, replies, and quotes?

**Why a Sankey.** It shows conservation (every reposter, replier, or quoter is one unit of attention) and shows how that attention splits into composite quality buckets at the next tier. Tier-0 is one auto-selected viral root. Tier-1 splits into Reposts / Replies / Quotes. Tier-2 splits replies and quotes again into a 2x3 grid of *substance* (short vs. substantive) x *sentiment* (orange / fuchsia / teal).

**Observation.** Reposts dominate raw volume; most engagement is a one-click amplification with no text at all. Among posts that do carry text, "short + teal" and "substantive + fuchsia" are the largest follow-on buckets, which fits the pattern of a viral post collecting brief positive reactions plus a long tail of measured, substantive replies. Strongly negative quotes are rare.

**Caveats.**
- This is *one* post, so it is an illustrative trace, not a population claim.
- Word count is a crude stand-in for "quality".
- Even after enrichment the Bluesky API does not return every descendant, so the absolute counts are lower bounds.

## 4c: NRC emotion heatmap by theme and month

**What it answers.** Which emotions dominate which AI themes, and how does that change over time?

**Why a heatmap.** Rows are months, columns are NRC emotions (fear, anger, trust, anticipation, joy, sadness, surprise, disgust), and color encodes the share of posts in that theme-month whose dominant emotion was that category. A categorical y-axis was also the only way to dodge a Plotly date-tick rendering bug that turned the axis into "Jan 200 / Jan 2001".

**Observation.** `agi_risk` lights up under fear and sadness fairly consistently. `ai_creative` and `ai_jobs` lean on anticipation and trust. `deepfakes` shows a fear-and-disgust signature distinct from any other theme. Across 2024 and 2025 there is a perceptible drift where anticipation tiles brighten and trust tiles dim across most themes.

**Caveats.**
- NRC is a lexicon (word lookup), not a model: no understanding of negation or sarcasm, and any single charged word is over-weighted.
- Month-buckets with fewer than 5 posts are dropped, so very sparse themes still have gaps.
- "Dominant emotion" hides ties; a row with two near-equal emotions arbitrarily favors one.

## 4d: News outlets' certainty and framing fingerprints

**What it answers.** How confident do news outlets sound when they write about AI, and how stylistically distinct are they from one another?

**Why a scatter with small multiples.** The top panel plots outlets on hedge rate (x: "may", "could", "reportedly") vs. attribution rate (y: "according to", "said", "sources told"). Quadrant medians split the plane into four framing styles. Marker size encodes post volume, shape encodes outlet group (national / tech / investigative / local), and color encodes TF-IDF cosine similarity to the selected quadrant's framing fingerprint. The bottom panels show that quadrant's top bigrams and top action verbs, so the dropdown changes what the framing fingerprint actually *is*.

**Observation.** Investigative outlets (ProPublica especially) cluster firmly in "hedged & well-attributed" with many hedges and many sources. Tech outlets land in "declarative & unattributed" with confident verbs like "unveils", "launches", "powers". Locals are scattered and small-sample. Coloring by similarity surfaces the long tail of near-misses: several locals are stylistically close to the investigative quadrant even though they sit in a different quadrant by raw hedge/attribution rate.

**Caveats.**
- Regex-based hedging and attribution lexicons miss headlines that don't use canonical phrasings.
- Outlet group is hand-coded.
- Local-station sample sizes are still small even after enrichment.
- TF-IDF similarity rewards shared *vocabulary*, not shared *meaning*; two outlets writing about the same AI product can look similar without framing it the same way.

## Reflection

> The classroom anecdote that started this (an "AI bot society" half-truth that traveled further than the boring, accurate version) turned out to be a decent description of the data. Bluesky AI discourse skews positive and opinionated (4a), each theme has its own emotional fingerprint that is easy to read off the heatmap (4c), and even the news outlets we treat as ballast split sharply between hedged investigative reporting and confident, unattributed tech announcements (4d). None of this proves any individual post is misinformation, but it does show how easily a feed of confident, emotionally legible takes becomes the version of "the AI conversation" a reader walks away with.

## Competencies: C3, C6, C7

**C3 (data cleaning and file handling).** The two repeatable enrichment scripts (`enrich_bsky_threads.py`, `enrich_bsky_news.py`) plus the cleaning that fell out of them (`.fillna("")` before sentiment scoring, regex filters that drop `_enrichment`, `at://`, and outlet handles from theme menus, 429 backoff and host failover in the API loops) keep the pipeline runnable on any CSV that matches the Bluesky schema. A third helper, `tidy_bsky_csv.py`, slims the JSON-flattened CSV from 471 sparse columns to 60 in place using a principled keep rule (every column used by an analysis plus everything populated above 10%) and an atomic write, so `df.head()` stops printing 471 mostly-NaN columns and the schema is reproducible from any re-run. Most of these fixes only landed because I read the actual tracebacks instead of treating crashes as black boxes.

**C6 (data visualization).** Each chart was matched to its data structure: a radial scatter for a continuum, a Sankey for flow with conservation, a heatmap for a theme x month x emotion matrix, and a scatter with small multiples for outlet framing. Two earlier attempts got cut for not serving the question: a VADER stacked-area chart that duplicated 4a on a weaker encoding (and had a "Jan 2000 / Jan 2001" date axis bug), and a top-authors bubble chart for 4d that ranked individuals when the actual question was about outlets. Publishing as both a Jupyter notebook and standalone PNGs (`fig.write_image`, kaleido 1.x) lets the same evidence work inline on GitHub and as figures in a write-up.

**C7 (critical evaluation and professional judgment).** The biggest call was not shipping a misinformation chart at all: a hand-coded label would not have survived scrutiny, so I used linguistic proxies (sentiment, hedging, attribution, NRC emotion) and named the limits of each next to its chart. The smaller calls were about tool-question fit (VADER for 4a and 4b, NRC for 4c, regex plus TF-IDF for 4d), about *verifying* tidiness rather than assuming it (catching `NaN` text, AT-protocol URIs, and outlet handles before they silently corrupted the charts), and about responding to sparseness (both enrichment scripts, lowering 4c's per-month threshold from 30 to 5, hiding outlet-handle "themes" from dropdowns). Each was a moment where shipping the easy version was the wrong call.
