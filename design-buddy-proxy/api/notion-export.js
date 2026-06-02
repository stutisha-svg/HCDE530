const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

const NOTION_VERSION = '2022-06-28';
const NOTION_API = 'https://api.notion.com/v1';
const MAX_REFLECTIONS = 30;

function setCors(res) {
  Object.entries(CORS_HEADERS).forEach(([key, value]) => res.setHeader(key, value));
}

function hasValue(value) {
  return value !== undefined && value !== null && String(value).trim() !== '';
}

function parseBody(req) {
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

function sanitizeText(value, fallback = '') {
  if (!hasValue(value)) return fallback;
  return String(value).trim();
}

function chunkBy(items, size) {
  const chunks = [];
  for (let i = 0; i < items.length; i += size) {
    chunks.push(items.slice(i, i + size));
  }
  return chunks;
}

function jsonHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    'Notion-Version': NOTION_VERSION,
    'Content-Type': 'application/json',
  };
}

async function createFileUpload(notionToken, filename) {
  const res = await fetch(`${NOTION_API}/file_uploads`, {
    method: 'POST',
    headers: jsonHeaders(notionToken),
    body: JSON.stringify({
      mode: 'single_part',
      filename,
      content_type: 'image/png',
    }),
  });
  if (!res.ok) {
    throw new Error('Failed to create Notion file upload.');
  }
  const data = await res.json();
  if (!data || !data.id) {
    throw new Error('Notion file upload response missing id.');
  }
  return data.id;
}

async function sendFileUpload(notionToken, fileUploadId, binary, filename) {
  const form = new FormData();
  const blob = new Blob([binary], { type: 'image/png' });
  form.append('file', blob, filename);

  const res = await fetch(`${NOTION_API}/file_uploads/${fileUploadId}/send`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${notionToken}`,
      'Notion-Version': NOTION_VERSION,
    },
    body: form,
  });

  if (!res.ok) {
    throw new Error('Failed to upload image bytes to Notion.');
  }
}

async function uploadAnchorImageToNotion(notionToken, base64Image, reflectionId) {
  const raw = sanitizeText(base64Image);
  if (!raw) return null;

  let binary;
  try {
    binary = Buffer.from(raw, 'base64');
  } catch {
    return null;
  }

  if (!binary || !binary.length) return null;
  const fileUploadId = await createFileUpload(
    notionToken,
    `design-buddy-anchor-${reflectionId || Date.now()}.png`
  );
  await sendFileUpload(
    notionToken,
    fileUploadId,
    binary,
    `design-buddy-anchor-${reflectionId || Date.now()}.png`
  );
  return fileUploadId;
}

function paragraphBlock(text) {
  return {
    object: 'block',
    type: 'paragraph',
    paragraph: {
      rich_text: [{ type: 'text', text: { content: text || '' } }],
    },
  };
}

function headingBlock(text) {
  return {
    object: 'block',
    type: 'heading_3',
    heading_3: {
      rich_text: [{ type: 'text', text: { content: text || '' } }],
    },
  };
}

function dividerBlock() {
  return { object: 'block', type: 'divider', divider: {} };
}

function imageBlock(fileUploadId, caption) {
  return {
    object: 'block',
    type: 'image',
    image: {
      type: 'file_upload',
      caption: caption
        ? [{ type: 'text', text: { content: caption } }]
        : [],
      file_upload: { id: fileUploadId },
    },
  };
}

async function appendBlocks(notionToken, pageId, blocks) {
  const chunks = chunkBy(blocks, 90);
  for (const children of chunks) {
    const res = await fetch(`${NOTION_API}/blocks/${pageId}/children`, {
      method: 'PATCH',
      headers: jsonHeaders(notionToken),
      body: JSON.stringify({ children }),
    });
    if (!res.ok) {
      throw new Error('Failed to append blocks to Notion page.');
    }
  }
}

async function createNotionPage(notionToken, parentPageId, title, intro) {
  const res = await fetch(`${NOTION_API}/pages`, {
    method: 'POST',
    headers: jsonHeaders(notionToken),
    body: JSON.stringify({
      parent: { page_id: parentPageId },
      properties: {
        title: {
          title: [{ type: 'text', text: { content: title } }],
        },
      },
      children: [paragraphBlock(intro)],
    }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => null);
    if (res.status === 401) {
      throw new Error('Notion authorization failed. Check your integration token.');
    }
    throw new Error(data?.message || 'Failed to create Notion page.');
  }

  const data = await res.json();
  if (!data || !data.id) {
    throw new Error('Notion page creation returned no page id.');
  }
  return { id: data.id, url: data.url };
}

async function buildReflectionBlocks(notionToken, reflection, index) {
  const anchorValue = sanitizeText(reflection?.anchor?.value, 'Untitled anchor');
  const prompt = sanitizeText(reflection?.prompt);
  const response = sanitizeText(reflection?.response);
  const deck = sanitizeText(reflection?.deck, 'unknown');
  const date = sanitizeText(reflection?.date, new Date().toISOString().slice(0, 10));
  const helper = sanitizeText(reflection?.helperText);

  const blocks = [
    headingBlock(`${index + 1}. ${date} - ${anchorValue}`),
    paragraphBlock(`Deck: ${deck}`),
    paragraphBlock(`Prompt: ${prompt || '(none)'}`),
  ];

  const imageBase64 = sanitizeText(reflection?.anchorImage);
  if (imageBase64) {
    try {
      const fileUploadId = await uploadAnchorImageToNotion(
        notionToken,
        imageBase64,
        reflection?.id || String(index + 1)
      );
      if (fileUploadId) {
        blocks.push(imageBlock(fileUploadId, anchorValue));
      }
    } catch (error) {
      console.error('Anchor image upload failed:', error);
      blocks.push(paragraphBlock('Frame image upload failed for this reflection.'));
    }
  }

  if (helper) {
    blocks.push(paragraphBlock(`Context: ${helper}`));
  }
  blocks.push(paragraphBlock(response || '(empty reflection)'));
  blocks.push(dividerBlock());
  return blocks;
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
    const notionToken = sanitizeText(body.notionToken);
    const parentPageId = sanitizeText(body.parentPageId);
    const document = body.document || {};
    const documentName = sanitizeText(document.name, 'Design Buddy Document');
    const reflections = Array.isArray(document.reflections)
      ? document.reflections.slice(0, MAX_REFLECTIONS)
      : [];

    if (!hasValue(notionToken) || !hasValue(parentPageId) || !reflections.length) {
      return res.status(400).json({ error: 'Missing fields' });
    }

    const now = new Date().toISOString().slice(0, 10);
    const title = `${documentName} - ${now}`;
    const intro = `Exported from Design Buddy on ${now}.`;
    const page = await createNotionPage(notionToken, parentPageId, title, intro);

    const blocks = [];
    for (let i = 0; i < reflections.length; i += 1) {
      const reflectionBlocks = await buildReflectionBlocks(notionToken, reflections[i], i);
      blocks.push(...reflectionBlocks);
    }

    if (blocks.length) {
      await appendBlocks(notionToken, page.id, blocks);
    }

    return res.status(200).json({
      ok: true,
      pageId: page.id,
      pageUrl: page.url,
      exportedCount: reflections.length,
    });
  } catch (error) {
    console.error('Notion export failed:', error);
    const message =
      error && typeof error.message === 'string' && error.message
        ? error.message
        : 'Server error';
    const isAuth = message.toLowerCase().includes('authorization');
    return res.status(isAuth ? 401 : 500).json({ error: message });
  }
}
