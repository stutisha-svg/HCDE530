# Design Buddy — Privacy, Notion export, and review notes

## Listing copy (Figma Community)

**Short description**

Daily reflection prompts for HCD designers. Save reflections locally in Figma and optionally export compiled documents to your own Notion workspace.

**Privacy / data handling**

Reflections stay in Figma local storage. Notion export uses your own workspace via OAuth; we do not store your Notion token or reflection content on our servers.

**Notion export**

Connect your own Notion account to export compiled documents. Each export goes to a page you choose in your workspace. Design Buddy does not write to the plugin developer’s Notion workspace.

---

## Notes for Figma reviewers (Notion OAuth)

1. Open **View 5 (Log)** → **Documents** tab → **Connect Notion** (or **Export all to Notion**, which opens setup if needed).
2. Click **Connect with Notion**. Sign-in opens in your **external browser** (expected for Figma desktop).
3. Complete Notion authorization and page access in the browser.
4. When the browser tab shows **Connected to Notion**, return to the plugin.
5. Sign-in usually completes **automatically** within a few seconds. If the plugin does not advance, click **Finish Notion sign-in**.
6. If automatic completion fails (common in Figma desktop due to sandbox limits), click **Paste connection code instead**, copy the code from the browser tab, paste it into the plugin, and click **Finish Notion sign-in** again.
7. Choose a **parent page** for exports → **Save destination**.
8. Export a document with **Export all to Notion** or per-document **Export to Notion**.

**Backend:** `https://design-buddy-proxy.vercel.app` — OAuth config, token redeem, page search, and export only. No user tokens or reflection content are persisted on the server.

---

## Project limitations

### Notion OAuth in Figma desktop

Figma runs the plugin UI in a sandboxed iframe. OAuth completes in the **system browser**, which cannot reliably `postMessage` back to the plugin or share clipboard data with it.

**Primary path:** server polling after browser authorization (automatic when it succeeds).

**Backup path:** user copies a short-lived connection code from the browser success page and pastes it into the plugin. This is documented in the connect modal (“Paste connection code instead”) and only appears when automatic sign-in does not complete.

This is a **Figma platform constraint**, not a product choice to require manual tokens.

### Local-first storage

Reflections and compiled documents are stored in `figma.clientStorage` on the user’s machine. Clearing plugin data or switching machines does not sync reflections unless the user exports elsewhere (e.g. Notion).

### Notion export scope

Export sends compiled document reflections (text, metadata, optional frame preview images) to the user’s chosen Notion parent page. Incremental re-exports append new reflections to the same Notion page for that document.

---

## Pre-submission checklist

- [ ] Production Vercel env uses `NOTION_CLIENT_ID`, `NOTION_CLIENT_SECRET`, `NOTION_REDIRECT_URI` only (no `NOTION_INTEGRATION_TOKEN` / `NOTION_PARENT_PAGE_ID`).
- [ ] Full flow tested: connect → pick parent page → export → content appears in **reviewer’s own** Notion workspace.
- [ ] Listing text includes privacy statement above.
- [ ] Review notes include OAuth steps above for marketplace review.
