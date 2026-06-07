# Design Buddy — Agent Handover

**Date:** 2026-06-02  
**Reason:** Context window full. Do not continue building in this session.

---

## What has been built and is working (verified)

### Foundation (Steps 1–3)

| Step | Status | Notes |
|------|--------|-------|
| 1. `manifest.json` + `code.js` scaffold | Working | Panel **360×480**; plugin opens; `close` message supported |
| 2. Design system in `ui.html` | Working | CSS variables, Figtree + Amatic SC + Material Symbols Outlined (CDN), `.btn`, `.buddy-card`, modals |
| 3. `prompts.json` | Working | 20 Inspiration / 12 Connections / 12 Interfacing + 3 thread strings |

### Views and core flow

- View 1 Anchor: selectionchange preview, editable anchor name, committed anchor gate, View 2 transition.
- View 2 / 2b Draw: 2x2 deck cards, thread lock/unlock, prompt draw, max-2 redraw, surprise lock behavior, preview path to View 3.
- View 3 Reflect: anchor, deck indicator, prompt/context, response textarea, save path.
- View 4 Saved: continue reflecting and log entry points.
- View 5 Log Hub: Reflections/Documents tabs, compile selected to docs, rename/delete/restore, preview modal, start-new card.

### Notion integration (new)

- Added standalone backend at sibling folder `design-buddy-proxy`.
- New route `api/notion-export.js` deployed on Vercel and active.
- Uses server env vars:
  - `NOTION_INTEGRATION_TOKEN`
  - `NOTION_PARENT_PAGE_ID`
- Exports include frame PNGs using Notion File Upload API.
- Incremental sync behavior added:
  - Per-document metadata tracked in stored docs (`notionPageId`, `notionPageUrl`, `notionLastExportedAt`, `notionExportedReflectionIds`).
  - Subsequent exports append only new reflections.
- Export success opens Notion page URL in browser.

### View 5 / navigation polish (new)

- Footer button renamed to **Export all to Notion**.
- Document cards show Notion sync status marker (not exported vs synced count + timestamp).
- Removed document-level **Open in Notion** button per user request.
- Added floating quick-log FAB (Material Symbols document icon) with count badge.
- FAB moved to top-right and reduced size (~20%).
- Back behavior from View 5 now checks state:
  - If frame/prompt missing, back routes to View 1.
  - Otherwise regular flow back to View 4.

### Storage and handlers

| Key | Purpose |
|-----|---------|
| `reflections` | Array of reflection entries (newest first) |
| `documents` | Compiled docs and sync metadata |

`code.js` handlers include `update-document` patch support (`msg.patch`) for metadata updates.

---

## What is in progress and its current state

| Item | State |
|------|-------|
| Notion export end-to-end UX | Working with correct Notion integration setup and shared parent page |
| Build log and commit hygiene | Multiple uncommitted changes expected in `ui.html`, `code.js`, and `design-buddy-proxy` |
| AI API step | Deferred; Step 13 files intentionally left in place |

---

## What has not been started yet

Per `cursorrules` §14 build order (remaining):

| Step | Item |
|------|------|
| 13 | **AI API call** — follow-up question on View 4 after save |
| 14 | Notion stretch enhancements beyond current export flow |
| — | `README.md` updates |
| — | Full documented end-to-end test pass |

---

## Decisions that deviate from the brief (and why)

| Topic | Brief | Actual | Why |
|-------|-------|--------|-----|
| View 5 docs action | `.md` document download action | Replaced with **Export to Notion** | User-directed priority shift |
| Notion auth UX | Prompt-token from UI (earlier iteration) | Server env-based integration token + parent page | User wanted plugin to handle auth setup internally |
| View 5 footer doc button | Connect Notion | Export all to Notion | User request |
| Quick access | No global jump | Floating top-right doc FAB to View 5 | User request |

---

## Unresolved questions and problems

1. Confirm final desired behavior for View 5 back routing in all entry combinations after latest state-based guard.
2. Validate rate-limit behavior when “Export all to Notion” runs across many docs sequentially.
3. `prompts-data.js` remains legacy/unused.
4. AI Step 13 remains deferred and not wired.

---

## Guardrails (full restatement from `cursorrules`)

### 0. What this project is

A Figma plugin called Design Buddy. It opens as a small panel (240 × 480px) inside Figma  
and prompts HCD designers to reflect on their work at the end of each day. Reflections are  
saved locally via figma.clientStorage and exported as a .md file. The full specification  
lives in readme.md. Read that file before writing any code.

### 1. Version control — human commits, agent stages

