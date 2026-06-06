/**
 * Static verification for Notion OAuth export (no live OAuth).
 * Run: node scripts/verify-notion-auth.js
 */

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const exportSrc = readFileSync(join(root, 'api', 'notion-export.js'), 'utf8');

const checks = [
  {
    name: 'No server NOTION_INTEGRATION_TOKEN fallback',
    pass: !exportSrc.includes('NOTION_INTEGRATION_TOKEN'),
  },
  {
    name: 'No server NOTION_PARENT_PAGE_ID fallback',
    pass: !exportSrc.includes('NOTION_PARENT_PAGE_ID'),
  },
  {
    name: 'Requires accessToken from request body',
    pass: /body\.accessToken\s*\|\|\s*body\.notionToken/.test(exportSrc),
  },
  {
    name: 'Requires parentPageId from request body',
    pass: exportSrc.includes('body.parentPageId'),
  },
  {
    name: 'Returns 401 when token missing',
    pass: /status\(401\)/.test(exportSrc) && exportSrc.includes('Connect Notion'),
  },
];

let failed = 0;
checks.forEach((c) => {
  const status = c.pass ? 'PASS' : 'FAIL';
  console.log(`${status}: ${c.name}`);
  if (!c.pass) failed += 1;
});

if (failed) {
  process.exit(1);
}
console.log('\nAll static checks passed.');
