# Design Buddy — Agent Handover

**Date:** 2026-06-01  
**Reason:** Context window full. Do not continue building in this session.

---

## What has been built and is working (verified)

### Foundation (Steps 1–3)

| Step | Status | Notes |
|------|--------|-------|
| 1. `manifest.json` + `code.js` scaffold | Working | Panel **360×480**; plugin opens; `close` message supported |
| 2. Design system in `ui.html` | Working | CSS variables, Figtree + Amatic SC + Material Symbols Outlined (CDN), `.btn`, `.buddy-card`, modals |
| 3. `prompts.json` | Working | 20 Inspiration / 12 Connections / 12 Interfacing + 3 thread strings |

### View 1 — Anchor

- Loading animation (~1.5s)
- Copy: *"What stayed with you today?"* + frame/component/token subtext
- `selectionchange` in `code.js` → PNG preview or fallback + name; editable name; remove selection
- `anchorCommitted`; nav arrow → View 2
- **Start new reflection** from View 5 pre-selects exclusive deck and skips View 2 after anchor (`initView2(true)` + `goToView2b()`)

### View 2 / View 2b — Draw

- 2×2 deck grid **120×170px**; tap deck or Surprise me → auto View 2b
- Thread locked until `reflectionCount >= 3`
- Buddy card **216×306px**; Context flip; Redraw max 2; Surprise me locks Redraw/Surprise/Back
- `.view-nav` back + continue; View 3 preview from card tab

### View 3 — Reflect

- Anchor, deck indicator, prompt, Context box, textarea, Save
- Frame/card tabs; **"Earlier you noted:"** from newest reflection
- Saves `anchorImage` (frame PNG) when available for document preview later

### View 4 — Saved

- *"Saved. See you tomorrow."*
- **See all reflections** → View 5
- **Go back to reflecting more** → View 3 with **same reflection text preserved** (does not clear textarea)
- No Close text button; no separate export screen (export lives in View 5)

### View 5 — Log (expanded hub; replaces brief View 5 + View 6)

**Reflections tab**

- Black **Start new reflection** card (least-used deck)
- Reflection cards: delete (confirm modal), expandable prompt
- **Compile document** mode: select cards → **Compile selected** → modal (existing documents list + **Add to new document**)
- Footer: **Download all as .md** (all loose reflections, brief markdown format) — was View 6

**Documents tab**

- Document cards: title + **stylus** rename (Material Symbols), preview modal (anchor, deck, prompt, context, reflection, frame image when saved), **Break apart** (restore to Reflections tab), per-doc **Download .md**, delete (confirm modal)
- Footer: **Connect Notion** disabled, "Coming soon"

**Navigation**

- Round back button (`.view-nav`) → View 4
- Only View 5 list area scrolls

### Storage — `figma.clientStorage`

| Key | Purpose |
|-----|---------|
| `reflections` | Array of reflection entries (newest first) |
| `documents` | Array of compiled docs: `{ id, name, date, createdAt, updatedAt, reflections[], markdown }` |

**`code.js` message handlers**

- `get-prompts`, `get-reflections` → `reflections-loaded` with `{ data, documents }`
- `save-reflection`, `delete-reflection`
- `compile-reflections` (mode `new` or `append`)
- `restore-document`, `update-document`, `delete-document`
- `close`
- `selectionchange` / PNG export

### Prompts

- Embedded as `PROMPTS_DATA` in `code.js` via `node scripts/embed-prompts-in-code.js`
- **Thread:** `{past_excerpt}` replaced at draw time via `getThreadPromptText()`

### Icons

- Material Symbols Outlined font (`delete`, `download`, `stylus` for rename — **not** `edit`)
- `M3_ICON` map in `ui.html`

---

## What is in progress and its current state

| Item | State |
|------|--------|
| **Git / commits** | BUILDLOG updated through 2026-06-01; **confirm `git status`** — substantial session work may be uncommitted |
| **Figma end-to-end test** | User has tested pieces; full regression after reload recommended |
| **View 6** | **Removed** — merged into View 5 (see below) |

---

## What has not been started yet

Per `cursorrules` §14 build order (remaining):

| Step | Item |
|------|------|
| 13 | **AI API call** — follow-up question on View 4 after save; needs `code.js` + env key; user approval for API wiring |
| 14 | **Notion integration** (stretch) |
| — | `README.md` |
| — | End-to-end test pass documented |

Build order steps 9–12 are **functionally complete** in View 5 (markdown export, compile, storage, thread excerpt). No separate View 6 screen exists.

---

## Decisions that deviate from the brief (and why)

| Topic | Brief | Actual | Why |
|-------|--------|--------|-----|
| Panel size | 380×600 / 240×480 in places | **360×480** | User-approved scaffold |
| View 1 | Button + textarea anchor | Selection-change + rename | User rework |
| View 2 | Select on same screen | Tap → immediate View 2b | User request |
| View 4 | Generate document → View 6; Close | See reflections; go back reflecting; export in View 5 | User UX iterations |
| View 5 | Simple scrollable log | **Tabs:** Reflections + Documents; compile, modals, start-new card | User request |
| View 6 | Dedicated export screen | **Merged into View 5** footers | User consolidation request |
| Prompt count label | "18 prompts" | **44** deck prompts in JSON | Full brief deck |
| Prompts in UI | fetch `prompts.json` | **`PROMPTS_DATA` in `code.js`** | Figma iframe cannot fetch sibling files reliably |
| View 5 scroll | No scroll in views | **View 5 list scrolls** | Brief requires scrollable log |
| Storage order | After View 6 | **Early** | Reflections must persist |
| Compile flow | View 6 download all | **Per-doc compile** + download all on Reflections tab | User request |
| Rename icon | edit | **`stylus`** Material Symbol | `edit` glyph is pencil-on-document; poor at 14px |

