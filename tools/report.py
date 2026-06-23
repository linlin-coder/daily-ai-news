#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""报告生成：中文报告 + 微信公众号HTML（顶级杂志风格）"""

import re


def markdown_to_wechat_html(md_content):
    """Markdown → 微信公众号兼容HTML（顶级杂志风格）"""
    # 提取标题用于 hero 区域
    title_match = re.search(r'^# (.+)', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "AI前沿日报"

    date_match = re.search(r'\*\*报告日期\*\*:\s*(.+)', md_content)
    date_str = date_match.group(1).strip() if date_match else ""

    parts = []

    # ===== 全局样式 + CSS动画 =====
    parts.append('''<style>
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-30px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.card-hover { transition: all 0.3s ease; }
</style>''')

    # ===== Hero 区域 =====
    parts.append(f'''
<section style="margin:0;padding:0;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);border-radius:0;overflow:hidden;">
  <section style="padding:40px 24px 35px;text-align:center;background:linear-gradient(135deg,rgba(15,12,41,0.9),rgba(48,43,99,0.9),rgba(36,36,62,0.9));animation:fadeIn 0.8s ease-out;">
    <!-- 装饰元素 -->
    <section style="margin:0 auto 15px;width:60px;height:3px;background:linear-gradient(90deg,#00d2ff,#3a7bd5);border-radius:2px;animation:shimmer 2s infinite;"></section>
    <section style="font-size:13px;color:rgba(255,255,255,0.6);letter-spacing:4px;text-transform:uppercase;margin-bottom:12px;font-family:monospace;">DAILY AI INTELLIGENCE</section>
    <section style="font-size:28px;font-weight:800;color:#fff;line-height:1.3;margin-bottom:8px;text-shadow:0 2px 10px rgba(0,0,0,0.3);">{title}</section>
    <section style="font-size:14px;color:rgba(255,255,255,0.5);margin-bottom:20px;">{date_str}</section>
    <!-- 装饰线 -->
    <section style="width:40px;height:2px;background:linear-gradient(90deg,#00d2ff,#3a7bd5);margin:0 auto;border-radius:1px;"></section>
  </section>
</section>''')

    # ===== 解析正文 =====
    lines = md_content.split("\n")
    in_list = False
    in_section = False
    section_index = 0
    skip_hero = True

    for line in lines:
        s = line.strip()

        # 跳过已处理的标题
        if skip_hero:
            if s.startswith("# ") or s.startswith("**报告日期") or s.startswith("**数据来源") or s == "---" or s == "":
                continue
            skip_hero = False

        if not s:
            if in_list:
                parts.append('</section>')
                in_list = False
            if in_section:
                parts.append('</section>')
                in_section = False
            continue

        # H2 标题 - 大版块标题
        if s.startswith("## "):
            if in_section:
                parts.append('</section>')
            section_index += 1
            text = s[3:]
            # 渐变色标题条
            colors = [
                "linear-gradient(135deg,#667eea,#764ba2)",
                "linear-gradient(135deg,#f093fb,#f5576c)",
                "linear-gradient(135deg,#4facfe,#00f2fe)",
                "linear-gradient(135deg,#43e97b,#38f9d7)",
                "linear-gradient(135deg,#fa709a,#fee140)",
            ]
            color = colors[(section_index - 1) % len(colors)]
            parts.append(f'''
<section style="margin:28px 0 0;padding:0;">
  <section style="position:relative;padding:16px 20px 14px 55px;background:{color};border-radius:12px 12px 0 0;animation:slideInLeft 0.6s ease-out;">
    <section style="position:absolute;left:16px;top:50%;transform:translateY(-50%);width:28px;height:28px;background:rgba(255,255,255,0.25);border-radius:50%;text-align:center;line-height:28px;font-size:14px;font-weight:bold;color:#fff;">{section_index}</section>
    <section style="font-size:19px;font-weight:700;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,0.2);">{_fmt(text)}</section>
  </section>
  <section style="background:#fff;padding:20px;border-radius:0 0 12px 12px;box-shadow:0 4px 20px rgba(0,0,0,0.06);animation:fadeInUp 0.6s ease-out 0.2s both;">''')
            in_section = True
            continue

        # H3 标题 - 子标题（带序号的热点）
        if s.startswith("### "):
            text = s[4:]
            # 判断是否是带数字序号的热点
            num_match = re.match(r'^(\d+)\.\s*(.*)', text)
            if num_match:
                num = num_match.group(1)
                title_text = num_match.group(2)
                parts.append(f'''
<section style="margin:16px 0 12px;padding:14px 16px 14px 58px;background:linear-gradient(135deg,#f8f9ff,#f0f4ff);border-radius:10px;border-left:4px solid #3a7bd5;position:relative;animation:fadeInUp 0.5s ease-out;">
  <section style="position:absolute;left:14px;top:14px;width:30px;height:30px;background:linear-gradient(135deg,#3a7bd5,#00d2ff);border-radius:8px;text-align:center;line-height:30px;font-size:14px;font-weight:bold;color:#fff;box-shadow:0 2px 8px rgba(58,123,213,0.3);">{num}</section>
  <section style="font-size:17px;font-weight:700;color:#1a1a1a;line-height:1.4;">{_fmt(title_text)}</section>
</section>''')
            else:
                parts.append(f'''
<section style="margin:16px 0 8px;font-size:16px;font-weight:700;color:#333;padding-left:12px;border-left:3px solid #3a7bd5;">{_fmt(text)}</section>''')
            continue

        # 分割线
        if s in ("---", "***"):
            if in_section:
                parts.append('</section>')
                in_section = False
            parts.append('<section style="margin:24px 0;height:1px;background:linear-gradient(90deg,transparent,#e0e0e0,transparent);"></section>')
            continue

        # 列表项
        if s.startswith("- ") or s.startswith("* "):
            if not in_list:
                parts.append('<section style="margin:8px 0;padding:0;">')
                in_list = True
            text = s[2:]
            # 特殊格式：来源/热度信息
            if any(kw in text for kw in ["来源:", "热度:", "来源：", "热度："]):
                parts.append(f'''
<section style="display:flex;align-items:center;margin:6px 0;padding:8px 12px;background:#f8f9fa;border-radius:8px;font-size:13px;color:#666;">
  <section style="width:4px;height:4px;background:#3a7bd5;border-radius:50%;margin-right:10px;flex-shrink:0;"></section>
  {_fmt(text)}
</section>''')
            else:
                parts.append(f'''
<section style="margin:5px 0;padding:4px 0 4px 16px;border-left:2px solid #e8ecf3;font-size:15px;color:#444;line-height:1.7;">{_fmt(text)}</section>''')
            continue

        # 引用/斜体
        if s.startswith("*") and s.endswith("*") and not s.startswith("**"):
            text = s.strip("*")
            parts.append(f'''
<section style="margin:12px 0;padding:12px 16px;background:linear-gradient(135deg,#fff8f0,#fff);border-left:3px solid #fa709a;border-radius:0 8px 8px 0;font-size:14px;color:#888;font-style:italic;">{text}</section>''')
            continue

        # 普通段落
        parts.append(f'<p style="margin:10px 0;font-size:15px;color:#444;line-height:1.9;text-align:justify;letter-spacing:0.5px;">{_fmt(s)}</p>')

    # 关闭所有打开的标签
    if in_list:
        parts.append('</section>')
    if in_section:
        parts.append('</section></section>')

    # ===== 底部 =====
    parts.append('''
<section style="margin:30px 0 0;padding:0;">
  <section style="height:3px;background:linear-gradient(90deg,#3a7bd5,#00d2ff,#3a7bd5);border-radius:2px;margin-bottom:20px;"></section>
  <section style="text-align:center;padding:20px;background:linear-gradient(135deg,#f8f9ff,#f0f4ff);border-radius:12px;">
    <section style="font-size:12px;color:#999;letter-spacing:2px;margin-bottom:6px;">POWERED BY last30days ENGINE</section>
    <section style="font-size:11px;color:#bbb;">数据来源: Hacker News / GitHub · AI 自动综合分析</section>
  </section>
</section>
</section>''')

    return "\n".join(parts)


def _fmt(text):
    """行内格式化"""
    # 粗体 → 渐变高亮
    text = re.sub(
        r'\*\*(.*?)\*\*',
        r'<strong style="color:#1a1a1a;font-weight:700;">\1</strong>',
        text
    )
    # 链接 → 只保留文字
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # 代码 → 标签样式
    text = re.sub(
        r'`([^`]+)`',
        r'<code style="padding:2px 6px;background:#f0f4ff;border-radius:4px;font-size:13px;color:#3a7bd5;font-family:monospace;">\1</code>',
        text
    )
    return text
