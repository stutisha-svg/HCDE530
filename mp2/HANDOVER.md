# Design Buddy — Agent Handover

**Date:** 2026-05-31  
**Reason:** Context window full. Do not continue building in this session.

---

## What has been built and is working (verified)

### Steps 1–3 (logged in BUILDLOG.md; user confirmed commits through design system and prompts.json)

| Step | Status | Notes |
|------|--------|-------|
| 1. `manifest.json` + `code.js` scaffold | Working | Plugin opens; panel **360×480** (see deviations) |
| 2. Design system in `ui.html` | Working | CSS variables, Figtree + Amatic SC, base components; smoke-test block was later removed |
| 3. `prompts.json` | Working | 44 deck prompts (20 Inspiration / 12 Connections / 12 Interfacing) + 3 thread strings; valid JSON |

### Step 4 — View 1 (Anchor) — implemented; commit may be pending

- Launch loading animation (~1.5s): orbiting deck shapes (triangle, hexagon, square, dot), then fade to View 1
- Copy: heading *"What stayed with you today?"*, subtext about selecting frame/component/token
- **Selection via `figma.on('selectionchange')` in `code.js`** — exports PNG preview as base64 when possible; no button click required
- Display-only CTA: *"Click any frame in your file"*
- On selection: preview region (image or fallback icon + name), editable anchor name field, *Remove selection*
- `anchorCommitted` flag so Figma deselecting when clicking the plugin UI does not clear anchor before Continue
- Right arrow (bottom right) enabled when anchor is committed; navigates to View 2
- **Fix verified:** `.view--hidden { display: none !important; }` so View 1 actually hides when navigating (`.view-1` / `.view-2` `display: flex` was overriding)

### Step 5 — View 2 + View 2b — implemented; user testing ongoing

**View 2 (deck pick):**

- Four decks stacked vertically as portrait playing cards (~2:1 height:width, centered, max-width ~108px)
- Deck SVG indicators + one-line descriptions
- Thread card fourth in stack; greyed/disabled until `reflectionCount >= 3` (`setReflectionCount()` exists; storage not wired — always 0)
- *Surprise me* row with dice icon (muted, centered, no border) — selects random deck (same as tapping a deck)
- Right arrow enabled only after a deck is selected (highlight state on card)
- Arrow advances to **View 2b** (does not draw on deck tap)

**View 2b (drawn prompt):**

- Deck indicator (shape + label) at top
- Bordered prompt **card** with draw animation (~500ms fade/slide/scale)
- Prompt text from prompts deck (Amatic SC via `.text-prompt`)
- **Redraw** + **Surprise me** as horizontal `btn btn-secondary` row
- Redraw: same deck, max 2 redraws then Redraw hidden
- Surprise me (2b): random deck, resets redraw count, redraws
- Right arrow → View 3 stub (*"Reflect — Step 6"*)

**Prompts loading:**

- `fetch('./prompts.json')` fails in Figma UI iframe (blank View 2b was reported)
- **`prompts-data.js` added** — `window.__DESIGN_BUDDY_PROMPTS__` loaded via `<script src="prompts-data.js">` in `ui.html`
- Regenerate when `prompts.json` changes:
  ```powershell
  node -e "const fs=require('fs'); const p=fs.readFileSync('prompts.json','utf8'); fs.writeFileSync('prompts-data.js', 'window.__DESIGN_BUDDY_PROMPTS__ = ' + p + ';\n');"
  ```

### `code.js` (current)

- `figma.showUI` 360×480
- `selectionchange` → `selection` / `selection-cleared` messages (with PNG export + fallback)
- No `get-selection` onmessage handler (removed)
- No `close` handler (native panel close only)

---

## What is in progress and its current state

| Item | State |
|------|--------|
| **View 2 / View 2b** | Last rework addressed blank prompt, playing-card layout, dice icon, secondary CTAs, card animation. **Needs full Figma re-test** after reload |
| **Commits** | BUILDLOG ends at Step 4 start. View 1, View 2, `prompts-data.js`, and fixes may be **uncommitted** — confirm with `git status` |
| **View 3 stub** | Placeholder only; `appState` receives `anchor`, `deck`, `prompt`, `helperText` on 2b → 3 navigation but View 3 does not display them |

