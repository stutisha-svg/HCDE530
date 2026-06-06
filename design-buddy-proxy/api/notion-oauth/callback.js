import { hasValue, sanitizeText } from '../_notion-shared.js';

const NOTION_TOKEN_URL = 'https://api.notion.com/v1/oauth/token';

function htmlPage(title, message, payload) {
  const safePayload = JSON.stringify(payload).replace(/</g, '\\u003c');
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>${title}</title>
  <style>
    body { font-family: system-ui, sans-serif; padding: 2rem; max-width: 28rem; margin: 0 auto; color: #1a1a1a; }
    p { line-height: 1.5; }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <p>${message}</p>
  <script>
    (function () {
      var payload = ${safePayload};
      if (window.opener) {
        window.opener.postMessage(payload, '*');
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

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return res.status(200).send(
      htmlPage(
        'Connected to Notion',
        'You can close this tab and return to Design Buddy.',
        {
          type: 'design-buddy-notion-oauth',
          ok: true,
          state,
          accessToken,
          workspaceName: sanitizeText(tokenData.workspace_name, 'Notion workspace'),
          workspaceId: sanitizeText(tokenData.workspace_id),
          botId: sanitizeText(tokenData.bot_id),
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