---

## Unresolved questions and problems

1. **AI API** — Figma plugin UI cannot call Anthropic directly with env vars the same way as Node; need pattern (e.g. backend proxy, or `figma.clientStorage` token field + user paste). Confirm approach with user before implementing.
2. **Uncommitted work** — Run `git status`; suggest commits for View 5 hub, View 4 polish, `code.js` document handlers, `cursorrules` icons section.
3. **`prompts-data.js`** — Legacy; UI unused. Delete only with user approval.
4. **Legacy documents** — Docs compiled before `reflections[]` snapshot may lack break-apart data; preview falls back to markdown text only.
5. **`cursorrules` §0** — Still says 240×480; §13 says 360×480 (use §13).

---

## Guardrails (full restatement from `cursorrules`)

### 0. What this project is

A Figma plugin called Design Buddy. It opens as a small panel inside Figma and prompts HCD designers to reflect on their work at the end of each day. Reflections are saved locally via `figma.clientStorage` and exported as a `.md` file. The full specification lives in `design-buddy-cursor-brief.md`. Read that file before writing any code.

### 1. Version control — human commits, agent stages

After every sub-feature is built, tested, and reviewed:

- Stop and tell the user exactly what was completed and what to commit.
- Suggest a commit message: `feat: [what was built]` or `fix: [what was fixed]`
- Do not proceed until the user confirms the commit.
- Never commit on behalf of the user.

### 2. Context handover — when memory fills

If context window is approaching its limit: do not continue building; write `HANDOVER.md`; tell user to start new session with HANDOVER.md + `cursorrules` + brief.

### 3. No assumptions

Before any decision not in brief or rules: stop, ask, wait.

### 4. Task breakdown and verification

Break tasks into sub-steps; share for confirmation; report BUILT / TESTED / RESULT / READY FOR REVIEW / NEXT; wait for approval.

### 5. Blast radius — declare before changing

Before multi-file or working-code changes: list files, impact, risk; ask confirmation.

### 6. Never touch working code unprompted

No refactor/cleanup unless user asks.

### 7. One file at a time

Never edit more than one file per step unless blast radius approved.

### 8. Bug fixing limit

Stop after 2 failed fix attempts; explain and ask user.

### 9. Dependencies

Flag new packages; prefer native APIs; Google Fonts (Figtree, Amatic SC, Material Symbols) already approved.

### 10. Build log

Maintain `BUILDLOG.md`; append after every confirmed commit: `[date] | [commit message] | [what was tested] | [next step]`. Never delete.

### 11. Protected files

Never delete/overwrite/modify unless user instructs: `prompts.json`, `cursorrules`, `BUILDLOG.md`, `design-buddy-cursor-brief.md`. Ask before modifying.

### 12. Icons — Material 3 (Material Symbols)

All UI icons: Google Material Symbols Outlined via font ligatures in `ui.html` (`M3_ICON`). Rename uses **`stylus`**, not `edit`. 16px. `aria-label` on buttons.

### 13. Plugin size and layout (fixed)

Panel **360×480px**. No scroll inside views except View 5 list. No overlapping elements. Buddy cards: deck **120×170px**; prompt **216×306px**. View 2b: `.view-nav` for back/continue; max 2 redraws; Surprise me locks screen.

### 14. Build order

1. manifest + code.js scaffold ✓  
2. design system ✓  
3. prompts.json ✓  
4. View 1 ✓  
5. View 2 ✓  
6. View 3 ✓  
7. View 4 ✓  
8. View 5 ✓ (includes former View 6 export/Notion stub)  
9. View 6 — **merged into View 5** (no separate view)  
10. Local storage: save ✓  
11. Local storage: retrieve + builds-on-previous + thread excerpt ✓  
12. Markdown export ✓ (View 5 + per-document)  
13. AI API call  
14. Notion (stretch)

### 15. When to stop and ask vs. proceed

Proceed: code fully in brief; bug fix in current file (≤2 attempts); append BUILDLOG.  
Stop and ask: not in brief; multi-file; new dependency; architecture; build order deviation; protected files; bug after 2 attempts.

---

## Next step for the incoming agent (precise)

1. **Read** `cursorrules`, `design-buddy-cursor-brief.md`, and this file.
2. **Confirm** `git status` with user; suggest commit(s) for uncommitted session work if needed.
3. **Begin Step 13 — AI API call** per brief:
   - After save, generate one follow-up question; show on View 4 under *"One more thing to sit with:"*
   - Model `claude-sonnet-4-20250514`, max 150 tokens, system prompt in brief
   - **Stop and ask user** how API key should reach the plugin (Figma UI cannot use server env vars directly)
   - Likely needs `code.js` to proxy or user-provided key in settings — declare blast radius before touching `code.js` + `ui.html`
4. **Do not** recreate View 6 as a separate screen unless user asks.

---

## Project files (current)

```
mp2/
├── manifest.json
├── code.js                    (PROMPTS_DATA + reflections/documents storage; regen via script)
├── ui.html                    (Views 1–5; modals; no View 6)
├── prompts.json               (protected source deck)
├── scripts/
│   └── embed-prompts-in-code.js
├── prompts-data.js            (legacy; unused)
├── cursorrules
├── design-buddy-cursor-brief.md
├── BUILDLOG.md
└── HANDOVER.md                (this file)
```

---

*End of handover.*
