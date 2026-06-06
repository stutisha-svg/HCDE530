# Notion OAuth setup (Design Buddy proxy)

Exports go to **each user's own Notion workspace**. The proxy does not store user tokens.

## 1. Create a public Notion integration

1. Open [notion.so/my-integrations](https://www.notion.so/my-integrations).
2. **New integration** → type **Public**.
3. Capabilities: **Read content**, **Update content**, **Insert content** (required for export and image upload).
4. Add redirect URI (production):
   - `https://design-buddy-proxy.vercel.app/api/notion-oauth/callback`
5. Copy **OAuth client ID** and **OAuth client secret** (not the internal `ntn_` secret).

## 2. Vercel environment variables

On the `design-buddy-proxy` project:

| Variable | Value |
|----------|--------|
| `NOTION_CLIENT_ID` | OAuth client ID from step 1 |
| `NOTION_CLIENT_SECRET` | OAuth client secret from step 1 |
| `NOTION_REDIRECT_URI` | `https://design-buddy-proxy.vercel.app/api/notion-oauth/callback` |

**Remove from production** (Figma marketplace compliance):

- `NOTION_INTEGRATION_TOKEN`
- `NOTION_PARENT_PAGE_ID`

Redeploy after changing env vars.

## 3. API routes

| Route | Purpose |
|-------|---------|
| `GET /api/notion-oauth/config` | Public OAuth client ID + redirect URI for the plugin |
| `GET /api/notion-oauth/callback` | OAuth code exchange → `postMessage` to plugin UI |
| `POST /api/notion-pages` | Search pages the user shared during OAuth (picker) |
| `POST /api/notion-export` | Create/append document pages (requires user `accessToken` + `parentPageId`) |

## 4. Figma listing copy

Suggested wording:

> Exports go to the Notion workspace you connect. Reflections stay in Figma local storage; we do not store your Notion token or reflection content on our servers.
