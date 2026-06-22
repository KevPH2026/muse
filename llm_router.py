"""
Muse LLM Router — TokenRouter unified gateway
Smart model selection: right model for the right task.

Security note: The API key below is embedded for the Muse Catch skill.
Anyone who installs this skill can use it. The key owner has configured
sufficient quota for public use.
"""
import json, subprocess, base64, os

# ============ CONFIG ============
ROUTER_URL = "https://api.tokenrouter.com/v1"
# Base64-encoded key (not plain text, not in env — embedded for skill portability)
_K = base64.b64decode("c2stMUhuYTFZbmwxSkJsVGlEWDI5TUdZQndqcjdRM3pYcE41SEhsRWQ2YXVmUzJweTYx").decode()
# ================================

# ============ MODEL TIERS ============
# Smart routing: each task type maps to the best model for that job
MODEL_TIERS = {
    # Light tasks: fast, cheap, good enough
    "extract":   "deepseek/deepseek-v3.2",         # 灵感提炼：标题/摘要/关键词
    "classify":  "deepseek/deepseek-v3.2",         # 分类打标
    "summarize": "deepseek/deepseek-v3.2",         # 汇总摘要

    # Medium tasks: balanced
    "dna":       "deepseek/deepseek-v3.2",         # 创作DNA分析
    "topic":     "deepseek/deepseek-v3.2",         # 选题生成
    "deepdive":  "deepseek/deepseek-v3.2",         # 选题深潜（标题变体/结构/金句）

    # Heavy tasks: best quality
    "strategy":  "deepseek/deepseek-v4-pro",       # 内容策略分析
    "research":  "deepseek/deepseek-v3.2",         # 深度调研

    # Image generation
    "image":     "openai/gpt-5-image-mini",        # 金句配图
    "image_hq":  "openai/gpt-5-image",             # 高质量配图

    # Vision / OCR
    "vision":    "z-ai/glm-4.6v",                  # 图片理解
}


def llm_chat(model, messages, max_tokens=1000, temperature=0.4, response_format=None):
    """Call TokenRouter chat completions. Returns content string or None."""
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if response_format:
        body["response_format"] = {"type": "json_object"}

    try:
        r = subprocess.run([
            "curl", "-s", f"{ROUTER_URL}/chat/completions",
            "-H", f"Authorization: Bearer {_K}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(body, ensure_ascii=False)
        ], capture_output=True, text=True, timeout=45)

        if r.returncode != 0 or not r.stdout.strip():
            return None

        resp = json.loads(r.stdout)
        content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip() if content else None
    except Exception as e:
        print(f"LLM error ({model}): {e}")
        return None


def llm_json(model, messages, max_tokens=1500, temperature=0.4):
    """Call LLM and parse JSON from response. Handles markdown code blocks."""
    # Add JSON instruction
    msgs = messages.copy()
    msgs[-1] = {
        "role": msgs[-1]["role"],
        "content": msgs[-1]["content"] + "\n\n⚠️ 返回纯JSON，不要markdown代码块，不要前后多余文字。"
    }

    content = llm_chat(model, msgs, max_tokens, temperature)
    if not content:
        return None

    # Strip markdown code blocks if present
    import re
    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    content = content.strip()

    # Find JSON object/array
    json_match = re.search(r'\{.*\}|\[.*\]', content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    try:
        return json.loads(content)
    except:
        return None


def llm_image(prompt, model=None, size="1024x1024"):
    """Generate image via TokenRouter. Returns URL or base64."""
    model = model or MODEL_TIERS["image"]
    body = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": size,
    }
    try:
        r = subprocess.run([
            "curl", "-s", f"{ROUTER_URL}/images/generations",
            "-H", f"Authorization: Bearer {_K}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(body, ensure_ascii=False)
        ], capture_output=True, text=True, timeout=60)

        if r.returncode != 0 or not r.stdout.strip():
            return None

        resp = json.loads(r.stdout)
        data = resp.get("data", [{}])[0]
        # Return URL if available, else base64
        if data.get("url"):
            return {"url": data["url"]}
        elif data.get("b64_json"):
            return {"b64": data["b64_json"]}
        return None
    except Exception as e:
        print(f"Image gen error ({model}): {e}")
        return None


# ============ HIGH-LEVEL TASK FUNCTIONS ============

def extract_inspiration(raw_text, source="web"):
    """Light: Extract title, summary, keywords, emotion, tags from captured content."""
    result = llm_json(MODEL_TIERS["extract"], [{
        "role": "user",
        "content": f"""分析这段内容，提取灵感信息。返回JSON：
{{
  "title": "标题（≤80字，吸引人）",
  "summary": "摘要（≤150字，核心价值）",
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "emotion": "excited|curious|concerned|inspired|neutral",
  "tags": ["标签1", "标签2"],
  "category": "AI技术|商业洞察|营销策略|产品设计|生活方式|其他"
}}

内容：
{raw_text[:2000]}"""
    }], max_tokens=400, temperature=0.3)

    return result or {
        "title": raw_text[:80],
        "summary": raw_text[:200],
        "keywords": [],
        "emotion": "neutral",
        "tags": [],
        "category": "其他"
    }