---

## What has not been started yet

Per `cursorrules` §13 build order:

6. View 3 — Reflect  
7. View 4 — Saved  
8. View 5 — Log  
9. View 6 — Document generation  
10. Local storage: save  
11. Local storage: retrieve + builds-on-previous prefix  
12. Markdown export  
13. AI API call  
14. Notion integration (stretch goal)

Also not done:

- `README.md`
- Wiring `get-reflections` / Thread unlock from real storage
- Helper text UI (eye toggle was built then **removed** per user; `helperText` still stored in `appState` for future use)
- Removing or syncing `prompts-data.js` automatically when `prompts.json` edits (manual regen only)

---

## Decisions that deviate from the brief (and why)

| Topic | Brief / rules | Actual | Why |
|-------|----------------|--------|-----|
| Panel size | 240×480 (`cursorrules` §12; brief snippet 380×600) | **360×480** in `code.js` | User approved 360×480 for scaffold |
| View 1 copy | *"What were you working on today?"* / *Design Buddy* | *"What stayed with you today?"* + frame/component/token subtext | User-specified View 1 rework |
| View 1 input | Button + optional textarea | Selection-change only + editable frame name; no freeform textarea | User rework; either/or removed |
| View 2 flow | Select deck → draw prompt on same view | **View 2** pick deck → arrow → **View 2b** draw | User rework |
| Prompt count | "18 prompts" in build order text | **44** deck prompts in `prompts.json` | User approved full brief deck |
| Thread unlock | Brief: 3+ reflections | Code: `reflectionCount >= 3` | User said ">3" then card copy "after 3 reflections" — implemented as **>= 3** |
| Prompts file | `prompts.json` only | **`prompts-data.js`** duplicate for UI load | Figma UI `fetch` unreliable |
| Context / helper | Eye icon for helper text on prompt | **Removed** from View 2b | User: not in brief, layout breakage |
| Google Fonts | — | Figtree + Amatic SC via CDN | User approved Step 2 |

---

## Unresolved questions and problems

1. **View 2b after latest fixes** — User reported blank card, missing indicator/animation before `prompts-data.js` fix. Re-test: indicator, animated card, prompt text, Redraw, Surprise me (2b), arrow to View 3.
2. **`prompts-data.js` in Figma** — Confirm `<script src="prompts-data.js">` loads in plugin iframe (sibling file). If not, need `code.js` to post prompts or inline JSON.
3. **Uncommitted work** — View 1, View 2, `prompts-data.js`, `HANDOVER.md` may need commits; user controls git.
4. **`cursorrules` §12 vs 360×480** — Rules still say 240×480; code uses 360×480. Align rules or code with user intent.
5. **Playing cards in 480px panel** — Four tall cards + surprise row may need scroll on `deck-stack` (`overflow-y: auto` added); verify no overlap with nav arrow.
6. **June 3 / June 6 milestones** — Views 1–4 and full E2E not met yet.

---

## Guardrails (full restatement from `cursorrules`)

### 0. What this project is

A Figma plugin called Design Buddy. It opens as a small panel inside Figma and prompts HCD designers to reflect on their work at the end of each day. Reflections are saved locally via `figma.clientStorage` and exported as a `.md` file. The full specification lives in `design-buddy-cursor-brief.md`. Read that file before writing any code.

### 1. Version control — human commits, agent stages

After every sub-feature is built, tested, and reviewed:

- Stop and tell the user exactly what was completed and what to commit.
- Suggest a commit message: `feat: [what was built]` or `fix: [what was fixed]`
- Do not proceed to the next task until the user confirms the commit has been made.
- Never commit on behalf of the user.

