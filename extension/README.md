# 🌀 Muse · Catch 浏览器插件

> 一键捕获正在浏览的网页到 Muse 灵感库。任何页面，瞬间入库。

---

## 安装（30 秒）

### Chrome / Edge / Brave（Chromium 内核）

1. 打开 `chrome://extensions`
2. 右上角打开「**开发者模式**」
3. 点「**加载已解压的扩展程序**」
4. 选择本目录：`~/.hermes/workspace/muse/extension`
5. 完成 ✅

### 使用

| 操作 | 说明 |
|---|---|
| 🔌 **点击图标** | 弹出捕获面板，自动填入当前页面标题+URL |
| ✂️ **选中文字** | 在页面选中文字后打开插件，自动填入 |
| 💭 **写想法** | 在「我的想法」里写为什么这条值得记 |
| 🏷️ **选标签** | 点一下标签就能选中/取消 |
| ⚡ **Ctrl+Shift+M** | 快捷键直接捕获当前页面 |
| 🖱️ **右键菜单** | 右键任意页面或选中文字 → 「捕获到 Muse」 |

### API 地址配置

默认 `http://localhost:5200/api/ingest`。如果 API 在其他地址，点插件底部 ⚙️ 修改。

---

## 文件清单

```
extension/
  manifest.json    — Chrome 扩展配置（V3）
  popup.html       — 弹出界面
  popup.css        — 深色赛博风格
  popup.js         — 捕获逻辑
  background.js    — 后台服务 + 右键菜单 + 快捷键
  content.js       — 页面选中文字获取
  icon16.png       — 图标
  icon48.png
  icon128.png
```

---

## 技术架构

```
浏览器页面 → [选中文字/页面信息]
                ↓
         Chrome Extension
         (popup / 快捷键 / 右键)
                ↓
         POST /api/ingest
                ↓
         Muse API (Flask)
         llm_extract → LLM 提取标题/摘要/关键词/情绪
                ↓
         SQLite (muse.db)
                ↓
         前端仪表盘 (index.html)
```
