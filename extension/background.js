// Muse · Catch — Background Service Worker
// 右键菜单 + 快捷键 + API 代理

const DEFAULT_API = 'http://localhost:5200/api/ingest';

// ============ INSTALL ============
chrome.runtime.onInstalled.addListener(() => {
  // 右键菜单：捕获页面
  chrome.contextMenus.create({
    id: 'capture-page',
    title: '🌀 捕获到 Muse',
    contexts: ['page']
  });

  // 右键菜单：捕获选中文字
  chrome.contextMenus.create({
    id: 'capture-selection',
    title: '✂️ 捕获选中文字到 Muse',
    contexts: ['selection']
  });
});

// ============ CONTEXT MENU ============
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  let payload = {
    source: 'browser_extension',
    url: tab.url,
    title: tab.title
  };

  if (info.menuItemId === 'capture-page') {
    payload.content = tab.title;
    payload.note = '';
  } else if (info.menuItemId === 'capture-selection') {
    payload.content = info.selectionText;
    payload.note = '';
  }

  await sendToMuse(payload);
});

// ============ KEYBOARD SHORTCUT ============
chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'capture-page') {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return;
    const payload = {
      source: 'browser_shortcut',
      url: tab.url,
      title: tab.title,
      content: tab.title,
      note: ''
    };
    await sendToMuse(payload);
  }
});

// ============ MESSAGE FROM POPUP ============
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'CAPTURE') {
    sendToMuse(msg.payload).then(sendResponse);
    return true; // async
  }
});

// ============ SEND TO MUSE API ============
async function sendToMuse(payload) {
  const stored = await chrome.storage.local.get('apiUrl');
  const apiUrl = stored.apiUrl || DEFAULT_API;

  try {
    const resp = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (resp.ok) {
      const result = await resp.json();
      // Show notification
      chrome.notifications?.create?.({
        type: 'basic',
        iconUrl: 'icon128.png',
        title: '🌀 Muse · 已捕获',
        message: `"${(result.title || payload.title || '').slice(0, 50)}"`,
        priority: 0
      });
      return result;
    } else {
      const err = await resp.text();
      throw new Error(err || `HTTP ${resp.status}`);
    }
  } catch (err) {
    console.error('Muse capture failed:', err);
    chrome.notifications?.create?.({
      type: 'basic',
      iconUrl: 'icon128.png',
      title: 'Muse · 捕获失败',
      message: err.message,
      priority: 2
    });
    throw err;
  }
}
