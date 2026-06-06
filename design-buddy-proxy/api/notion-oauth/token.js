import { setCors, sanitizeText } from '../_notion-shared.js';
import { takePendingOAuth } from './_pending.js';

export default async function handler(req, res) {
  setCors(res);

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const state = sanitizeText(req.query?.state);
  if (!state) {
    return res.status(400).json({ error: 'Missing state' });
  }

  const pending = takePendingOAuth(state);
  if (!pending) {
    return res.status(404).json({ ok: false, error: 'pending' });
  }

  return res.status(200).json({
    ok: true,
    state,
    accessToken: pending.accessToken,
    workspaceName: pending.workspaceName,
    workspaceId: pending.workspaceId,
  });
}
