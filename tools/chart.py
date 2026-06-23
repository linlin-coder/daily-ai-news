"""从文章内容中提取真实数据，用 nature-figure 标准绘制科学图表"""

import re
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np


def _setup_font():
    """Nature 风格字体设置"""
    candidates = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    ]
    font_prop = None
    for path in candidates:
        if os.path.exists(path):
            font_prop = fm.FontProperties(fname=path)
            break

    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'svg.fonttype': 'none',
        'pdf.fonttype': 42,
        'font.size': 8,
        'axes.spines.right': False,
        'axes.spines.top': False,
        'axes.linewidth': 0.6,
        'axes.unicode_minus': False,
        'figure.dpi': 200,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.facecolor': 'white',
    })
    return font_prop


def _extract_data_points(md_content):
    """从文章正文中提取真实数据点（不是元数据）

    扫描所有段落，寻找：
    - 百分比数字 (增长XX%、XX%准确率)
    - 具体数值 (达到XX万、XX亿美元)
    - 对比数据 (从X增长到Y)
    返回: [(context, value, unit, source_title), ...]
    """
    data_points = []
    lines = md_content.split('\n')
    current_title = ''

    for line in lines:
        # 跟踪当前文章标题
        m = re.match(r'^###\s+\d+\.\s+(.*)', line.strip())
        if m:
            current_title = m.group(1).strip()

        # 跳过元数据行
        if line.strip().startswith('**来源**') or line.strip().startswith('**热度**'):
            continue

        # 匹配百分比数据
        for m in re.finditer(r'(\d+(?:\.\d+)?)\s*%\s*[）)）]?', line):
            val = float(m.group(1))
            # 获取前后文作为上下文
            start = max(0, m.start() - 30)
            end = min(len(line), m.end() + 30)
            context = line[start:end].strip()
            # 提取单位/指标名
            unit_match = re.search(r'[\u4e00-\u9fff]+(?:增长|提升|下降|增加|减少|达到|占比|准确率|通过率|成功率)', line[max(0, m.start()-15):m.end()+5])
            unit = unit_match.group(0) if unit_match else '占比'
            data_points.append((context, val, '%', current_title))

        # 匹配具体金额/数量
        for m in re.finditer(r'(\d+(?:\.\d+)?)\s*(?:亿|万|百万|千|美元|元|人|家|篇|个)', line):
            val = float(m.group(1))
            unit = m.group(0)
            start = max(0, m.start() - 20)
            end = min(len(line), m.end() + 20)
            context = line[start:end].strip()
            # 过滤掉太小或太大的无关数字
            if val > 0 and val < 10000:
                data_points.append((context, val, unit, current_title))

    return data_points


def _group_by_topic(data_points):
    """按文章标题分组数据点"""
    groups = {}
    for context, val, unit, title in data_points:
        if title not in groups:
            groups[title] = []
        groups[title].append((context, val, unit))
    return groups


def generate_charts(md_content, output_dir):
    """从文章内容中提取真实数据并生成图表

    只有当文章包含可量化的数据时才生成图表。
    返回: [(path, caption), ...]
    """
    font_prop = _setup_font()
    data_points = _extract_data_points(md_content)

    if not data_points:
        return []

    topic_groups = _group_by_topic(data_points)
    charts = []

    # ===== 为每个有数据的文章生成图表 =====
    chart_idx = 0
    for title, points in topic_groups.items():
        # 只取百分比类型的数据做对比图
        pct_points = [(c, v, u) for c, v, u in points if u == '%']
        if len(pct_points) >= 2:
            chart_idx += 1
            fig, ax = plt.subplots(figsize=(4.5, 2.8))

            labels = [c[:20] for c, v, u in pct_points]
            values = [v for c, v, u in pct_points]

            x = np.arange(len(labels))
            bars = ax.bar(x, values, width=0.5, color='#667eea', edgecolor='none', alpha=0.85)

            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontproperties=font_prop, fontsize=7, rotation=20, ha='right')
            ax.set_ylabel('%', fontsize=8)
            ax.set_title(title[:30], fontproperties=font_prop, fontsize=9, fontweight='bold', pad=8)

            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{val:.0f}%', ha='center', va='bottom', fontsize=7, color='#333')

            ax.spines['left'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_linewidth(0.4)
            ax.spines['bottom'].set_linewidth(0.4)
            ax.tick_params(axis='both', length=3, width=0.4)
            ax.set_ylim(0, max(values) * 1.2 if values else 100)

            fig.tight_layout()
            path = os.path.join(output_dir, f'chart-data-{chart_idx}.png')
            fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            charts.append((path, f'数据图: {title[:25]}'))

    # ===== 跨文章数据对比（如果有多个文章都有百分比数据）=====
    all_pct = []
    for title, points in topic_groups.items():
        for context, val, unit in points:
            if unit == '%' and 0 < val < 100:
                all_pct.append((title[:20], val))

    if len(all_pct) >= 3:
        all_pct.sort(key=lambda x: x[1], reverse=True)
        all_pct = all_pct[:8]  # 最多8条

        fig, ax = plt.subplots(figsize=(5, 3))
        labels = [t for t, v in all_pct]
        values = [v for t, v in all_pct]

        colors = plt.cm.Blues(np.linspace(0.35, 0.85, len(values)))
        bars = ax.barh(range(len(values)), values, color=colors, height=0.55, edgecolor='none')

        ax.set_yticks(range(len(values)))
        ax.set_yticklabels(labels, fontproperties=font_prop, fontsize=7)
        ax.set_xlabel('%', fontsize=8)
        ax.set_title('关键数据指标对比', fontproperties=font_prop, fontsize=9, fontweight='bold', pad=10)
        ax.invert_yaxis()

        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{val:.0f}%', va='center', fontsize=7, color='#333')

        ax.spines['left'].set_visible(False)
        ax.tick_params(left=False, length=3, width=0.4)

        fig.tight_layout()
        path = os.path.join(output_dir, 'chart-data-cross.png')
        fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        charts.append((path, '各话题关键数据指标横向对比'))

    return charts


if __name__ == '__main__':
    import sys
    md_file = sys.argv[1] if len(sys.argv) > 1 else 'output/ai-news-2026-06-23.md'
    output_dir = os.path.dirname(md_file) or 'output'
    with open(md_file) as f:
        md = f.read()
    charts = generate_charts(md, output_dir)
    if charts:
        for path, caption in charts:
            print(f'{path} -> {caption}')
    else:
        print('No data-driven charts generated (no quantitative data found in articles)')
