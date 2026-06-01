const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const prompts = JSON.parse(fs.readFileSync(path.join(root, 'prompts.json'), 'utf8'));

const code = `figma.showUI(__html__, { width: 360, height: 480, title: "Design Buddy" });

const PROMPTS_DATA = ${JSON.stringify(prompts)};
const REFLECTIONS_KEY = "reflections";

async function loadReflections() {
  const data = await figma.clientStorage.getAsync(REFLECTIONS_KEY);
  return Array.isArray(data) ? data : [];
}

async function saveReflections(reflections) {
  await figma.clientStorage.setAsync(REFLECTIONS_KEY, reflections);
}

async function postReflectionsToUI() {
  const data = await loadReflections();
  figma.ui.postMessage({ type: "reflections-loaded", data });
}

figma.ui.postMessage({ type: "prompts-loaded", data: PROMPTS_DATA });
postReflectionsToUI();

figma.ui.onmessage = async (msg) => {
  if (msg.type === "get-prompts") {
    figma.ui.postMessage({ type: "prompts-loaded", data: PROMPTS_DATA });
  }

  if (msg.type === "get-reflections") {
    await postReflectionsToUI();
  }

  if (msg.type === "save-reflection") {
    const entry = msg.data;
    if (!entry) return;
    const existing = await loadReflections();
    existing.unshift(entry);
    await saveReflections(existing);
    figma.ui.postMessage({ type: "reflections-loaded", data: existing });
    figma.ui.postMessage({ type: "save-success" });
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
