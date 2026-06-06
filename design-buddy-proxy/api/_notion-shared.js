export const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export const NOTION_VERSION = '2022-06-28';
export const NOTION_API = 'https://api.notion.com/v1';

export function setCors(res) {
  Object.entries(CORS_HEADERS).forEach(([key, value]) => res.setHeader(key, value));
}

export function hasValue(value) {
  return value !== undefined && value !== null && String(value).trim() !== '';
}

export function parseBody(req) {
  if (!req || req.body === undefined || req.body === null) return {};
  if (typeof req.body === 'object' && !Buffer.isBuffer(req.body)) return req.body;
  if (Buffer.isBuffer(req.body)) {
    try {
      return JSON.parse(req.body.toString('utf8'));
    } catch {
      return {};
    }
  }
  if (typeof req.body === 'string') {
    try {
      return JSON.parse(req.body);
    } catch {
      return {};
    }
  }
  return {};
}

export function sanitizeText(value, fallback = '') {
  if (!hasValue(value)) return fallback;
  return String(value).trim();
}

export function jsonHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    'Notion-Version': NOTION_VERSION,
    'Content-Type': 'application/json',
  };
}
