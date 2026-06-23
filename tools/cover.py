#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""根据文章内容生成微信公众号封面图"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


def generate_cover(title, subtitle="", output_path="/tmp/cover.png"):
    """生成微信公众号封面图 (900x383)"""
    width, height = 900, 383

    # 渐变背景
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # 深蓝到青色渐变
    for y in range(height):
        r = int(15 + 25 * (y / height))
        g = int(30 + 80 * (y / height))
        b = int(80 + 100 * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 装饰元素 - 半透明圆点
    for i in range(8):
        x = 50 + i * 110
        y_pos = 30 + (i % 3) * 40
        draw.ellipse([x, y_pos, x + 20, y_pos + 20], fill=(255, 255, 255, 30))

    # 尝试加载字体
    font_title = _get_font(36)
    font_sub = _get_font(18)
    font_date = _get_font(14)

    # 标题（居中，自动换行）
    title_lines = _wrap_text(title, font_title, width - 100)
    y_start = 80
    for i, line in enumerate(title_lines[:3]):
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2
        draw.text((x, y_start + i * 50), line, fill="white", font=font_title)

    # 副标题
    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=font_sub)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2
        y = y_start + len(title_lines[:3]) * 50 + 20
        draw.text((x, y), subtitle, fill=(200, 220, 255), font=font_sub)

    # 底部日期
    date_str = datetime.now().strftime("%Y.%m.%d")
    draw.text((width - 150, height - 40), date_str, fill=(150, 170, 200), font=font_date)

    # 左侧装饰线
    draw.rectangle([30, 60, 34, height - 60], fill=(100, 200, 150))

    img.save(output_path, "PNG")
    return output_path


def _get_font(size):
    """尝试加载中文字体"""
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap_text(text, font, max_width):
    """文本自动换行"""
    lines = []
    current = ""
    for char in text:
        test = current + char
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] > max_width:
            if current:
                lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


if __name__ == "__main__":
    path = generate_cover(
        "AI前沿日报",
        "每日AI热点追踪 · 科研 · 工具 · 产业",
        "/tmp/test_cover.png"
    )
    print(f"Cover saved: {path}")
