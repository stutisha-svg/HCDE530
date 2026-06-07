# Design Buddy: MP2 Competency Notes

This document expands on the four competency claims in `reflection.md`: what each one meant in practice, what I learned, and how that learning showed up again later in the build.

---

## C8: Building and deploying a complete tool

**What it covers:** Scoping, declaring, building, and shipping a project that does something real for a real HCD use case, and reflecting on the process honestly.

**Learning:** A "complete tool" is not every feature in the brief; it is a coherent loop someone can actually use. Design Buddy's value is the situated reflection practice (anchor → draw → reflect → log → compile → export), not checkbox coverage of Step 13 AI or a separate document screen. I learned to treat scope as a design decision: merging View 6 into View 5's Documents tab kept the log hub as the single return point instead of splitting history and output across two views. Deferring the AI follow-up was not failure; it was choosing shippability over feature count.

**How I applied it further:** Once the core loop worked, I kept extending *within* that frame rather than adding parallel surfaces. Compile mode, Break apart restore, rename/preview/delete on documents, incremental Notion sync, and the quick-log FAB all serve the same hub. `BUILDLOG.md` and `HANDOVER.md` became part of the deliverable: when context windows filled, I wrote handover notes so the project could survive session breaks without losing intent. That habit of documenting state and next steps is how I treated "deployed" as ongoing, not a single final commit. The reflection itself (including naming what broke, like OAuth handoff and storage limits on Break apart) is part of C8: shipping honestly includes saying what is not done yet.

---

## C1: Vibecoding and rapid prototyping

**What it covers:** Using tools like Cursor to build from plain-language descriptions, iterating on output, and judging what the tool got right versus what it did not.

**Learning:** Vibecoding is fast at scaffolding and slow at edge cases. Cursor generated workable first passes for `ui.html` layout, `code.js` message handlers, and the Vercel proxy routes, which let me prototype Views 1–5 quickly. It was weaker on Figma-specific constraints: the desktop sandbox, `clientStorage` size limits, and the rule that plugin UI cannot load local asset files (which is why deck icons and the loading GIF had to be inlined or embedded via scripts in `assets/` and `scripts/`). I learned to use AI output as a draft layer: accept the structure, then rewrite the parts that touch platform limits.

**How I applied it further:** Iteration became a pattern of *generate → run in Figma → reject or refine*. When Notion OAuth stuck on "Waiting for Notion," I did not keep prompting blindly; I traced the handoff failure and pivoted to polling plus a finish button and paste-as-backup. When Break apart failed silently, I traced storage order (saving reflections before removing the document doubled data and hit the 5MB cap) and compile paths where `postMessage` dropped large `reflections` arrays. Deck icons moved into `assets/decks/` with `embed-deck-icons.py` precisely because rapid UI generation does not solve "Figma iframe cannot read `./icon.png`." C1 here means knowing when vibecoding accelerates the loop and when I need to read, test, and patch manually.

---

## C4: APIs and data acquisition

**What it covers:** Pulling structured data from web APIs, reading documentation, and handling authentication safely.

**Learning:** Notion's API is powerful but picky: API version headers, block payload limits, rich text chunking at 2000 characters, and file uploads that require create → upload → poll until `uploaded` before attaching blocks. OAuth added another layer: client ID/secret and redirect URI on Vercel, token exchange, and never storing user content on the proxy. I learned to read docs for the failure modes, not just the happy path, because export errors like "failed to append blocks" only made sense after aligning version and upload lifecycle.

**How I applied it further:** The plugin UI never calls Notion directly with secrets. It talks to `design-buddy-proxy` on Vercel; the proxy holds OAuth client credentials in env vars while user `accessToken` and `parentPageId` live in `figma.clientStorage`. Export requests send document metadata and pending reflections; the proxy creates or updates pages and returns `pageId` and `pageUrl`. Incremental sync (`notionExportedReflectionIds` per document) applied C4 again at the product level: the second export is a different API question ("append only new blocks") than the first. Auth evolved from a shared integration token (wrong for a public plugin) to per-user OAuth, then to desktop-specific handoff routes (`/api/notion-oauth/token`, redeem, config). Each pivot was reading the API *and* the deployment environment together.

---

## C7: Critical evaluation and professional judgment

**What it covers:** Evaluating AI-generated and tool-generated output before acting on it; knowing when to trust, when to verify, and how to communicate confidence.

**Learning:** Generated code often *looks* complete before it is trustworthy. I treated Figma reload, Notion page inspection, and storage inspection as verification steps, not optional QA. Marketplace feedback (.md download insufficient; need user-owned export) was a stakeholder signal to re-evaluate the document strategy, not defend the original brief. I learned to separate "works in the agent session" from "works in the user's Figma file with real frame PNGs and real OAuth in the system browser."

**How I applied it further:** Judgment calls stacked over time. Replace `.md` download with Notion export after feedback. Remove per-document "Open in Notion" when sync status text communicated enough. Add privacy copy on Views 1, 3, and 5 only after the local-first architecture was real, not aspirational. When auto OAuth failed in desktop Figma, I did not ship silence: finish button, polling, and paste-as-backup communicate lowered confidence in the automatic path while preserving a recovery path. Break apart restore got the same treatment: abort if nothing is restorable, save document removal before re-adding reflections, parse markdown fallback when `doc.reflections` is empty. C7 is the competency that turns C1's speed into something a reviewer or user can trust.

---


