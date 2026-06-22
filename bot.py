#!/usr/bin/env python3
"""Muse Telegram Bot — forward any message to capture inspiration."""
import requests
import os
import sys
import time
import json

TOKEN = os.environ.get("MUSE_BOT_TOKEN", "")
API = os.environ.get("MUSE_API_URL", "http://localhost:5200/api/ingest")
LAST_UPDATE_FILE = os.path.join(os.path.dirname(__file__), ".bot_offset")

def load_offset():
    try:
        with open(LAST_UPDATE_FILE) as f:
            return int(f.read().strip())
    except:
        return 0

def save_offset(offset):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(str(offset))

def handle_message(msg):
    """Extract content from any Telegram message and send to Muse API."""
    text = (msg.get("text") or msg.get("caption") or "").strip()
    chat_id = msg["chat"]["id"]

    if not text:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": "📭 没有文字内容可以捕获。试试发送或转发带文字的链接/文章？"
        })
        return

    payload = {
        "source": "telegram",
        "content": text,
        "url": "",
        "title": "",
        "note": f"Telegram: {msg['chat'].get('first_name', '')} {msg['chat'].get('last_name', '')}".strip(),
        "tags": ["telegram"]
    }

    # Extract URL if present (forwarded messages often have entities)
    entities = msg.get("entities", []) or msg.get("caption_entities", [])
    for e in entities:
        if e.get("type") == "url":
            url = text[e["offset"]:e["offset"]+e["length"]]
            payload["url"] = url
            break

    try:
        resp = requests.post(API, json=payload, timeout=10)
        if resp.ok:
            data = resp.json()
            reply = f"🌀 已捕获！\n\n📌 {data.get('title', '无标题')}\n🔑 {data.get('keywords', '')}"
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": reply
            })
        else:
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"❌ 捕获失败: {resp.text[:200]}"
            })
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"❌ API 连接失败: {e}"
        })

def poll():
    """Long-polling loop."""
    offset = load_offset()
    print(f"🤖 Muse Bot 启动 (offset={offset})")
    print(f"   API: {API}")

    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35
            )
            r.raise_for_status()

            for upd in r.json().get("result", []):
                offset = upd["update_id"] + 1
                if "message" in upd:
                    handle_message(upd["message"])

            save_offset(offset)
        except requests.exceptions.ReadTimeout:
            continue  # Normal timeout on long poll
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ 请设置 MUSE_BOT_TOKEN 环境变量")
        print("   1. Telegram 找 @BotFather → /newbot → 拿到 TOKEN")
        print("   2. export MUSE_BOT_TOKEN='你的TOKEN'")
        print("   3. 重新运行")
        sys.exit(1)
    poll()
