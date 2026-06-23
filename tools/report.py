#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""报告生成：中文报告 + 微信HTML"""

import re


def markdown_to_wechat_html(md_content):
    """Markdown → 微信公众号兼容HTML"""
    parts = []
    parts.append('<section style="max-width:100%;box-sizing:border-box;font-size:16px;color:#333;line-height:1.8;padding:20px;">')

    lines = md_content.split("\n")
    in_list = False

    for line in lines:
        s = line.strip()

        if not s:
            if in_list:
                parts.append("</ul>")
                in_list = False
            parts.append("<br>")
            continue

        if s.startswith("# "):
            parts.append(f'<h1 style="font-size:22px;font-weight:bold;color:#1a1a1a;border-bottom:2px solid #07c160;padding-bottom:8px;margin:24px 0 16px;">{_fmt(s[2:])}</h1>')
            continue
        if s.startswith("## "):
            parts.append(f'<h2 style="font-size:18px;font-weight:bold;color:#1a1a1a;border-left:4px solid #07c160;padding-left:12px;margin:20px 0 12px;">{_fmt(s[3:])}</h2>')
            continue
        if s.startswith("### "):
            parts.append(f'<h3 style="font-size:16px;font-weight:bold;color:#333;margin:16px 0 8px;">{_fmt(s[4:])}</h3>')
            continue

        if s in ("---", "***"):
            parts.append('<hr style="border:none;border-top:1px solid #e5e5e5;margin:20px 0;">')
            continue

        if s.startswith("- ") or s.startswith("* "):
            if not in_list:
                parts.append('<ul style="margin:8px 0;padding-left:20px;">')
                in_list = True
            parts.append(f'<li style="margin:4px 0;">{_fmt(s[2:])}</li>')
            continue

        if in_list and not s.startswith("- ") and not s.startswith("* "):
            parts.append("</ul>")
            in_list = False

        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            parts.append(f'<p style="font-size:14px;color:#666;font-style:italic;margin:8px 0;">{_fmt(s.strip("*"))}</p>')
            continue

        parts.append(f'<p style="margin:8px 0;text-align:justify;">{_fmt(s)}</p>')

    if in_list:
        parts.append("</ul>")

    parts.append("</section>")
    return "\n".join(parts)


def _fmt(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#1a1a1a;">\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text
