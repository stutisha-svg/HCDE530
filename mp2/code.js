figma.showUI(__html__, { width: 360, height: 480, title: "Design Buddy" });

figma.on('selectionchange', async () => {
  const node = figma.currentPage.selection[0];
  if (!node) {
    figma.ui.postMessage({ type: 'selection-cleared' });
    return;
  }
  try {
    const bytes = await node.exportAsync({ format: 'PNG', constraint: { type: 'SCALE', value: 1 } });
    const base64 = figma.base64Encode(bytes);
    figma.ui.postMessage({
      type: 'selection',
      data: {
        name: node.name,
        type: node.type,
        image: base64
      }
    });
  } catch (e) {
    figma.ui.postMessage({
      type: 'selection',
      data: { name: node.name, type: node.type, image: null }
    });
  }
});
