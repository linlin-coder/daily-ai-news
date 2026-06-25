#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""使用 AI 生成微信公众号封面图（通过 Pollinations API）"""

import os
import re
import hashlib
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.parse import quote


def generate_cover(title, subtitle="", output_path="/tmp/cover.png"):
    """用 AI 生成封面图"""
    prompt = build_prompt(title, subtitle)
    seed = int(hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:8], 16) % 100000

    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=900&height=383&seed={seed}&nologo=true"

    print(f"[cover] Generating with prompt: {prompt[:80]}...")

    req = Request(url, headers={"User-Agent": "DailyAINews/1.0"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read()

    with open(output_path, "wb") as f:
        f.write(data)

    print(f"[cover] Saved: {output_path} ({len(data)} bytes)")
    return output_path


def generate_cover_from_content(content_text, output_path="/tmp/cover.png"):
    """根据文章内容生成封面图"""
    keywords = extract_keywords(content_text)
    prompt = (
        f"Eye-catching technology magazine cover, {keywords}, "
        f"bold vibrant colors neon blue magenta, dramatic lighting, "
        f"abstract digital art, futuristic holographic effect, "
        f"no text no letters, 4K cinematic"
    )
    seed = int(hashlib.md5(content_text[:100].encode()).hexdigest()[:8], 16) % 100000
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=900&height=383&seed={seed}&nologo=true"

    print(f"[cover] Generating from content...")
    req = Request(url, headers={"User-Agent": "DailyAINews/1.0"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read()
    with open(output_path, "wb") as f:
        f.write(data)
    print(f"[cover] Saved: {output_path} ({len(data)} bytes)")
    return output_path


def build_prompt(title, subtitle):
    """根据标题构建图片生成prompt — 追求视觉冲击力"""
    visual_themes = {
        "agent": "autonomous AI agent robot futuristic city hologram",
        "robot": "humanoid robot chrome metallic dramatic pose",
        "chip": "glowing semiconductor chip neon circuits explosion",
        "开源": "glowing open source code terminal matrix style",
        "llm": "massive neural network brain glowing synapses",
        "药物": "molecular drug discovery glowing capsule lab",
        "医疗": "medical AI hologram doctor futuristic scan",
        "欺诈": "digital fraud hacker dark cyber security alert",
        "隐私": "digital privacy eye surveillance data stream",
        "教皇": " Vatican cathedral dramatic light AI contrast",
        "ted chiang": "philosophical mind consciousness abstract art",
        "诈骗": "dark web scam digital crime neon warning",
        "过滤": "digital filter data stream cleanup technology",
    }

    title_lower = (title + " " + subtitle).lower()
    theme_elements = []
    for keyword, visual in visual_themes.items():
        if keyword in title_lower:
            theme_elements.append(visual)

    if not theme_elements:
        theme_elements = [
            "artificial intelligence neural network",
            "futuristic technology hologram",
        ]

    elements_str = " ".join(theme_elements[:2])

    return (
        f"Eye-catching magazine cover illustration, {elements_str}, "
        f"vibrant neon blue and magenta gradient, dramatic cinematic lighting, "
        f"abstract geometric shapes, holographic digital effect, "
        f"no text no letters no words no watermark, "
        f"professional 4K ultra detailed, trending on artstation"
    )


def extract_keywords(text):
    """从文章中提取关键词"""
    text_lower = text.lower()
    keyword_map = {
        "agent": "AI agent autonomous robot",
        "drug discovery": "molecular drug discovery capsule",
        "protein": "protein structure biology 3D",
        "medical": "medical healthcare AI hologram",
        "llm": "large language model neural brain",
        "open source": "open source code terminal glowing",
        "chip": "AI chip semiconductor neon",
        "robot": "robotics chrome humanoid",
        "隐私": "privacy digital eye data stream",
        "欺诈": "cyber crime dark hacker alert",
        "过滤": "digital filter data stream",
    }
    found = []
    for kw, desc in keyword_map.items():
        if kw in text_lower:
            found.append(desc)
    if not found:
        found = ["artificial intelligence", "futuristic technology"]
    return " ".join(found[:2])


if __name__ == "__main__":
    path = generate_cover(
        "Google AI Agent偷看你的邮箱",
        "Gemini Spark · 隐私风暴",
        "/tmp/test_ai_cover.png"
    )
    print(f"Done: {path}")
