"""从 last30days 原始数据提取指标并用 matplotlib 生成科学图表"""

import re
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np


def _setup_font():
    """设置中文字体"""
    candidates = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
    ]
    for path in candidates:
        if os.path.exists(path):
            prop = fm.FontProperties(fname=path)
            plt.rcParams['font.family'] = prop.get_name()
            plt.rcParams['axes.unicode_minus'] = False
            return prop
    plt.rcParams['axes.unicode_minus'] = False
    return None


def _extract_articles(md_content):
    """从 markdown 提取文章标题、来源、热度"""
    articles = []
    lines = md_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r'^###\s+\d+\.\s+(.*)', line)
        if m:
            title = m.group(1).strip()
            art = {'title': title, 'score': 0, 'comments': 0, 'source': 'unknown'}
            # 向后搜索元信息行（紧跟的 1-3 行）
            for j in range(i+1, min(i+4, len(lines))):
                meta_line = lines[j]
                sm = re.search(r'\*?\*?热度\*?\*?[：:]\s*(\d+)分', meta_line)
                if sm:
                    art['score'] = int(sm.group(1))
                cm = re.search(r'(\d+)条评论', meta_line)
                if cm:
                    art['comments'] = int(cm.group(1))
                src_m = re.search(r'\*?\*?来源\*?\*?[：:]\s*(.+?)(?:\s*\|\s*\*?\*?热度)', meta_line)
                if not src_m:
                    src_m = re.search(r'\*?\*?来源\*?\*?[：:]\s*(.+)', meta_line)
                if src_m:
                    art['source'] = src_m.group(1).strip()
            articles.append(art)
        i += 1
    return articles


def _extract_engine_stats(md_content):
    """从 engine footer 提取统计"""
    stats = {}
    m = re.search(r'HN:\s*(\d+)\s*storys?\s*[│|]\s*(\d+)\s*points?\s*[│|]\s*(\d+)\s*comments?', md_content)
    if m:
        stats['hn_stories'] = int(m.group(1))
        stats['hn_points'] = int(m.group(2))
        stats['hn_comments'] = int(m.group(3))
    m = re.search(r'GitHub:\s*(\d+)\s*items?\s*[│|]\s*(\d+)\s*comments?', md_content)
    if m:
        stats['gh_items'] = int(m.group(1))
        stats['gh_comments'] = int(m.group(2))
    return stats


