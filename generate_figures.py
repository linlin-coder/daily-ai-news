#!/usr/bin/env python3
"""
Generate architecture, workflow, and resource diagrams for daily_ai_news project
for software copyright application materials.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Set up matplotlib parameters for publication quality
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
})

def create_architecture_diagram():
    """Create system architecture diagram."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Define components
    components = {
        'cron': {'pos': (5, 7), 'size': (2, 0.8), 'label': 'Cron Trigger\n(06:00 daily)', 'color': '#E8F4FD'},
        'opencode': {'pos': (5, 5.5), 'size': (2.5, 0.8), 'label': 'opencode Agent\n(LLM-driven)', 'color': '#D4EDDA'},
        'last30days': {'pos': (2, 4), 'size': (2, 0.8), 'label': 'last30days Skill\n(HN, GitHub, Web)', 'color': '#FFF3CD'},
        'tools': {'pos': (5, 4), 'size': (2, 0.8), 'label': 'Python Tools\n(cover, chart, report, wechat)', 'color': '#F8D7DA'},
        'external': {'pos': (8, 4), 'size': (2, 0.8), 'label': 'External APIs\n(Pollinations, WeChat)', 'color': '#E2E3E5'},
        'output': {'pos': (2, 2.5), 'size': (2, 0.8), 'label': 'Raw Data\n(Markdown)', 'color': '#D1ECF1'},
        'charts': {'pos': (5, 2.5), 'size': (2, 0.8), 'label': 'Charts & Images\n(PNG)', 'color': '#D4EDDA'},
        'wechat': {'pos': (8, 2.5), 'size': (2, 0.8), 'label': 'WeChat Official\nAccount', 'color': '#F8D7DA'},
        'database': {'pos': (5, 1), 'size': (2, 0.8), 'label': 'SQLite Database\n(daily_ai_news.db)', 'color': '#FFF3CD'},
    }
    
    # Draw components
    for comp_id, comp in components.items():
        x, y = comp['pos']
        w, h = comp['size']
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h, 
                             boxstyle="round,pad=0.1", 
                             facecolor=comp['color'], 
                             edgecolor='black', 
                             linewidth=0.8)
        ax.add_patch(rect)
        ax.text(x, y, comp['label'], ha='center', va='center', fontsize=7, fontweight='bold')
    
    # Draw arrows
    arrows = [
        ((5, 7), (5, 5.9)),  # cron -> opencode
        ((5, 5.1), (2, 4.4)),  # opencode -> last30days
        ((5, 5.1), (5, 4.4)),  # opencode -> tools
        ((5, 5.1), (8, 4.4)),  # opencode -> external
        ((2, 3.6), (2, 2.9)),  # last30days -> output
        ((5, 3.6), (5, 2.9)),  # tools -> charts
        ((8, 3.6), (8, 2.9)),  # external -> wechat
        ((2, 2.1), (5, 1.4)),  # output -> database
        ((5, 2.1), (5, 1.4)),  # charts -> database
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
    
    # Add title
    ax.text(5, 7.8, 'Daily AI News System Architecture', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_workflow_diagram():
    """Create workflow diagram showing 8-step process."""
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Define workflow steps
    steps = [
        {'pos': (1, 4), 'label': '1. Collect\nData', 'color': '#E8F4FD'},
        {'pos': (3, 4), 'label': '2. Read\nRaw Files', 'color': '#D4EDDA'},
        {'pos': (5, 4), 'label': '3. Filter\nSensitive Content', 'color': '#FFF3CD'},
        {'pos': (7, 4), 'label': '4. Deduplicate\nContent', 'color': '#F8D7DA'},
        {'pos': (9, 4), 'label': '5. Generate\nReport', 'color': '#E2E3E5'},
        {'pos': (11, 4), 'label': '6. Rewrite\n(Anti-AIGC)', 'color': '#D1ECF1'},
        {'pos': (2, 2), 'label': '7. Generate\nCover & Charts', 'color': '#D4EDDA'},
        {'pos': (6, 2), 'label': '8. Convert to\nWeChat HTML', 'color': '#FFF3CD'},
        {'pos': (10, 2), 'label': '9. Publish\nDraft', 'color': '#F8D7DA'},
    ]
    
    # Draw steps
    for i, step in enumerate(steps):
        x, y = step['pos']
        rect = FancyBboxPatch((x - 0.8, y - 0.4), 1.6, 0.8, 
                             boxstyle="round,pad=0.1", 
                             facecolor=step['color'], 
                             edgecolor='black', 
                             linewidth=0.8)
        ax.add_patch(rect)
        ax.text(x, y, step['label'], ha='center', va='center', fontsize=7, fontweight='bold')
    
    # Draw arrows between steps
    arrow_pairs = [
        ((1, 4), (3, 4)),  # 1->2
        ((3, 4), (5, 4)),  # 2->3
        ((5, 4), (7, 4)),  # 3->4
        ((7, 4), (9, 4)),  # 4->5
        ((9, 4), (11, 4)),  # 5->6
        ((11, 4), (2, 2)),  # 6->7
        ((2, 2), (6, 2)),  # 7->8
        ((6, 2), (10, 2)),  # 8->9
    ]
    
    for start, end in arrow_pairs:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.2))
    
    # Add title
    ax.text(6, 5.5, 'Daily AI News Workflow (8-Step Process)', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_resource_diagram():
    """Create resource dependency diagram."""
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define resource categories
    categories = {
        'core': {'pos': (5, 8), 'label': 'Core System', 'color': '#E8F4FD'},
        'skills': {'pos': (2, 6), 'label': 'Skills', 'color': '#D4EDDA'},
        'python': {'pos': (5, 6), 'label': 'Python Libraries', 'color': '#FFF3CD'},
        'external': {'pos': (8, 6), 'label': 'External APIs', 'color': '#F8D7DA'},
        'data': {'pos': (2, 4), 'label': 'Data Storage', 'color': '#E2E3E5'},
        'tools': {'pos': (5, 4), 'label': 'Development Tools', 'color': '#D1ECF1'},
        'platform': {'pos': (8, 4), 'label': 'Platform', 'color': '#D4EDDA'},
    }
    
    # Define resources under each category
    resources = {
        'core': [
            {'pos': (5, 7), 'label': 'opencode Agent', 'color': '#D4EDDA'},
        ],
        'skills': [
            {'pos': (1.5, 5.5), 'label': 'last30days', 'color': '#D4EDDA'},
            {'pos': (2.5, 5.5), 'label': 'wechat-article-rewrite', 'color': '#D4EDDA'},
        ],
        'python': [
            {'pos': (4, 5.5), 'label': 'matplotlib', 'color': '#FFF3CD'},
            {'pos': (5, 5.5), 'label': 'numpy', 'color': '#FFF3CD'},
            {'pos': (6, 5.5), 'label': 'Pillow', 'color': '#FFF3CD'},
        ],
        'external': [
            {'pos': (7.5, 5.5), 'label': 'Pollinations AI', 'color': '#F8D7DA'},
            {'pos': (8.5, 5.5), 'label': 'WeChat API', 'color': '#F8D7DA'},
        ],
        'data': [
            {'pos': (1.5, 3.5), 'label': 'SQLite', 'color': '#E2E3E5'},
            {'pos': (2.5, 3.5), 'label': 'Markdown Files', 'color': '#E2E3E5'},
        ],
        'tools': [
            {'pos': (4, 3.5), 'label': 'Python 3.12', 'color': '#D1ECF1'},
            {'pos': (5, 3.5), 'label': 'Node.js v24', 'color': '#D1ECF1'},
            {'pos': (6, 3.5), 'label': 'Bash', 'color': '#D1ECF1'},
        ],
        'platform': [
            {'pos': (7.5, 3.5), 'label': 'Linux', 'color': '#D4EDDA'},
            {'pos': (8.5, 3.5), 'label': 'WeChat Official Account', 'color': '#D4EDDA'},
        ],
    }
    
    # Draw category boxes
    for cat_id, cat in categories.items():
        x, y = cat['pos']
        rect = FancyBboxPatch((x - 1.2, y - 0.3), 2.4, 0.6, 
                             boxstyle="round,pad=0.1", 
                             facecolor=cat['color'], 
                             edgecolor='black', 
                             linewidth=0.8)
        ax.add_patch(rect)
        ax.text(x, y, cat['label'], ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Draw resource items
    for cat_id, items in resources.items():
        for item in items:
            x, y = item['pos']
            rect = FancyBboxPatch((x - 0.7, y - 0.2), 1.4, 0.4, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=item['color'], 
                                 edgecolor='gray', 
                                 linewidth=0.5)
            ax.add_patch(rect)
            ax.text(x, y, item['label'], ha='center', va='center', fontsize=6)
    
    # Draw connecting lines
    for cat_id, items in resources.items():
        cat_pos = categories[cat_id]['pos']
        for item in items:
            item_pos = item['pos']
            ax.plot([cat_pos[0], item_pos[0]], [cat_pos[1]-0.3, item_pos[1]+0.2], 
                   color='gray', linewidth=0.5, linestyle='--')
    
    # Add title
    ax.text(5, 9.5, 'Daily AI News Resource Dependencies', ha='center', va='center', 
            fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig

def save_figures():
    """Save all figures in multiple formats."""
    # Create figures
    fig_arch = create_architecture_diagram()
    fig_workflow = create_workflow_diagram()
    fig_resource = create_resource_diagram()
    
    # Save architecture diagram
    fig_arch.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/architecture_diagram.svg', 
                    bbox_inches='tight')
    fig_arch.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/architecture_diagram.pdf', 
                    bbox_inches='tight')
    fig_arch.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/architecture_diagram.png', 
                    dpi=300, bbox_inches='tight')
    
    # Save workflow diagram
    fig_workflow.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/workflow_diagram.svg', 
                        bbox_inches='tight')
    fig_workflow.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/workflow_diagram.pdf', 
                        bbox_inches='tight')
    fig_workflow.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/workflow_diagram.png', 
                        dpi=300, bbox_inches='tight')
    
    # Save resource diagram
    fig_resource.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/resource_diagram.svg', 
                        bbox_inches='tight')
    fig_resource.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/resource_diagram.pdf', 
                        bbox_inches='tight')
    fig_resource.savefig('/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/resource_diagram.png', 
                        dpi=300, bbox_inches='tight')
    
    print("All figures saved successfully:")
    print("- architecture_diagram.{svg,pdf,png}")
    print("- workflow_diagram.{svg,pdf,png}")
    print("- resource_diagram.{svg,pdf,png}")

if __name__ == "__main__":
    save_figures()