After every sub-feature is built, tested, and reviewed:
- Stop and tell the user exactly what was completed and what to commit.
- Suggest a commit message in this format: `feat: [what was built]` or `fix: [what was fixed]`
- Do not proceed to the next task until the user confirms the commit has been made.
- Never commit on behalf of the user. Version control is the user's responsibility.

Sub-features that each warrant their own commit:
- Design system and base CSS variables
- Each individual View (View 1, View 2, View 3, View 4, View 5, View 6)
- prompts.json populated with all 18 prompts
- code.js scaffold (plugin opens and communicates with UI)
- Local storage: save reflection
- Local storage: retrieve reflections
- Builds-on-previous prefix logic
- Markdown export (.md download)
- AI API call (added last)
- Notion integration (stretch goal, added last)

### 2. Context handover — when memory fills

If your context window is approaching its limit:
- Do not continue building.
- Write a file called `HANDOVER.md` in the project root.
- It must include:
  - What has been built and is working (verified)
  - What is in progress and its current state
  - What has not been started yet
  - Any decisions made that deviate from the brief, and why
  - Any unresolved questions or problems
  - All guardrails from this .cursorrules file, restated in full
  - The next step the incoming agent should take, precisely described
- Tell the user: "Context is filling. I've written HANDOVER.md. Please start a new session
  and paste that file along with .cursorrules and the brief."

### 3. No assumptions

Before making any decision not explicitly covered in the brief or this file:
- Stop and ask.
- State what you were about to do and why you were uncertain.
- Wait for a response before proceeding.

This applies to:
- Project structure and file organisation
- Database schema or storage structure
- UI layout decisions not specified in the brief
- Which library or dependency to use
- Naming conventions
- Scalability or architecture choices
- Anything you are inferring rather than reading directly from the spec

When in doubt, ask. A question takes 10 seconds. A wrong assumption can break the build.

### 4. Task breakdown and verification

For every task from the brief:
- Break it into the smallest implementable sub-steps before writing code.
- Share the breakdown with the user for confirmation before starting.
- After completing each sub-step: test it, check for bugs and console errors, then report
  back with what was built, what was tested, and what the result was.
- Do not move to the next sub-step until the user has reviewed and approved the current one.

Report format after each sub-step:
```
BUILT: [what was implemented]
TESTED: [how it was verified]
RESULT: [what works, what doesn't]
READY FOR REVIEW: [what the user should check]
NEXT: [what comes after approval]
```

### 5. Blast radius — declare before changing

Before making any change that affects more than one file, or that modifies existing working
code:
- Stop.
- Name every file that will be changed.
- Describe exactly what will change in each file.
- Describe how this affects the rest of the project — what could break, what depends on it.
- Ask for explicit confirmation before proceeding.

Format:
```
BLAST RADIUS
Change: [what you're about to do]
Files affected: [list every file]
Impact: [what this changes in the broader project]
Risk: [what could break]
Waiting for confirmation before proceeding.
```

### 6. Never touch working code unprompted

- Do not refactor, rename, reorganise, or clean up any code that is already working unless
  the user explicitly asks for it.
- Do not add comments, reformat whitespace, or change variable names in working files as a
  side effect of another task.
- If you notice something that could be improved, flag it as a suggestion after the current
  task is complete. Do not act on it without instruction.

### 7. One file at a time

- Never edit more than one file in a single step.
- If a task genuinely requires changes to multiple files, list all the files first, explain
  why each needs to change, and get confirmation before touching any of them.

### 8. Bug fixing limit

- If a bug is not resolved after 2 attempts, stop trying.
- Explain the problem clearly: what the bug is, what you tried, why it didn't work, and
  what you think the root cause is.
- Ask the user how to proceed.
- Do not keep making changes hoping something will work.

### 9. Dependencies

- Never install a new package or import an external library without flagging it first.
- State: the package name, what it does, why it is needed, and whether a native alternative
  exists.
- Wait for confirmation before installing.
- Prefer native browser APIs and the Figma Plugin API over third-party dependencies
  wherever possible.

### 10. Build log

Maintain a file called `BUILDLOG.md` in the project root.
After every confirmed commit, append one line in this format:
```
[date] | [commit message] | [what was tested] | [next step]
```
This file is never deleted. It is the running record of the build.

### 11. Protected files

The following files must never be deleted, overwritten, or modified unless the user
explicitly instructs it:

- `prompts.json` — this is source content, not code. It was written before the build began.
- `.cursorrules` — this file.
- `BUILDLOG.md` — the build record.
- `readme.md` — the project specification.

If any task seems to require modifying these files, stop and ask first.

### 12. Icons — Material 3 (Material Symbols)

