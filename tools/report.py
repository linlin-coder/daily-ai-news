#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""报告生成：中文报告 + 微信HTML"""

import re
from datetime import datetime


def generate_chinese_report(results, topic="AI热点"):
    """从研究结果生成中文报告"""
    today = datetime.now().strftime("%Y年%m月%d日")
    title = f"AI前沿日报 | {today}"

    # 分类
    hn_stories = [r for r in results if r.get("source") == "hackernews"]
    gh_repos = [r for r in results if r.get("source") == "github"]

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"**报告日期**: {today}")
    lines.append(f"**数据来源**: Hacker News / GitHub")
    lines.append("")
    lines.append("---")
    lines.append("")

    # HN 热点
    if hn_stories:
        lines.append("## 今日AI热点讨论")
        lines.append("")
        for i, s in enumerate(hn_stories[:12], 1):
            pts = s.get("points", 0)
            cmt = s.get("comments", 0)
            lines.append(f"**{i}. {s['title']}**")
            lines.append(f"- Hacker News | {pts}分 | {cmt}条评论 | {s.get('date', '')}")
            lines.append(f"- {s['url']}")
            lines.append("")

    # GitHub
    if gh_repos:
        lines.append("## GitHub 热门AI项目")
        lines.append("")
        for i, r in enumerate(gh_repos[:8], 1):
            desc = r.get("description", "暂无描述")[:120]
            lines.append(f"**{i}. {r['title']}**")
            lines.append(f"- ⭐ {r.get('stars', 0)} | {r.get('language', 'N/A')}")
            lines.append(f"- {desc}")
            lines.append(f"- {r['url']}")
            lines.append("")

    # 趋势总结
    lines.append("---")
    lines.append("")
    lines.append("## 关键趋势")
    lines.append("")

    trends = _extract_trends(results)
    for i, t in enumerate(trends, 1):
        lines.append(f"**{i}. {t}**")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*本报告由 AI 自动生成，数据来自 Hacker News 和 GitHub 的公开讨论。*")

    report = "\n".join(lines)

    # 摘要
    digest = f"今日AI热点："
    if hn_stories:
        digest += hn_stories[0].get("title", "")[:40]
    if gh_repos:
        digest += f" | GitHub热门：{gh_repos[0].get('title', '')}"

    return title, digest, report


def _extract_trends(results):
    """从结果中提取趋势"""
    all_titles = " ".join([r.get("title", "") for r in results]).lower()
    all_descs = " ".join([r.get("description", "") for r in results]).lower()
    combined = all_titles + " " + all_descs

    trend_keywords = {
        "open source": "开源AI模型与工具持续涌现",
        "agent": "AI Agent自主执行能力快速进化",
        "reasoning": "推理能力成为大模型核心竞争力",
        "multimodal": "多模态AI走向实用化",
        "safety": "AI安全与对齐研究热度上升",
        "coding": "AI编程助手重塑开发工作流",
        "video": "AI视频生成技术突破",
        "robotics": "具身智能与机器人领域加速发展",
        "drug": "AI药物发现与生物医药深度融合",
        "protein": "蛋白质设计与结构预测新突破",
        "medical": "AI医疗诊断走向临床落地",
        "chip": "AI芯片与算力基础设施竞争",
        "regulation": "全球AI监管政策加速落地",
        "startup": "AI创业生态持续活跃",
        "benchmark": "模型评测与基准测试引发讨论",
    }

    trends = []
    for keyword, trend in trend_keywords.items():
        if keyword in combined:
            trends.append(trend)
            if len(trends) >= 5:
                break

    # 补充默认趋势
    defaults = [
        "大模型能力边界持续拓展",
        "AI应用从实验室走向产业落地",
        "开源与闭源模型竞争加剧",
    ]
    for d in defaults:
        if len(trends) >= 5:
            break
        trends.append(d)

    return trends[:5]


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

        # 标题
        if s.startswith("# "):
            parts.append(f'<h1 style="font-size:22px;font-weight:bold;color:#1a1a1a;border-bottom:2px solid #07c160;padding-bottom:8px;margin:24px 0 16px;">{_fmt(s[2:])}</h1>')
            continue
        if s.startswith("## "):
            parts.append(f'<h2 style="font-size:18px;font-weight:bold;color:#1a1a1a;border-left:4px solid #07c160;padding-left:12px;margin:20px 0 12px;">{_fmt(s[3:])}</h2>')
            continue
        if s.startswith("### "):
            parts.append(f'<h3 style="font-size:16px;font-weight:bold;color:#333;margin:16px 0 8px;">{_fmt(s[4:])}</h3>')
            continue

        # 分割线
        if s in ("---", "***"):
            parts.append('<hr style="border:none;border-top:1px solid #e5e5e5;margin:20px 0;">')
            continue

        # 列表
        if s.startswith("- ") or s.startswith("* "):
            if not in_list:
                parts.append('<ul style="margin:8px 0;padding-left:20px;">')
                in_list = True
            parts.append(f'<li style="margin:4px 0;">{_fmt(s[2:])}</li>')
            continue

        if in_list and not s.startswith("- ") and not s.startswith("* "):
            parts.append("</ul>")
            in_list = False

        # 斜体
        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            parts.append(f'<p style="font-size:14px;color:#666;font-style:italic;margin:8px 0;">{_fmt(s.strip("*"))}</p>')
            continue

        # 段落
        parts.append(f'<p style="margin:8px 0;text-align:justify;">{_fmt(s)}</p>')

    if in_list:
        parts.append("</ul>")

    parts.append("</section>")
    return "\n".join(parts)


def _fmt(text):
    """行内格式"""
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#1a1a1a;">\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text
