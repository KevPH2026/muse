// Muse · Catch — Popup Logic
// 捕获当前浏览页面到 Muse 灵感库

const DEFAULT_API = 'http://localhost:5200/api/ingest';

let currentTab = null;
let selectedTags = [];

// ============ INIT ============
document.addEventListener('DOMContentLoaded', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTab = tab;

  // Fill page info
  document.getElementById('page-title').textContent = tab.title || '(无标题)';
  document.getElementById('page-url').textContent = tab.url || '';

  // Get selected text from content script
  try {
    const resp = await chrome.tabs.sendMessage(tab.id, { type: 'GET_SELECTED_TEXT' });
    if (resp && resp.text) {
      document.getElementById('selected-text').value = resp.text;
    }
  } catch (e) {
    // Content script may not be injected yet → inject it
    try {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });
      const resp = await chrome.tabs.sendMessage(tab.id, { type: 'GET_SELECTED_TEXT' });
      if (resp && resp.text) {
        document.getElementById('selected-text').value = resp.text;
      }
    } catch (_) {}
  }

  // Load settings
  const stored = await chrome.storage.local.get('apiUrl');
  document.getElementById('api-url').value = stored.apiUrl || DEFAULT_API;

  // Bind events
  bindEvents();
});

// ============ EVENTS ============
function bindEvents() {
  // Tag selection
  document.getElementById('quick-tags').addEventListener('click', (e) => {
    const tag = e.target.closest('.tag');
    if (!tag) return;
    const tagName = tag.dataset.tag;
    if (selectedTags.includes(tagName)) {
      selectedTags = selectedTags.filter(t => t !== tagName);
      tag.classList.remove('active');
    } else {
      selectedTags.push(tagName);
      tag.classList.add('active');
    }
  });

  // Capture button
  document.getElementById('capture-btn').addEventListener('click', capture);

  // Settings toggle
  document.getElementById('settings-btn').addEventListener('click', () => {
    const panel = document.getElementById('settings-panel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
  });

  // Save settings
  document.getElementById('save-settings').addEventListener('click', async () => {
    const url = document.getElementById('api-url').value.trim();
    await chrome.storage.local.set({ apiUrl: url });
    showStatus('✅ API 地址已保存', 'success');
    document.getElementById('settings-panel').style.display = 'none';
  });

  // Keyboard shortcut
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      capture();
    }
  });
}

// ============ CAPTURE ============
async function capture() {
  const btn = document.getElementById('capture-btn');
  const status = document.getElementById('status');

  if (btn.classList.contains('loading')) return;

  btn.classList.add('loading');
  btn.innerHTML = '<span class="btn-icon">⏳</span> 捕获中…';
  status.textContent = '';

  const selectedText = document.getElementById('selected-text').value.trim();
  const userNote = document.getElementById('user-note').value.trim();

  const payload = {
    source: 'browser_extension',
    url: currentTab.url,
    title: currentTab.title,
    content: selectedText || userNote || '',
    note: userNote,
    tags: selectedTags
  };

  try {
    const stored = await chrome.storage.local.get('apiUrl');
    const apiUrl = stored.apiUrl || DEFAULT_API;

    const resp = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(err || `HTTP ${resp.status}`);
    }

    const result = await resp.json();
    showStatus(`🌀 已捕获！"${(result.title || selectedText || currentTab.title).slice(0, 30)}"`, 'success');

    // Clear form
    document.getElementById('selected-text').value = '';
    document.getElementById('user-note').value = '';
    selectedTags = [];
    document.querySelectorAll('.tag.active').forEach(t => t.classList.remove('active'));

    // Auto-close after 2s
    setTimeout(() => window.close(), 2000);
  } catch (err) {
    showStatus(`❌ 失败: ${err.message}`, 'error');
  } finally {
    btn.classList.remove('loading');
    btn.innerHTML = '<span class="btn-icon">⚡</span> 捕获灵感';
  }
}

function showStatus(msg, type) {
  const el = document.getElementById('status');
  el.textContent = msg;
  el.className = 'status ' + (type || '');
  if (type === 'success') {
    setTimeout(() => { el.textContent = ''; el.className = 'status'; }, 3000);
  }
}
