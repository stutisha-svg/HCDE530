[2026-05-31] | feat: plugin scaffold (manifest, panel open) | Plugin opens in Figma at 360×480, native close works | Step 2: design system
[2026-05-31] | feat: design system (CSS variables, typography, base components) | Smoke test in Figma: fonts, cards, SVG deck indicators, buttons, textarea, reveal animation | Step 3: prompts.json
[2026-05-31] | feat: prompts.json with full prompt deck and thread variants | JSON valid: 20/12/12 deck prompts + 3 thread strings | Step 4: View 1 — Anchor
[2026-05-31] | feat: View 1 — Anchor (loading, selectionchange, anchor preview) | Figma: frame select, preview, rename, arrow to View 2; fix view--hidden + anchorCommitted | Step 5: View 2 — Draw
[2026-05-31] | feat: View 2 deck pick + View 2b prompt draw | Vertical playing cards, Thread locked, Surprise me + dice; 2b card animation, Redraw/Surprise row | Verify in Figma; commit if pending; Step 6: View 3 — Reflect
[2026-05-31] | fix: View 2b prompts via prompts-data.js + layout | Blank prompt fixed; playing-card ratio; secondary CTAs; deck indicator on 2b | User re-test View 2b; then View 3 Reflect
[2026-05-31] | feat: View 2/2b complete + View 3 Reflect UI | Figma: deck pick, draw, redraw/surprise lock, reflect + save to stub | Step 7: View 4 — Saved
[2026-05-31] | fix: load prompts via code.js postMessage + View 2/2b UX | Prompts embedded in code.js; 2x2 grid; auto-advance to 2b; buddy cards; bottom nav; flip Context on card | View 3 polish + View 4
[2026-05-31] | feat: View 3 — Reflect with Context and review tabs | Anchor, deck indicator, prompt, Context box, textarea, frame/card tabs, save flow | Step 4: View 4 — Saved
[2026-05-31] | feat: View 4 — Saved confirmation screen | Saved message, log/document actions, close via code.js | Step 5: View 5 — Log
[2026-05-31] | feat: View 5 — reflection log | Scrollable log, expandable prompts, in-memory then clientStorage | Step 6: Document generation
[2026-05-31] | feat: persist reflections with figma.clientStorage | Save/load on plugin open; reflections survive close; Thread unlock from count | Step 9: View 6 — Document generation
[2026-05-31] | chore: sync prompts.json into code.js | User-edited prompts.json regenerated via embed script | Reload plugin; then View 6
[2026-06-01] | feat: View 6 export screen + thread excerpt substitution | View 6: full log .md download, Notion stub; Thread prompts use {past_excerpt}; View 4 export entry | Step 13: AI API call
[2026-06-01] | refactor: merge View 6 into View 5 | Export all .md on Reflections tab; Notion on Documents tab; View 4 simplified | Step 13: AI API call
