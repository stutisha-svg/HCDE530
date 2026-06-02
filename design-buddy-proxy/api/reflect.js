const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

const SYSTEM_PROMPT =
  'You are a reflective design coach. Given this designer\'s reflection, generate one follow-up question that pushes their thinking further. Surface a contradiction, an assumption, or an implication they haven\'t named yet. One sentence. Second person. No preamble.';

const ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages';
const MODEL = 'claude-sonnet-4-20250514';

function setCors(res) {
  Object.entries(CORS_HEADERS).forEach(([key, value]) => {
    res.setHeader(key, value);
  });
}

function buildUserMessage(anchor, deck, prompt, lastReflection) {
  const lines = [
    `Anchor: ${anchor}`,
    `Deck: ${deck}`,
    `Prompt: ${prompt}`,
  ];
  if (lastReflection && String(lastReflection).trim()) {
    lines.push(`Earlier reflection excerpt: ${lastReflection}`);
  }
  return lines.join('\n');
}

function hasValue(value) {
  return value !== undefined && value !== null && String(value).trim() !== '';
}

function parseBody(req) {
  if (!req || req.body === undefined || req.body === null) return {};

  if (typeof req.body === 'string') {
    try {
      return JSON.parse(req.body);
    } catch {
      return {};
    }
  }

  if (Buffer.isBuffer(req.body)) {
    try {
      return JSON.parse(req.body.toString('utf8'));
    } catch {
      return {};
    }
  }

  if (typeof req.body === 'object') {
    return req.body;
  }

  return {};
}

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
    const { anchor, deck, prompt, lastReflection } = body;

    if (!hasValue(anchor) || !hasValue(deck) || !hasValue(prompt)) {
      return res.status(400).json({ error: 'Missing fields' });
    }

    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) {
      return res.status(500).json({ error: 'Server error' });
    }

    const userMessage = buildUserMessage(
      anchor,
      deck,
      prompt,
      lastReflection ?? ''
    );

    const upstream = await fetch(ANTHROPIC_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 150,
        system: SYSTEM_PROMPT,
        messages: [{ role: 'user', content: userMessage }],
      }),
    });

    if (!upstream.ok) {
      console.error('Anthropic upstream status', upstream.status);
      return res.status(502).json({ error: 'Upstream error' });
    }

    const data = await upstream.json();
    const text = data?.content?.[0]?.text;

    if (!text || typeof text !== 'string') {
      return res.status(502).json({ error: 'Upstream error' });
    }

    return res.status(200).json({ question: text.trim() });
  } catch (error) {
    console.error('Reflect handler error:', error);
    return res.status(500).json({ error: 'Server error' });
  }
}
