#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""使用 AI 生成微信公众号封面图（通过 Pollinations API）"""

import os
import hashlib
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.parse import quote


def generate_cover(title, subtitle="", output_path="/tmp/cover.png"):
    """用 AI 生成封面图"""
    # 构建英文 prompt（Pollinations 对英文效果更好）
    prompt = build_prompt(title, subtitle)
    
    # 生成唯一seed避免缓存
    seed = int(hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:8], 16) % 100000
    
    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=900&height=383&seed={seed}&nologo=true"
    
    print(f"[cover] Generating with prompt: {prompt[:60]}...")
    
    req = Request(url, headers={"User-Agent": "DailyAINews/1.0"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read()
    
    with open(output_path, "wb") as f:
        f.write(data)
    
    print(f"[cover] Saved: {output_path} ({len(data)} bytes)")
    return output_path


def generate_cover_from_content(content_text, output_path="/tmp/cover.png"):
    """根据文章内容生成封面图"""
    # 提取关键词生成 prompt
    keywords = extract_keywords(content_text)
    prompt = f"Modern technology magazine cover about {keywords}, digital art, blue and purple gradient, circuit board patterns, neural network visualization, futuristic, clean design, professional"
    
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
    """根据标题构建图片生成prompt"""
    # 映射到视觉主题
    visual_themes = {
        "drug": "molecular structure DNA helix medical research",
        "protein": "protein folding molecular biology 3D structure",
        "cancer": "medical scan cells under microscope biomedical",
        "imaging": "MRI brain scan medical imaging technology",
        "genomic": "DNA sequencing genome data visualization",
        "llm": "neural network transformer architecture AI model",
        "agent": "autonomous robot AI agent digital assistant",
        "robot": "humanoid robot industrial automation technology",
        "chip": "semiconductor chip GPU AI hardware computing",
        "open source": "code terminal developer workspace programming",
    }
    
    title_lower = (title + " " + subtitle).lower()
    theme_elements = []
    for keyword, visual in visual_themes.items():
        if keyword in title_lower:
            theme_elements.append(visual)
    
    if not theme_elements:
        theme_elements = [
            "artificial intelligence",
            "digital technology",
            "futuristic interface"
        ]
    
    elements_str = " ".join(theme_elements[:2])
    
    return (
        f"Professional technology magazine cover illustration, "
        f"{elements_str}, "
        f"blue purple gradient background, abstract digital art, "
        f"clean modern design, no text no letters no words, "
        f"high quality 4K, cinematic lighting"
    )


def extract_keywords(text):
    """从文章中提取关键词"""
    text_lower = text.lower()
    
    keyword_map = {
        "agent": "AI agent autonomous",
        "drug discovery": "molecular drug discovery",
        "protein": "protein structure biology",
        "medical": "medical healthcare AI",
        "llm": "large language model neural network",
        "open source": "open source code",
        "chip": "AI chip semiconductor",
        "robot": "robotics automation",
    }
    
    found = []
    for kw, desc in keyword_map.items():
        if kw in text_lower:
            found.append(desc)
    
    if not found:
        found = ["artificial intelligence", "digital technology"]
    
    return " ".join(found[:2])


if __name__ == "__main__":
    path = generate_cover(
        "AI前沿日报",
        "AI Agent · 医疗AI · 开源工具",
        "/tmp/test_ai_cover.png"
    )
    print(f"Done: {path}")
