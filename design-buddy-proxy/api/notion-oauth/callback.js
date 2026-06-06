import { hasValue, sanitizeText } from '../_notion-shared.js';
import { setPendingOAuth } from './_pending.js';
import { createOAuthTicket } from './_ticket.js';

const NOTION_TOKEN_URL = 'https://api.notion.com/v1/oauth/token';

function htmlPage(title, message, payload) {
  const safePayload = JSON.stringify(payload).replace(/</g, '\\u003c');
  const showTicket = payload && payload.ok && payload.ticket;
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>${title}</title>
  <style>
    body { font-family: system-ui, sans-serif; padding: 2rem; max-width: 32rem; margin: 0 auto; color: #1a1a1a; }
    p { line-height: 1.5; }
    .hint { color: #555; font-size: 0.95rem; }
    textarea { width: 100%; min-height: 6rem; margin: 0.75rem 0; padding: 0.75rem; font: 0.85rem/1.4 ui-monospace, monospace; border: 1px solid #ccc; border-radius: 8px; box-sizing: border-box; }
    button { padding: 0.6rem 1rem; border: 1px solid #111; border-radius: 8px; background: #111; color: #fff; cursor: pointer; }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <p>${message}</p>
  ${showTicket ? '<p class="hint">Copy this connection code, paste it into Design Buddy, then click Finish Notion sign-in.</p><textarea id="ticket" readonly></textarea><button type="button" id="copy-btn">Copy connection code</button><p id="copy-hint" class="hint"></p>' : '<p id="copy-hint" class="hint"></p>'}
  <script>
    (function () {
      var payload = ${safePayload};
      if (window.opener) {
        window.opener.postMessage(payload, '*');
      }
      if (payload && payload.ok && payload.ticket) {
        var ticketEl = document.getElementById('ticket');
        var copyBtn = document.getElementById('copy-btn');
        var hint = document.getElementById('copy-hint');
        if (ticketEl) ticketEl.value = payload.ticket;
        function copyTicket() {
          if (!payload.ticket) return;
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(payload.ticket).then(function () {
              if (hint) hint.textContent = 'Copied. Return to Figma, paste into Design Buddy, and click Finish Notion sign-in.';
            }).catch(fallbackCopy);
          } else {
            fallbackCopy();
          }
        }
        function fallbackCopy() {
          if (!ticketEl) return;
          ticketEl.focus();
          ticketEl.select();
          try {
            document.execCommand('copy');
            if (hint) hint.textContent = 'Copied. Return to Figma, paste into Design Buddy, and click Finish Notion sign-in.';
          } catch (e) {
            if (hint) hint.textContent = 'Select the code above, copy it manually, then paste into Design Buddy.';
          }
        }
        if (copyBtn) copyBtn.addEventListener('click', copyTicket);
        copyTicket();
      }
    })();
  </script>
</body>
</html>`;
}

async function exchangeCode(code, redirectUri) {
  const clientId = process.env.NOTION_CLIENT_ID;
  const clientSecret = process.env.NOTION_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    throw new Error('Server missing Notion OAuth client credentials.');
  }

  const basic = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
  const res = await fetch(NOTION_TOKEN_URL, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${basic}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      grant_type: 'authorization_code',
      code,
      redirect_uri: redirectUri,
    }),
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.error || data?.message || 'Notion token exchange failed.');
  }
  return data;
}

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).send('Method not allowed');
  }

  const code = sanitizeText(req.query?.code);
  const state = sanitizeText(req.query?.state);
  const error = sanitizeText(req.query?.error);

  if (error) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(400).send(
      htmlPage(
        'Notion connection failed',
        'Authorization was denied or interrupted. Close this tab and try again in Design Buddy.',
        { type: 'design-buddy-notion-oauth', ok: false, error }
      )
    );
  }

  if (!hasValue(code) || !hasValue(state)) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(400).send(
      htmlPage(
        'Notion connection failed',
        'Missing authorization code. Close this tab and try again in Design Buddy.',
        { type: 'design-buddy-notion-oauth', ok: false, error: 'missing_code' }
      )
    );
  }

  const redirectUri = process.env.NOTION_REDIRECT_URI || '';
  if (!redirectUri) {
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(500).send(
      htmlPage(
        'Notion connection failed',
        'Server is not configured for Notion OAuth. Close this tab and contact the plugin author.',
        { type: 'design-buddy-notion-oauth', ok: false, error: 'server_config' }
      )
    );
  }

  try {
    const tokenData = await exchangeCode(code, redirectUri);
    const accessToken = sanitizeText(tokenData.access_token);
    if (!accessToken) {
      throw new Error('Notion did not return an access token.');
    }

    const workspaceName = sanitizeText(tokenData.workspace_name, 'Notion workspace');
    const workspaceId = sanitizeText(tokenData.workspace_id);

    setPendingOAuth(state, {
      accessToken,
      workspaceName,
      workspaceId,
    });

    const ticket = createOAuthTicket({
      state,
      accessToken,
      workspaceName,
      workspaceId,
    });

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(200).send(
      htmlPage(
        'Connected to Notion',
        'You can close this tab and return to Design Buddy.',
        {
          type: 'design-buddy-notion-oauth',
          ok: true,
          state,
          ticket,
          workspaceName,
          workspaceId,
        }
      )
    );
  } catch (err) {
    const message =
      err && typeof err.message === 'string' ? err.message : 'Notion authorization failed.';
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(500).send(
      htmlPage(
        'Notion connection failed',
        message + ' Close this tab and try again in Design Buddy.',
        { type: 'design-buddy-notion-oauth', ok: false, error: message }
      )
    );
  }
}