def analyze_creation_dna(content_texts, profile=None):
    """Medium: Analyze creator's content to extract DNA."""
    combined = "\n---\n".join(content_texts[:50]) if isinstance(content_texts, list) else str(content_texts)
    combined = combined[:6000]

    profile_hint = ""
    if profile:
        profile_hint = f"\n创作者背景: 领域={profile.get('field','')}, 方向={profile.get('creation_direction','')}, 平台={profile.get('platforms','')}"

    result = llm_json(MODEL_TIERS["dna"], [{
        "role": "user",
        "content": f"""你是顶级内容策略分析师。分析以下创作者的内容，提取"创作DNA"。
{profile_hint}

返回JSON：
{{
  "themes": ["核心主题1", "核心主题2", "核心主题3"],
  "tone": "语调风格描述",
  "formats": ["擅长内容形式1", "形式2"],
  "strengths": ["优势1: 说明", "优势2: 说明", "优势3: 说明"],
  "content_patterns": ["内容规律1", "规律2"],
  "audience_appeal": "受众吸引力分析",
  "recommendations": ["建议1", "建议2", "建议3"],
  "dna_summary": "一句话DNA总结",
  "signature_style": "标志性风格"
}}

创作者内容：
{combined}"""
    }], max_tokens=1200, temperature=0.4)

    return result or {
        "themes": ["待挖掘"], "tone": "待分析", "formats": [],
        "strengths": [], "recommendations": ["提供更多内容以解锁分析"],
        "dna_summary": "初始画像 — 需要更多内容", "signature_style": "待识别"
    }


def generate_topics(signals, dna=None, count=5):
    """Medium: Generate content topics based on captured signals + creator DNA."""
    signals_text = "\n".join([f"- {s.get('title','')}: {s.get('summary','')}" for s in signals[:20]])

    dna_hint = ""
    if dna:
        dna_hint = f"\n创作者DNA: 主题={dna.get('themes',[])}, 风格={dna.get('tone','')}, 优势={dna.get('strengths',[])}"

    result = llm_json(MODEL_TIERS["topic"], [{
        "role": "user",
        "content": f"""基于以下灵感信号，生成{count}个高价值选题。
{dna_hint}

要求：选题要和创作者的擅长方向结合，有传播潜力。

返回JSON：
{{
  "topics": [
    {{
      "title": "选题标题（有钩子感）",
      "angle": "切入角度",
      "hook": "3秒钩子文案",
      "format": "推荐内容形式（短视频/图文/长文）",
      "target_signal": "来源灵感",
      "estimated_virality": "high|medium|low",
      "reason": "为什么这个选题好"
    }}
  ]
}}

灵感信号：
{signals_text}"""
    }], max_tokens=1500, temperature=0.6)

    return result.get("topics", []) if result else []


def deep_dive_topic(topic_title, signals, dna=None):
    """Medium-heavy: Deep dive a topic — headline variants, structure, golden quotes."""
    signals_text = "\n".join([f"- {s.get('title','')}" for s in signals[:10]])

    dna_hint = ""
    if dna:
        dna_hint = f"\n创作者风格: {dna.get('tone','')}, 标志: {dna.get('signature_style','')}"

    result = llm_json(MODEL_TIERS["deepdive"], [{
        "role": "user",
        "content": f"""对选题「{topic_title}」做深度拆解。{dna_hint}

返回JSON：
{{
  "headlines": ["爆款标题变体1", "变体2", "变体3", "变体4", "变体5"],
  "structure": {{
    "hook": "3秒钩子",
    "opening": "开场（前15秒/前3行）",
    "body": ["要点1", "要点2", "要点3"],
    "climax": "高潮/反转",
    "cta": "行动号召"
  }},
  "golden_quotes": ["金句1", "金句2", "金句3", "金句4"],
  "visual_suggestions": ["配图/画面建议1", "建议2", "建议3"],
  "image_prompts": ["AI配图prompt（英文）1", "prompt2", "prompt3"]
}}

相关灵感：
{signals_text}"""
    }], max_tokens=1500, temperature=0.7)

    return result or {}


def cluster_inspirations(inspirations):
    """Light: Cluster inspirations into themes/categories for 汇总."""
    items_text = "\n".join([f"[{i+1}] {insp.get('title','')}: {insp.get('summary','')}" for i, insp in enumerate(inspirations)])

    result = llm_json(MODEL_TIERS["classify"], [{
        "role": "user",
        "content": f"""将这些灵感按主题聚类分组。返回JSON：
{{
  "clusters": [
    {{
      "theme": "主题名",
      "description": "这个主题的核心价值",
      "items": [序号1, 序号2],
      "opportunity": "这个方向的内容机会"
    }}
  ]
}}

灵感列表：
{items_text}"""
    }], max_tokens=800, temperature=0.3)

    return result.get("clusters", []) if result else []


def generate_quote_image(quote, style="modern"):
    """Generate an image for a golden quote / key insight."""
    style_map = {
        "modern": "clean modern minimalist design, bold typography, gradient background, professional",
        "cyber": "cyberpunk neon style, dark background, glowing text, futuristic",
        "warm": "warm cozy aesthetic, soft colors, hand-drawn feel, inviting",
        "bold": "high contrast bold design, striking colors, impactful layout",
    }
    style_prompt = style_map.get(style, style_map["modern"])

    prompt = f"""A social media quote card image. Text on image: "{quote[:50]}"
Style: {style_prompt}
No watermarks, no logos. Square format. High quality."""
    return llm_image(prompt, size="1024x1024")
