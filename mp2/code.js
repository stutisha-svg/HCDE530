figma.showUI(__html__, { width: 360, height: 480, title: "Design Buddy" });

figma.ui.onmessage = (msg) => {
  if (msg.type === 'close') {
    figma.closePlugin();
  }
};
