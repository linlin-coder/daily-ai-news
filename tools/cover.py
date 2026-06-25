#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""使用 AI 生成微信公众号封面图（通过 Pollinations API）

封面必须与当天文章内容强相关，从 md 正文中提取核心主题生成 prompt。
"""

import os
import re
import hashlib
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.parse import quote


# 主题 → 视觉元素映射表
VISUAL_MAP = {
    # AI 产品/模型
    "gemini": "Google Gemini holographic AI interface",
    "gpt": "OpenAI GPT neural glowing orb",
    "claude": "Anthropic Claude AI mind visualization",
    "chatgpt": "ChatGPT conversation hologram",
    "llm": "massive language model brain neural network",
    "大模型": "massive language model brain neural network",
    "语言模型": "massive language model brain neural network",

    # AI Agent / 自动化
    "agent": "autonomous AI agent robot city hologram",
    "自动化": "digital automation workflow robot arms",

    # 隐私/安全
    "隐私": "digital privacy eye surveillance data breach",
    "安全": "cybersecurity shield digital threat warning",
    "监控": "surveillance camera digital eye data stream",
    "数据泄露": "data breach flowing numbers red alert",

    # 欺诈/滥用
    "欺诈": "digital fraud fake identity dark web scam",
    "诈骗": "scam call center dark digital crime",
    "深度伪造": "deepfake face morphing digital distortion",
    "deepfake": "deepfake face morphing digital distortion",
    "假": "fake vs real digital comparison split",

    # 医疗/生物
    "医疗": "medical AI doctor hologram futuristic scan",
    "药物": "molecular drug discovery glowing capsule lab",
    "蛋白质": "protein folding 3D structure biology",
    "基因": "DNA double helix genome sequencing light",
    "生物": "biotech molecular biology lab futuristic",
    "健康": "healthcare AI wearable digital heartbeat",

    # 芯片/硬件
    "芯片": "glowing semiconductor chip neon circuits",
    "gpu": "GPU server room neon glow computing",
    "算力": "supercomputing data center power glow",

    # 开源
    "开源": "open source code terminal developer matrix",
    "github": "GitHub code repository developer workspace",

    # 机器人
    "机器人": "humanoid robot chrome metallic future city",
    "具身": "embodied AI robot physical world interaction",

    # 自动驾驶
    "自动驾驶": "self-driving car AI sensor fusion city",
    "无人": "drone autonomous delivery urban sky",

    # 伦理/社会
    "伦理": "AI ethics balance scale philosophy mind",
    "偏见": "AI bias fairness balance digital scales",
    "就业": "human robot workplace future office",
    "教育": "AI education classroom futuristic learning",

    # 投资/商业
    "融资": "startup funding rocket growth chart",
    "市值": "stock market chart AI company growth",
    "裁员": "layoff office empty desk technology crisis",

    # 写作/创作
    "写作": "AI writing pen paper future creative",
    "创作": "digital art creation AI canvas futuristic",
    "图像": "AI image generation pixel art explosion",
    "视频": "AI video generation cinematic reel",
}


def generate_cover(title, subtitle="", output_path="/tmp/cover.png"):
    """用 AI 生成封面图"""
    prompt = build_prompt(title, subtitle)
    seed = int(hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:8], 16) % 100000

    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=900&height=383&seed={seed}&nologo=true"

    print(f"[cover] Generating: {prompt[:100]}...")

    req = Request(url, headers={"User-Agent": "DailyAINews/1.0"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read()

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"[cover] Saved: {output_path} ({len(data)} bytes)")
    return output_path


def generate_cover_from_md(md_content, output_path="/tmp/cover.png"):
    """从当天的 markdown 报告中提取核心主题生成封面

    优先取第一条热点的关键词，因为那通常是当天最重要的新闻。
    """
    topics = extract_topics_from_md(md_content)
    prompt = build_prompt_from_topics(topics)
    seed = int(hashlib.md5(md_content[:200].encode()).hexdigest()[:8], 16) % 100000

    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=900&height=383&seed={seed}&nologo=true"

    print(f"[cover] Topics: {topics}")
    print(f"[cover] Generating: {prompt[:100]}...")

    req = Request(url, headers={"User-Agent": "DailyAINews/1.0"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read()

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"[cover] Saved: {output_path} ({len(data)} bytes)")
    return output_path


def extract_topics_from_md(md_content):
    """从 markdown 报告中提取核心主题关键词

    扫描所有标题和正文，返回最相关的视觉主题。
    """
    text_lower = md_content.lower()
    found = []

    for keyword in VISUAL_MAP:
        if keyword in text_lower:
            found.append(keyword)

    # 去重，保持顺序
    seen = set()
    unique = []
    for k in found:
        if k not in seen:
            seen.add(k)
            unique.append(k)

    return unique[:5]  # 最多5个主题


def build_prompt(title, subtitle):
    """根据标题构建 prompt（向后兼容）"""
    title_lower = (title + " " + subtitle).lower()
    elements = []
    for keyword, visual in VISUAL_MAP.items():
        if keyword in title_lower:
            elements.append(visual)
    if not elements:
        elements = ["artificial intelligence", "futuristic technology"]
    return _compose_prompt(elements[:2])


def build_prompt_from_topics(topics):
    """根据主题列表构建 prompt"""
    elements = []
    for topic in topics:
        if topic in VISUAL_MAP:
            elements.append(VISUAL_MAP[topic])
    if not elements:
        elements = ["artificial intelligence", "futuristic technology"]
    return _compose_prompt(elements[:2])


def _compose_prompt(elements):
    """组合最终的图片生成 prompt"""
    elements_str = " ".join(elements)
    return (
        f"Eye-catching technology magazine cover illustration, {elements_str}, "
        f"vibrant neon blue and magenta gradient, dramatic cinematic lighting, "
        f"abstract geometric shapes floating, holographic digital effect, "
        f"no text no letters no words no watermark no logo, "
        f"professional 4K ultra detailed, trending on artstation, concept art"
    )


def generate_cover_from_content(content_text, output_path="/tmp/cover.png"):
    """根据文章内容生成封面图（向后兼容）"""
    return generate_cover_from_md(content_text, output_path)


if __name__ == "__main__":
    # 测试：从 md 内容生成
    test_md = """
# 5个AI大厂翻车现场，第3个让程序员集体破防

## 今日AI热点

### 1. Google Gemini AI偷看你的邮箱帮你订机票
Google最新AI Agent Gemini Spark能读取你的Gmail、日历、照片...

### 2. 用户呼吁平台过滤AI垃圾内容
YouTube、Instagram上的AI生成内容泛滥...

### 3. TikTok Shop上AI假人物带货诈骗
深度伪造技术被用于电商欺诈...
"""
    path = generate_cover_from_md(test_md, "/tmp/test_cover.png")
    print(f"Done: {path}")
