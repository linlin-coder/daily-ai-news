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


# 主题 → 视觉元素映射表（强调差异化，避免千篇一律的人脸）
VISUAL_MAP = {
    # AI 产品/模型
    "gemini": "glowing Google Gemini crystal orb floating in dark space with light rays",
    "gpt": "massive glowing GPT text stream flowing through digital void",
    "claude": "ethereal Claude AI consciousness expanding into geometric patterns",
    "chatgpt": "conversation bubbles transforming into holographic knowledge graph",
    "llm": "towering neural network architecture with cascading data streams",
    "大模型": "towering neural network architecture with cascading data streams",
    "语言模型": "towering neural network architecture with cascading data streams",

    # AI Agent / 自动化
    "agent": "autonomous robot hand reaching for floating digital task icons in space",
    "自动化": "chain of dominoes falling with digital sparks and automation symbols",

    # 隐私/安全
    "隐私": "shattered glass screen revealing digital surveillance eye behind it",
    "安全": "glowing cybersecurity shield deflecting red digital attacks",
    "监控": "wall of surveillance camera lenses with red laser scanning beams",
    "数据泄露": "cracked server tower leaking glowing data streams into darkness",

    # 欺诈/滥用
    "欺诈": "split screen showing real human face vs AI generated fake face",
    "诈骗": "phone screen displaying scam call with warning symbols flashing",
    "深度伪造": "face being digitally reconstructed pixel by pixel in real time",
    "deepfake": "face being digitally reconstructed pixel by pixel in real time",
    "假": "two identical human figures one made of light one made of pixels",

    # 医疗/生物
    "医疗": "holographic DNA double helix floating above futuristic medical scanner",
    "药物": "molecular capsule dissolving into glowing therapeutic particles",
    "蛋白质": "intricate protein folding 3D structure glowing in blue light",
    "基因": "DNA sequencing gel with glowing bands reading genetic code",
    "生物": "petri dish with glowing cell divisions under futuristic microscope",
    "健康": "digital heartbeat line transforming into healthy organ hologram",

    # 芯片/硬件
    "芯片": "macro shot of GPU chip die with neon circuits firing data pulses",
    "gpu": "server rack filled with glowing GPUs connected by laser links",
    "算力": "massive data center corridor with rows of pulsing compute nodes",

    # 开源
    "开源": "code editor window exploding into collaborative global developer network",
    "github": "GitHub contribution graph transforming into glowing world map",

    # 机器人
    "机器人": "humanoid robot hand and human hand reaching toward each other in space",
    "具身": "robot interacting with physical objects in a real kitchen environment",

    # 自动驾驶
    "自动驾驶": "self-driving car sensor fusion visualization with LiDAR point cloud",
    "无人": "fleet of delivery drones flying formation over futuristic city at night",

    # 伦理/社会
    "伦理": "ancient scales of justice weighing human brain vs computer chip",
    "偏见": "mirrored faces splitting into biased red and blue halves",
    "就业": "human worker and robot arm collaborating at same workbench",
    "教育": "students in classroom with floating holographic AI tutor",

    # 投资/商业
    "融资": "rocket ship launching from laptop screen trailing stock chart upward",
    "市值": "massive golden bull statue made of circuit boards and coins",
    "裁员": "empty office desk with abandoned computer screen showing layoff email",

    # 写作/创作
    "写作": "fountain pen tip dripping glowing ink that forms digital words",
    "创作": "artist palette exploding with AI-generated surreal dreamscapes",
    "图像": "photo camera lens splitting into kaleidoscope of AI-generated art styles",
    "视频": "film reel unwinding into holographic movie scenes in mid-air",

    # 国家安全（敏感话题，用视觉化表达）
    "国家安全": "digital globe with encrypted data streams orbiting around it",
    "情报": "encrypted message symbols floating in dark digital space",
    "政府": "government building silhouette made of binary code and data streams",
}


def _fetch_image(url):
    """带重试的图片下载"""
    import time
    req = Request(url, headers={"User-Agent": "DailyAINews/1.0"})
    for attempt in range(3):
        try:
            with urlopen(req, timeout=60) as resp:
                return resp.read()
        except Exception as e:
            print(f"[cover] Attempt {attempt+1} failed: {e}")
            if attempt == 2:
                raise
            time.sleep(3)


def generate_cover(title, subtitle="", output_path="/tmp/cover.png"):
    """用 AI 生成封面图"""
    prompt = build_prompt(title, subtitle)
    seed = int(hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:8], 16) % 100000

    url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=900&height=383&seed={seed}&nologo=true"

    print(f"[cover] Generating: {prompt[:100]}...")
    data = _fetch_image(url)

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

    data = _fetch_image(url)

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
    """组合最终的图片生成 prompt — 明确排除人脸"""
    import random
    elements_str = " ".join(elements[:2])

    comps = [
        "dramatic close-up", "wide cinematic view", "floating in dark void",
        "exploding burst of light", "abstract geometric composition",
    ]
    comp = random.choice(comps)

    return (
        f"Technology magazine cover, {comp}, {elements_str}, "
        f"neon blue magenta gradient, holographic effect, "
        f"no text no letters no face no person no human no portrait, "
        f"4K concept art"
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
