import {
  setCors,
  parseBody,
  sanitizeText,
  hasValue,
  NOTION_API,
  jsonHeaders,
} from './_notion-shared.js';

const MAX_PAGES = 50;

function pageTitle(page) {
  const props = page?.properties || {};
  const titleProp = props.title || props.Name || props.name;
  if (!titleProp || !Array.isArray(titleProp.title)) return 'Untitled';
  return (
    titleProp.title
      .map((part) => part?.plain_text || '')
      .join('')
      .trim() || 'Untitled'
  );
}

async function searchPages(accessToken) {
  const pages = [];
  let cursor = undefined;

  while (pages.length < MAX_PAGES) {
    const body = {
      filter: { property: 'object', value: 'page' },
      page_size: Math.min(25, MAX_PAGES - pages.length),
      sort: { direction: 'descending', timestamp: 'last_edited_time' },
    };
    if (cursor) body.start_cursor = cursor;

    const res = await fetch(`${NOTION_API}/search`, {
      method: 'POST',
      headers: jsonHeaders(accessToken),
      body: JSON.stringify(body),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const message = data?.message || 'Failed to search Notion pages.';
      const err = new Error(message);
      err.status = res.status;
      throw err;
    }

    const results = Array.isArray(data.results) ? data.results : [];
    results.forEach((page) => {
      if (page?.object !== 'page' || !page.id) return;
      pages.push({
        id: page.id,
        title: pageTitle(page),
        url: page.url || '',
      });
    });

    if (!data.has_more || !data.next_cursor) break;
    cursor = data.next_cursor;
  }

  return pages;
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
    const accessToken = sanitizeText(body.accessToken || body.notionToken);

    if (!hasValue(accessToken)) {
      return res.status(401).json({ error: 'Notion access token required.' });
    }

    const pages = await searchPages(accessToken);
    return res.status(200).json({ pages });
  } catch (error) {
    const message =
      error && typeof error.message === 'string' ? error.message : 'Server error';
    const status = error?.status === 401 ? 401 : 500;
    return res.status(status).json({ error: message });
  }
}
