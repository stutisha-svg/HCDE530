# Week 6: AI discourse on Bluesky

This project analyzes AI-related Bluesky posts (search-collected, thread-enriched, and news-outlet-enriched) with four Plotly visualizations in a Jupyter notebook: sentiment by theme, propagation of one viral post, NRC emotions over time by theme, and hedging/attribution framing for news accounts.

## Data source

Posts are collected from the Bluesky **AT Protocol** HTTP API via `app.bsky.feed.searchPosts`, with optional follow-up calls (`getPostThread`, `getQuotes`, `getAuthorFeed`) in the enrichment scripts. Official API documentation: [https://docs.bsky.app](https://docs.bsky.app). The collector uses the public hosts `https://public.api.bsky.app` and `https://api.bsky.app` (see `collect_bsky.py`).

## Analytical questions

1. **Propagation.** How does an AI-related post propagate through engagement (reposts, replies, quotes), and does the *substance and sentiment* of follow-on text change as attention fans out?
2. **News accounts.** How confidently do established news outlets write about AI (hedging vs. attribution), and how distinct are outlet groups in their framing?
3. **Themes.** Which AI-related themes carry which emotional signatures, and how does emotional composition drift over time?

(The notebook also discusses why strict "misinformation" labeling was deferred in favor of linguistic proxies; see `week6.md`.)

## Viewing the notebook on GitHub

You do **not** need to install Python to read the analysis: open the repository on GitHub, browse to `week6/week6_mp1_starter.ipynb`, and GitHub will render the notebook (markdown, code, and static outputs) directly in the browser. Interactive Plotly controls (dropdowns, hovers) work best after cloning the repo and running the notebook locally; for a read-only pass, the rendered notebook on GitHub plus the exported PNGs (`chart_4a_*.png` through `chart_4d_*.png`) are enough.

## Local reproduction (optional)

Clone the repo, create a Python environment, install the packages used in the notebook (`pandas`, `plotly`, `kaleido`, `vaderSentiment`, `nrclex`, `nltk`, `requests`), then either regenerate `bsky_posts_collected.csv` via `collect_bsky.py` (plus the two enrichment scripts) or supply your own copy. Open `week6_mp1_starter.ipynb` in Jupyter or VS Code and run all cells.