def generate_charts(md_content, output_dir):
    """生成所有图表，返回 [(path, caption), ...]"""
    font_prop = _setup_font()
    articles = _extract_articles(md_content)
    stats = _extract_engine_stats(md_content)
    charts = []

    plt.rcParams.update({
        'font.size': 10,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.linewidth': 0.8,
        'figure.dpi': 150,
    })

    # ===== Chart 1: 热度柱状图 =====
    scored = [a for a in articles if a['score'] > 0]
    if scored:
        scored.sort(key=lambda x: x['score'], reverse=True)
        fig, ax = plt.subplots(figsize=(6, 3.5))
        labels = [a['title'][:18] + ('...' if len(a['title']) > 18 else '') for a in scored]
        scores = [a['score'] for a in scored]
        colors = ['#667eea' if i == 0 else '#764ba2' if i < 3 else '#a8b4e2'
                  for i in range(len(scored))]
        bars = ax.barh(range(len(scored)), scores, color=colors, height=0.6, edgecolor='none')
        ax.set_yticks(range(len(scored)))
        ax.set_yticklabels(labels, fontproperties=font_prop, fontsize=9)
        ax.set_xlabel('Hacker News 热度 (points)', fontproperties=font_prop, fontsize=9)
        ax.set_title('今日热点话题热度排名', fontproperties=font_prop, fontsize=12, fontweight='bold', pad=12)
        ax.invert_yaxis()
        for bar, val in zip(bars, scores):
            ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2,
                    str(val), va='center', fontsize=9, color='#333')
        ax.spines['left'].set_visible(False)
        ax.tick_params(left=False)
        fig.tight_layout()
        path = os.path.join(output_dir, 'chart-scores.png')
        fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        charts.append((path, '热点话题 Hacker News 热度对比'))

    # ===== Chart 2: 来源分布饼图 =====
    hn_count = sum(1 for a in articles if 'HN' in a['source'] or 'Hacker' in a['source'] or 'Verdi' in a['source'] or 'TechCrunch' in a['source'])
    gh_count = sum(1 for a in articles if 'GitHub' in a['source'] or 'github' in a['source'])
    other_count = len(articles) - hn_count - gh_count
    if hn_count + gh_count + other_count > 0:
        fig, ax = plt.subplots(figsize=(4, 4))
        sizes = [s for s in [hn_count, gh_count, other_count] if s > 0]
        labels_pie = []
        if hn_count > 0: labels_pie.append(f'Hacker News\n{hn_count}篇')
        if gh_count > 0: labels_pie.append(f'GitHub\n{gh_count}篇')
        if other_count > 0: labels_pie.append(f'其他\n{other_count}篇')
        colors_pie = ['#667eea', '#f093fb', '#4facfe'][:len(sizes)]
        explode = [0.03] * len(sizes)
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels_pie, colors=colors_pie, explode=explode,
            autopct='%1.0f%%', startangle=90, textprops={'fontproperties': font_prop, 'fontsize': 10},
            pctdistance=0.75
        )
        for t in autotexts:
            t.set_fontsize(9)
            t.set_color('#333')
        ax.set_title('数据来源分布', fontproperties=font_prop, fontsize=12, fontweight='bold', pad=16)
        fig.tight_layout()
        path = os.path.join(output_dir, 'chart-source.png')
        fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        charts.append((path, '本次采集数据来源分布'))

    # ===== Chart 3: 综合统计卡片 =====
    total_articles = len(articles)
    total_comments = sum(a['comments'] for a in articles)
    total_points = sum(a['score'] for a in articles)
    if stats:
        hn_pts = stats.get('hn_points', total_points)
        gh_cmt = stats.get('gh_comments', 0)
    else:
        hn_pts = total_points
        gh_cmt = 0

    fig, axes = plt.subplots(1, 4, figsize=(7, 1.8))
    metrics = [
        ('📰', str(total_articles), '篇文章'),
        ('🔥', str(hn_pts), '总热度'),
        ('💬', str(total_comments), '条评论'),
        ('🐙', str(stats.get('gh_items', gh_count)), 'GitHub项目'),
    ]
    card_colors = ['#f0f4ff', '#fff0f6', '#f0fff4', '#f8f0ff']
    for ax, (icon, val, label), bg in zip(axes, metrics, card_colors):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                     facecolor=bg, edgecolor='#eef', linewidth=1.5, zorder=0))
        ax.text(0.5, 0.62, val, ha='center', va='center', fontsize=18,
                fontweight='bold', color='#3a7bd5', transform=ax.transAxes, zorder=1)
        ax.text(0.5, 0.25, label, ha='center', va='center', fontsize=8,
                color='#888', transform=ax.transAxes, zorder=1,
                fontproperties=font_prop)
        ax.axis('off')
    fig.suptitle('本次采集概览', fontproperties=font_prop, fontsize=11,
                 fontweight='bold', y=1.08, color='#333')
    fig.tight_layout()
    path = os.path.join(output_dir, 'chart-stats.png')
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    charts.append((path, '本次采集综合统计'))

    return charts


if __name__ == '__main__':
    import sys
    md_file = sys.argv[1] if len(sys.argv) > 1 else 'output/ai-news-2026-06-23.md'
    output_dir = os.path.dirname(md_file) or 'output'
    with open(md_file) as f:
        md = f.read()
    charts = generate_charts(md, output_dir)
    for path, caption in charts:
        print(f'{path} → {caption}')
