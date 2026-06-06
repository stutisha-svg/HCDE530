import { setCors, parseBody, sanitizeText } from '../_notion-shared.js';
import { verifyOAuthTicket } from './_ticket.js';

export default async function handler(req, res) {
  setCors(res);

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const body = parseBody(req);
    const ticket = sanitizeText(body.ticket);
    const state = sanitizeText(body.state);

    if (!ticket) {
      return res.status(400).json({ error: 'Missing connection ticket.' });
    }

    const data = verifyOAuthTicket(ticket, state || undefined);
    if (!data) {
      return res.status(401).json({
        error: 'Invalid or expired Notion connection. Sign in again.',
      });
    }

    return res.status(200).json({
      ok: true,
      state: data.state,
      accessToken: data.accessToken,
      workspaceName: data.workspaceName,
      workspaceId: data.workspaceId,
    });
  } catch (error) {
    const message =
      error && typeof error.message === 'string' ? error.message : 'Server error';
    return res.status(500).json({ error: message });
  }
}
