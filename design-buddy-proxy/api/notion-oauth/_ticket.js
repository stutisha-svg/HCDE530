import crypto from 'crypto';

const TTL_MS = 10 * 60 * 1000;

function base64UrlEncode(value) {
  return Buffer.from(value).toString('base64url');
}

function base64UrlDecode(value) {
  return Buffer.from(value, 'base64url');
}

function signingSecret() {
  return process.env.NOTION_CLIENT_SECRET || process.env.NOTION_OAUTH_TICKET_SECRET || '';
}

export function createOAuthTicket(payload) {
  const secret = signingSecret();
  if (!secret) {
    throw new Error('Server missing Notion OAuth ticket secret.');
  }

  const body = {
    state: payload.state,
    accessToken: payload.accessToken,
    workspaceName: payload.workspaceName || '',
    workspaceId: payload.workspaceId || '',
    exp: Date.now() + TTL_MS,
  };

  const encoded = base64UrlEncode(JSON.stringify(body));
  const signature = crypto.createHmac('sha256', secret).update(encoded).digest('base64url');
  return `${encoded}.${signature}`;
}

export function verifyOAuthTicket(ticket, expectedState) {
  const secret = signingSecret();
  if (!secret || !ticket || typeof ticket !== 'string') {
    return null;
  }

  const parts = ticket.split('.');
  if (parts.length !== 2) return null;

  const [encoded, signature] = parts;
  const expectedSig = crypto.createHmac('sha256', secret).update(encoded).digest('base64url');
  const sigBuffer = base64UrlDecode(signature);
  const expectedBuffer = base64UrlDecode(expectedSig);
  if (
    sigBuffer.length !== expectedBuffer.length ||
    !crypto.timingSafeEqual(sigBuffer, expectedBuffer)
  ) {
    return null;
  }

  let body;
  try {
    body = JSON.parse(base64UrlDecode(encoded).toString('utf8'));
  } catch {
    return null;
  }

  if (!body || typeof body !== 'object') return null;
  if (!body.accessToken || !body.state) return null;
  if (expectedState && body.state !== expectedState) return null;
  if (!body.exp || body.exp < Date.now()) return null;

  return {
    state: body.state,
    accessToken: body.accessToken,
    workspaceName: body.workspaceName || '',
    workspaceId: body.workspaceId || '',
  };
}