All UI icons must use **Google Material Symbols** (Material 3 style), not custom strokes
or legacy Material Icons 24px paths.

- **Source:** [Material Symbols](https://fonts.google.com/icons) — **Outlined** only.
- **Delivery:** Load `Material Symbols Outlined` from Google Fonts in `ui.html` and use
  ligatures via `<span class="material-symbols-outlined m3-icon">icon_name</span>`.
  Define names once in `M3_ICON` in `ui.html` — do not hand-draw SVG paths.
- **Rename / edit actions:** use the **`stylus`** icon (pencil only). Do **not** use
  `edit` — that glyph is a pencil on a document and is wrong for rename buttons.
- **Size:** 16px via `.material-symbols-outlined.m3-icon` (`opsz` 24).
- **Accessibility:** `aria-hidden="true"` on the span; `aria-label` on the parent
  `<button>`.

When adding a new icon, add its ligature name to the Google Fonts `icon_names` list in
`ui.html`, then add it to `M3_ICON`.

### 13. Plugin size and layout (fixed)

The plugin panel is **360 × 480px** (set in `code.js`). Do not change panel dimensions.

**No scroll** inside any view. **No overlapping elements.** If content does not fit, reduce
spacing or card size — never add `overflow-y: auto` to views.

### Buddy card dimensions (CSS variables in `ui.html`)

| Variant | View | Size (W × H) | Ratio |
|---------|------|--------------|-------|
| Deck pick | View 2 | **120 × 170px** | 120∶170 |
| Drawn prompt | View 2b | **216 × 306px** | same 120∶170 |

Use the shared `.buddy-card` component for all cards. Deck indicator on View 2b sits **on**
the prompt card (`.buddy-card__badge`), not above the panel.

### Bottom navigation (View 2b and any view with back + continue)

Back and continue must share one **horizontal row** at the bottom (`.view-nav`):
back (left), continue (right). Do **not** absolutely position these over the card or action
buttons. Action rows (Redraw, Surprise me) sit **above** `.view-nav`, never overlapping it.

View 2: deck grid **248px** wide (2×120 + 8 gap); Surprise me button matches that width.

### View 2b — Redraw and Surprise me (behavior)

- **Redraw:** max **2** per visit to View 2b (one deck pick). After 2 redraws, hide Redraw only.
- **Surprise me (View 2b):** when tapped, draw a new random prompt and then **lock** the screen:
  hide **Redraw**, **Surprise me**, and **Back** so the user cannot return to deck pick and get
  another redraw/surprise cycle. **Continue** stays visible to advance to Reflect.
- Reset redraw count and control visibility only when entering View 2b from a new deck pick
  (View 2).

### 14. Build order

Follow this order. Do not skip ahead.

1. manifest.json + code.js scaffold — plugin opens in Figma, panel appears
2. Design system — CSS variables, typography scale, base component styles
3. prompts.json — all 18 prompts plus thread variants
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
14. Notion integration (stretch goal)

UI milestone (June 3): Views 1–4 fully designed and interactive.
Full build milestone (June 6): All features working end to end.

### 15. When to stop and ask vs. when to proceed

Proceed without asking:
- Writing code that is fully specified in the brief
- Fixing a bug within the file you are currently working on (first 2 attempts)
- Appending to BUILDLOG.md

Stop and ask:
- Anything not covered in the brief
- Any change affecting more than one file
- Any new dependency
- Any structural or architectural decision
- Any deviation from the build order
- Any modification to a protected file
- Any bug that persists after 2 attempts

---

## Next step for the incoming agent (precise)

1. Read `cursorrules`, `readme.md`, and this file.
2. Confirm current `git status` and have user commit current uncommitted work.
3. Verify in Figma:
   - View 5 back-routing state logic (frame/prompt missing => View 1; else View 4).
   - Export all + incremental Notion sync behavior.
   - Floating FAB position/size/icon in all views.
4. Only after user confirms stability, continue with remaining brief items (`README`, AI step, extra Notion polish).

---

## Project files (current)

```
mp2/
├── manifest.json
├── code.js
├── ui.html
├── prompts.json
├── scripts/
│   └── embed-prompts-in-code.js
├── prompts-data.js            (legacy; unused)
├── cursorrules
├── readme.md
├── BUILDLOG.md
└── HANDOVER.md

design-buddy-proxy/            (sibling folder, NOT inside mp2)
├── api/
│   ├── reflect.js             (Step 13 route; untouched)
│   └── notion-export.js       (active Notion export route)
├── package.json
├── .env.example
└── .gitignore
```

---

*End of handover.*
