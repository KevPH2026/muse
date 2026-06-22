// Muse · Catch — Content Script
// 获取页面选中文字

// Listen for selection requests from popup
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'GET_SELECTED_TEXT') {
    const text = window.getSelection()?.toString()?.trim() || '';
    sendResponse({ text });
  }
  return true;
});

// Track selection changes (store for popup)
let lastSelection = '';
document.addEventListener('selectionchange', () => {
  const text = window.getSelection()?.toString()?.trim() || '';
  lastSelection = text;
  // Store in session so popup can get it
  try {
    sessionStorage.setItem('muse_selected_text', text.slice(0, 5000));
  } catch (_) {}
});
