import { setCors } from '../_notion-shared.js';

export default async function handler(req, res) {
  setCors(res);

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const clientId = process.env.NOTION_CLIENT_ID || '';
  const redirectUri = process.env.NOTION_REDIRECT_URI || '';

  if (!clientId || !redirectUri) {
    return res.status(500).json({
      error: 'Server missing Notion OAuth configuration. Set NOTION_CLIENT_ID and NOTION_REDIRECT_URI.',
    });
  }

  return res.status(200).json({ clientId, redirectUri });
}