Sub-features that each warrant their own commit: design system; each View (1–6); `prompts.json`; code.js scaffold; local storage save/retrieve; builds-on-previous prefix; markdown export; AI API; Notion (stretch).

### 2. Context handover — when memory fills

If context window is approaching its limit: do not continue building; write `HANDOVER.md`; tell user to start new session with HANDOVER.md + `cursorrules` + brief.

### 3. No assumptions

Before any decision not explicitly in brief or rules: stop, ask, wait.

### 4. Task breakdown and verification

Break tasks into smallest sub-steps; share breakdown for confirmation; report BUILT / TESTED / RESULT / READY FOR REVIEW / NEXT after each sub-step; wait for approval.

### 5. Blast radius — declare before changing

Before multi-file or working-code changes: stop, list files, describe changes and impact, ask confirmation.

### 6. Never touch working code unprompted

No refactor/cleanup of working code unless user asks.

### 7. One file at a time

Never edit more than one file per step unless blast radius approved.

### 8. Bug fixing limit

Stop after 2 failed fix attempts; explain and ask user.

### 9. Dependencies

Flag new packages; prefer native APIs; Google Fonts already approved.

### 10. Build log

Maintain `BUILDLOG.md`; append after every confirmed commit: `[date] | [commit message] | [what was tested] | [next step]`. Never delete.

### 11. Protected files

Never delete/overwrite/modify unless user instructs: `prompts.json`, `.cursorrules`, `BUILDLOG.md`, `design-buddy-cursor-brief.md`. Ask before modifying.

### 12. Plugin size is fixed

Rules say 240×480 in `code.js` — **currently 360×480** (deviation). No scrolling within views where possible; redesign to fit.

### 13. Build order

1. manifest + code.js scaffold  
2. Design system  
3. prompts.json  
4. View 1 — Anchor  
5. View 2 — Draw  
6. View 3 — Reflect  
7. View 4 — Saved  
8. View 5 — Log  
9. View 6 — Document generation  
10. Local storage: save  
11. Local storage: retrieve + builds-on-previous prefix  
12. Markdown export  
13. AI API call  
14. Notion (stretch)

UI milestone (June 3): Views 1–4. Full build (June 6): E2E.

### 14. When to stop and ask vs. proceed

Proceed: code fully in brief; bug fix in current file (≤2 attempts); append BUILDLOG.

Stop and ask: not in brief; multi-file changes; new dependency; architecture; build order deviation; protected file edits; bug after 2 attempts.

---

## Next step for the incoming agent (precise)

1. **Read** `cursorrules`, `design-buddy-cursor-brief.md`, and this file.
2. **Ask user** to reload the plugin in Figma and confirm View 2b: deck indicator visible, prompt card animates with text, Redraw / Surprise me work, arrow reaches View 3 stub.
3. If View 2b still blank: verify `prompts-data.js` loads; consider `code.js` posting prompts on init; do not duplicate logic without blast-radius approval.
4. **Confirm git status** — commit pending work if user wants, e.g.:
   - `feat: View 1 — Anchor (loading, selectionchange, anchor flow)`
   - `feat: View 2 — Draw (deck pick + View 2b prompt draw)`
   - `fix: load prompts via prompts-data.js for Figma UI`
5. **Remove** design-system smoke-test CSS/markup if any remnants remain (already removed from body; confirm).
6. **Begin Step 6 — View 3 (Reflect)** per brief: show anchor (muted), drawn prompt, optional "Earlier you noted:" from last reflection (storage not wired yet — stub or skip until step 10–11), large reflection textarea, Save reflection button. Break into sub-steps; one file at a time where possible; share breakdown with user first.

---

## Project files (current)

```
mp2/
├── manifest.json
├── code.js
├── ui.html          (all views + design system + app logic)
├── prompts.json     (source deck — protected)
├── prompts-data.js  (UI load copy — regenerate from prompts.json when deck changes)
├── cursorrules
├── design-buddy-cursor-brief.md
├── BUILDLOG.md
└── HANDOVER.md      (this file)
```

---

*End of handover.*
