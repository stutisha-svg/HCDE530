const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const prompts = JSON.parse(fs.readFileSync(path.join(root, 'prompts.json'), 'utf8'));

const code = `figma.showUI(__html__, { width: 360, height: 480, title: "Design Buddy" });

const PROMPTS_DATA = ${JSON.stringify(prompts)};
const REFLECTIONS_KEY = "reflections";
const DOCUMENTS_KEY = "documents";

async function loadReflections() {
  const data = await figma.clientStorage.getAsync(REFLECTIONS_KEY);
  return Array.isArray(data) ? data : [];
}

async function loadDocuments() {
  const data = await figma.clientStorage.getAsync(DOCUMENTS_KEY);
  return Array.isArray(data) ? data : [];
}

async function saveReflections(reflections) {
  await figma.clientStorage.setAsync(REFLECTIONS_KEY, reflections);
}

async function saveDocuments(documents) {
  await figma.clientStorage.setAsync(DOCUMENTS_KEY, documents);
}

async function postHistoryToUI() {
  const reflections = await loadReflections();
  const documents = await loadDocuments();
  figma.ui.postMessage({
    type: "reflections-loaded",
    data: reflections,
    documents
  });
}

figma.ui.postMessage({ type: "prompts-loaded", data: PROMPTS_DATA });
postHistoryToUI();

figma.ui.onmessage = async (msg) => {
  if (msg.type === "get-prompts") {
    figma.ui.postMessage({ type: "prompts-loaded", data: PROMPTS_DATA });
  }

  if (msg.type === "get-reflections") {
    await postHistoryToUI();
  }

  if (msg.type === "save-reflection") {
    const entry = msg.data;
    if (!entry) return;
    const existing = await loadReflections();
    existing.unshift(entry);
    await saveReflections(existing);
    await postHistoryToUI();
    figma.ui.postMessage({ type: "save-success" });
  }

  if (msg.type === "delete-reflection") {
    const id = msg.id;
    if (!id) return;
    const existing = await loadReflections();
    const next = existing.filter((r) => r.id !== id);
    await saveReflections(next);
    await postHistoryToUI();
  }

  if (msg.type === "save-compiled-document") {
    const doc = msg.document;
    const reflectionIds = Array.isArray(msg.reflectionIds) ? msg.reflectionIds : [];
    if (!doc || reflectionIds.length === 0) return;
    const existing = await loadReflections();
    const idSet = new Set(reflectionIds);
    const nextReflections = existing.filter((r) => !idSet.has(r.id));
    await saveReflections(nextReflections);
    const docs = await loadDocuments();
    docs.unshift(doc);
    await saveDocuments(docs);
    await postHistoryToUI();
  }

  if (msg.type === "close") {
    figma.closePlugin();
  }
};

figma.on("selectionchange", async () => {
  const node = figma.currentPage.selection[0];
  if (!node) {
    figma.ui.postMessage({ type: "selection-cleared" });
    return;
  }
  try {
    const bytes = await node.exportAsync({ format: "PNG", constraint: { type: "SCALE", value: 1 } });
    const base64 = figma.base64Encode(bytes);
    figma.ui.postMessage({
      type: "selection",
      data: {
        name: node.name,
        type: node.type,
        image: base64
      }
    });
  } catch (e) {
    figma.ui.postMessage({
      type: "selection",
      data: { name: node.name, type: node.type, image: null }
    });
  }
});
`;

fs.writeFileSync(path.join(root, 'code.js'), code);
console.log('Wrote code.js (' + code.length + ' bytes)');
