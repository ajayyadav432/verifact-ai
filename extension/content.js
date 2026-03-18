// content.js — Injected into every page.
// Listens for a message from popup.js and responds with the
// user's currently selected text (or a trimmed snippet of body text).

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getSelectedText") {
    const selected = window.getSelection()?.toString().trim();

    if (selected && selected.length > 0) {
      sendResponse({ text: selected, source: "selection" });
    } else {
      // Fallback: grab visible body text (first 2000 chars)
      const bodyText = (document.body.innerText || "").trim().slice(0, 2000);
      sendResponse({ text: bodyText, source: "page" });
    }
  }
  // Return true to keep the message channel open for async sendResponse
  return true;
});
