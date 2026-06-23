#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""报告生成：中文报告 + 微信公众号HTML（顶级杂志风格 v2）"""

import re


def markdown_to_wechat_html(md_content, chart_images=None):
    """Markdown → 微信公众号兼容HTML（v3: 独立卡片 + 数据图表）"""
    title_match = re.search(r'^# (.+)', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "AI前沿日报"

    date_match = re.search(r'\*\*报告日期\*\*:\s*(.+)', md_content)
    date_str = date_match.group(1).strip() if date_match else ""

    source_match = re.search(r'\*\*数据来源\*\*:\s*(.+)', md_content)
    source_str = source_match.group(1).strip() if source_match else ""

    parts = []

    # ===== CSS动画 =====
    parts.append('''<style>
@keyframes fadeUp { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
@keyframes fadeLeft { from { opacity:0; transform:translateX(-20px); } to { opacity:1; transform:translateX(0); } }
@keyframes fadeRight { from { opacity:0; transform:translateX(20px); } to { opacity:1; transform:translateX(0); } }
@keyframes fade { from { opacity:0; } to { opacity:1; } }
@keyframes barGrow { from { width:0; } to { width:100%; } }
@keyframes dotPulse { 0%,100% { box-shadow:0 0 0 0 rgba(58,123,213,0.4); } 50% { box-shadow:0 0 0 6px rgba(58,123,213,0); } }
@keyframes shimmer { 0% { background-position:-200% 0; } 100% { background-position:200% 0; } }
@keyframes gradientBG { 0% { background-position:0% 50%; } 50% { background-position:100% 50%; } 100% { background-position:0% 50%; } }
@keyframes borderGlow { 0% { border-color:rgba(58,123,213,0.3); } 50% { border-color:rgba(58,123,213,0.6); } 100% { border-color:rgba(58,123,213,0.3); } }
</style>''')

    # ===== Hero =====
    parts.append(f'''
<section style="margin:0;padding:0;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);">
  <section style="padding:44px 24px 38px;text-align:center;">
    <section style="display:inline-block;padding:4px 14px;background:rgba(255,255,255,0.08);border-radius:20px;font-size:11px;color:rgba(255,255,255,0.5);letter-spacing:3px;margin-bottom:16px;">{source_str if source_str else 'last30days · HN · GitHub'}</section>
    <section style="margin:0 auto 18px;width:50px;height:2px;background:linear-gradient(90deg,#00d2ff,#3a7bd5);border-radius:1px;"></section>
    <section style="font-size:26px;font-weight:800;color:#fff;line-height:1.35;margin-bottom:10px;">{title}</section>
    <section style="font-size:13px;color:rgba(255,255,255,0.45);letter-spacing:1px;">{date_str}</section>
    <section style="margin:20px auto 0;width:30px;height:2px;background:linear-gradient(90deg,#00d2ff,#3a7bd5);border-radius:1px;"></section>
  </section>
</section>''')

    # ===== 解析正文 =====
    lines = md_content.split("\n")
    in_list = False
    section_index = 0
    skip_header = True
    card_num = 0
    in_card = False
    current_h3_title = ''

    # 渐变色板
    gradients = [
        ("linear-gradient(135deg,#667eea,#764ba2)", "#667eea"),
        ("linear-gradient(135deg,#f093fb,#f5576c)", "#f5576c"),
        ("linear-gradient(135deg,#4facfe,#00f2fe)", "#4facfe"),
        ("linear-gradient(135deg,#43e97b,#38f9d7)", "#43e97b"),
        ("linear-gradient(135deg,#fa709a,#fee140)", "#fa709a"),
    ]

    charts_inserted = False
    for line in lines:
        s = line.strip()

        # 跳过头部元信息
        if skip_header:
            if s.startswith("# ") or s.startswith("**报告日期") or s.startswith("**数据来源") or s == "" or s == "---":
                continue
            skip_header = False

        # 空行
        if not s:
            if in_list:
                parts.append('</section>')
                in_list = False
            continue

        # H2 版块标题（独立标题条，不包裹内容）
        if s.startswith("## "):
            if in_card:
                parts.append('</section>')
                in_card = False
            section_index += 1
            text = s[3:]
            grad, accent = gradients[(section_index - 1) % len(gradients)]
            parts.append(f'''
<section style="margin:32px 0 12px;padding:14px 18px;background:{grad};border-radius:10px;animation:fadeUp 0.5s ease-out;">
  <section style="display:flex;align-items:center;">
    <section style="width:26px;height:26px;background:rgba(255,255,255,0.2);border-radius:7px;text-align:center;line-height:26px;font-size:13px;font-weight:bold;color:#fff;margin-right:10px;flex-shrink:0;">{section_index}</section>
    <section style="font-size:18px;font-weight:700;color:#fff;">{_fmt(text)}</section>
  </section>
</section>''')
            continue

        # H3 热点条目（独立卡片）
        if s.startswith("### "):
            text = s[4:]
            num_match = re.match(r'^(\d+)\.\s*(.*)', text)
            if num_match:
                num = num_match.group(1)
                title_text = num_match.group(2)
                card_num += 1
                # 关闭上一个卡片（如果有）
                if in_card:
                    parts.append('</section>')
                    in_card = False
                parts.append(f'''
<section style="margin:12px 0;padding:16px;background:#fff;border-radius:10px;border:1px solid #eef2ff;box-shadow:0 4px 16px rgba(0,0,0,0.04);animation:fadeLeft 0.4s ease-out {0.08 * (card_num % 6)}s both;">
  <section style="display:flex;align-items:flex-start;gap:12px;">
    <section style="flex-shrink:0;width:32px;height:32px;background:linear-gradient(135deg,#3a7bd5,#00d2ff);border-radius:10px;text-align:center;line-height:32px;font-size:15px;font-weight:bold;color:#fff;box-shadow:0 3px 10px rgba(58,123,213,0.25);animation:dotPulse 2s infinite;">{num}</section>
    <section style="flex:1;font-size:16px;font-weight:700;color:#1a1a1a;line-height:1.45;padding-top:4px;">{_fmt(title_text)}</section>
  </section>''')
                in_card = True
                current_h3_title = title_text
                continue
            else:
                parts.append(f'''
<section style="margin:14px 0 6px;font-size:16px;font-weight:700;color:#333;">{_fmt(text)}</section>''')
                continue

        # 分割线
        if s in ("---", "***"):
            if in_card:
                parts.append('</section>')
                in_card = False
            # 检查是否有匹配的图表插入到对应文章后
            if chart_images and current_h3_title:
                for img_url, caption in chart_images:
                    title_kw = current_h3_title[:12]
                    if title_kw in caption or any(kw in caption for kw in title_kw.split()[:2]):
                        parts.append(f'''
<section style="margin:16px 0;text-align:center;">
  <img src="{img_url}" style="width:100%;max-width:520px;border-radius:6px;" />
  <section style="font-size:11px;color:#999;margin-top:6px;letter-spacing:0.5px;">{caption}</section>
</section>''')
                        chart_images = [(u, c) for u, c in chart_images if u != img_url]
                        break
                current_h3_title = ''
            parts.append('<section style="margin:28px 0;height:1px;background:linear-gradient(90deg,transparent,#ddd,transparent);"></section>')
            continue

        # 列表项
        if s.startswith("- ") or s.startswith("* "):
            if not in_list:
                parts.append('<section style="margin:8px 0;">')
                in_list = True
            text = s[2:]
            if any(kw in text for kw in ["来源:", "热度:", "来源：", "热度："]):
                # 标签式来源信息
                parts.append(f'''
<section style="display:inline-block;margin:3px 4px 3px 0;padding:4px 10px;background:linear-gradient(135deg,#f0f4ff,#e8ecff);border-radius:6px;font-size:12px;color:#5a6a8a;line-height:1.4;">{_fmt(text)}</section>''')
            else:
                parts.append(f'''
<section style="margin:6px 0;padding:6px 0 6px 14px;border-left:2px solid #e0e6f0;font-size:14.5px;color:#555;line-height:1.75;">{_fmt(text)}</section>''')
            continue

        # 引用/斜体（编辑观点等）
        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            text = s.strip("*")
            parts.append(f'''
<section style="margin:14px 0;padding:14px 16px;background:linear-gradient(135deg,#fff9f0,#fff5f8);border-radius:10px;border-left:3px solid #fa709a;position:relative;">
  <section style="position:absolute;top:8px;left:12px;font-size:20px;color:rgba(250,112,154,0.2);">❝</section>
  <section style="font-size:14px;color:#888;font-style:italic;line-height:1.7;padding-left:16px;">{text}</section>
</section>''')
            continue

        # 普通段落
        parts.append(f'<p style="margin:8px 0;font-size:15px;color:#444;line-height:1.85;text-align:justify;letter-spacing:0.3px;">{_fmt(s)}</p>')

    # 关闭标签
    if in_list:
        parts.append('</section>')
    if in_card:
        parts.append('</section>')

    # ===== 底部 =====
    parts.append('''
<section style="margin:36px 0 0;">
  <section style="height:2px;background:linear-gradient(90deg,transparent,#3a7bd5,transparent);border-radius:1px;margin-bottom:24px;"></section>
  <section style="text-align:center;padding:24px 16px;background:linear-gradient(135deg,#f8f9ff,#f0f4ff);border-radius:14px;">
    <section style="font-size:11px;color:#aaa;letter-spacing:3px;margin-bottom:4px;">LAST30DAYS · DAILY AI INTELLIGENCE</section>
    <section style="font-size:11px;color:#ccc;">Hacker News · GitHub · AI 自动综合分析</section>
  </section>
</section>''')

    return "\n".join(parts)


def _fmt(text):
    """行内格式化"""
    text = re.sub(
        r'\*\*(.*?)\*\*',
        r'<strong style="color:#1a1a1a;font-weight:700;">\1</strong>',
        text
    )
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(
        r'`([^`]+)`',
        r'<code style="padding:2px 6px;background:#f0f4ff;border-radius:4px;font-size:13px;color:#3a7bd5;font-family:monospace;">\1</code>',
        text
    )
    return text
