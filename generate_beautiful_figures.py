#!/usr/bin/env python3
"""
Generate beautiful Nature-style figures for daily_ai_news project
using professional design principles from nature-figure skill.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Nature-style palette from api.md
PALETTE = {
    "blue_main":      "#0F4D92",
    "blue_secondary": "#3775BA",
    "green_1": "#DDF3DE",
    "green_2": "#AADCA9",
    "green_3": "#8BCF8B",
    "red_1":   "#F6CFCB",
    "red_2":   "#E9A6A1",
    "red_strong": "#B64342",
    "neutral_light": "#CFCECE",
    "neutral_mid":   "#767676",
    "neutral_dark":  "#4D4D4D",
    "neutral_black": "#272727",
    "gold":   "#FFD700",
    "teal":   "#42949E",
    "violet": "#9A4D8E",
    "magenta":"#EA84DD",
}

# Nature NMI Pastel palette for softer look
PALETTE_NMI = {
    "baseline_dark": "#484878",
    "baseline_mid":  "#7884B4",
    "baseline_soft": "#B4C0E4",
    "ours_tiny":  "#E4E4F0",
    "ours_base":  "#E4CCD8",
    "ours_large": "#F0C0CC",
    "bg_lilac": "#E0E0F0",
    "bg_aqua":  "#E0F0F0",
    "bg_peach": "#F0E0D0",
    "neutral_light": "#D8D8D8",
    "neutral_mid":   "#A8A8A8",
    "neutral_dark":  "#606060",
    "delta_up":   "#2E9E44",
    "delta_down": "#E53935",
}

# Set up matplotlib parameters for publication quality
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",     # editable text in SVG
    "pdf.fonttype": 42,         # editable TrueType text in PDF
    "font.size": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})

def save_pub_py(fig, filename):
    """Save figure in multiple formats for publication."""
    fig.savefig(f"{filename}.svg", bbox_inches="tight", facecolor="white")
    fig.savefig(f"{filename}.pdf", bbox_inches="tight", facecolor="white")
    fig.savefig(f"{filename}.png", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)

def create_architecture_diagram():
    """Create beautiful system architecture diagram."""
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Define components with Nature-style colors
    components = {
        'cron': {'pos': (6, 7), 'size': (2.2, 0.7), 'label': 'Cron Trigger\n(06:00 daily)', 
                'color': PALETTE_NMI['baseline_soft'], 'text_color': PALETTE_NMI['baseline_dark']},
        'opencode': {'pos': (6, 5.5), 'size': (2.8, 0.8), 'label': 'opencode Agent\n(LLM-driven)', 
                    'color': PALETTE['blue_main'], 'text_color': 'white'},
        'last30days': {'pos': (2.5, 4), 'size': (2, 0.7), 'label': 'last30days Skill\n(HN, GitHub, Web)', 
                      'color': PALETTE_NMI['baseline_mid'], 'text_color': 'white'},
        'tools': {'pos': (6, 4), 'size': (2.2, 0.7), 'label': 'Python Tools\n(cover, chart, report)', 
                 'color': PALETTE['teal'], 'text_color': 'white'},
        'external': {'pos': (9.5, 4), 'size': (2, 0.7), 'label': 'External APIs\n(Pollinations, WeChat)', 
                    'color': PALETTE['violet'], 'text_color': 'white'},
        'output': {'pos': (2.5, 2.5), 'size': (2, 0.7), 'label': 'Raw Data\n(Markdown)', 
                  'color': PALETTE_NMI['bg_aqua'], 'text_color': PALETTE_NMI['baseline_dark']},
        'charts': {'pos': (6, 2.5), 'size': (2, 0.7), 'label': 'Charts & Images\n(PNG)', 
                  'color': PALETTE_NMI['bg_lilac'], 'text_color': PALETTE_NMI['baseline_dark']},
        'wechat': {'pos': (9.5, 2.5), 'size': (2, 0.7), 'label': 'WeChat Official\nAccount', 
                  'color': PALETTE['red_strong'], 'text_color': 'white'},
        'database': {'pos': (6, 1), 'size': (2, 0.7), 'label': 'SQLite Database\n(daily_ai_news.db)', 
                    'color': PALETTE_NMI['bg_peach'], 'text_color': PALETTE_NMI['baseline_dark']},
    }
    
    # Draw components with rounded corners and shadows
    for comp_id, comp in components.items():
        x, y = comp['pos']
        w, h = comp['size']
        
        # Draw shadow
        shadow = FancyBboxPatch((x - w/2 + 0.05, y - h/2 - 0.05), w, h, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E0E0E0', 
                               edgecolor='none', 
                               alpha=0.3)
        ax.add_patch(shadow)
        
        # Draw main box
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h, 
                             boxstyle="round,pad=0.1", 
                             facecolor=comp['color'], 
                             edgecolor=PALETTE_NMI['neutral_mid'], 
                             linewidth=0.8)
        ax.add_patch(rect)
        
        # Add text
        ax.text(x, y, comp['label'], ha='center', va='center', 
                fontsize=8, fontweight='bold', color=comp['text_color'])
    
    # Draw arrows with Nature-style
    arrows = [
        ((6, 7), (6, 5.9)),  # cron -> opencode
        ((6, 5.1), (2.5, 4.4)),  # opencode -> last30days
        ((6, 5.1), (6, 4.4)),  # opencode -> tools
        ((6, 5.1), (9.5, 4.4)),  # opencode -> external
        ((2.5, 3.6), (2.5, 2.9)),  # last30days -> output
        ((6, 3.6), (6, 2.9)),  # tools -> charts
        ((9.5, 3.6), (9.5, 2.9)),  # external -> wechat
        ((2.5, 2.1), (6, 1.4)),  # output -> database
        ((6, 2.1), (6, 1.4)),  # charts -> database
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', color=PALETTE_NMI['neutral_dark'], 
                                  lw=1.5, connectionstyle="arc3,rad=0.1"))
    
    # Add title with Nature styling
    ax.text(6, 7.8, 'Daily AI News System Architecture', ha='center', va='center', 
            fontsize=14, fontweight='bold', color=PALETTE_NMI['baseline_dark'])
    
    # Add subtle grid background
    ax.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    return fig

def create_workflow_diagram():
    """Create beautiful workflow diagram."""
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Define workflow steps with Nature-style colors
    steps = [
        {'pos': (1.5, 4), 'label': '1. Collect\nData', 'color': PALETTE_NMI['baseline_soft']},
        {'pos': (3.5, 4), 'label': '2. Read\nRaw Files', 'color': PALETTE_NMI['baseline_mid']},
        {'pos': (5.5, 4), 'label': '3. Filter\nSensitive', 'color': PALETTE['teal']},
        {'pos': (7.5, 4), 'label': '4. Deduplicate\nContent', 'color': PALETTE['blue_main']},
        {'pos': (9.5, 4), 'label': '5. Generate\nReport', 'color': PALETTE['violet']},
        {'pos': (11.5, 4), 'label': '6. Rewrite\n(Anti-AIGC)', 'color': PALETTE['red_strong']},
        {'pos': (3, 2), 'label': '7. Generate\nCover & Charts', 'color': PALETTE_NMI['bg_aqua']},
        {'pos': (7, 2), 'label': '8. Convert to\nWeChat HTML', 'color': PALETTE_NMI['bg_lilac']},
        {'pos': (11, 2), 'label': '9. Publish\nDraft', 'color': PALETTE_NMI['bg_peach']},
    ]
    
    # Draw steps with shadows and rounded corners
    for i, step in enumerate(steps):
        x, y = step['pos']
        w, h = 1.8, 0.7
        
        # Draw shadow
        shadow = FancyBboxPatch((x - w/2 + 0.05, y - h/2 - 0.05), w, h, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E0E0E0', 
                               edgecolor='none', 
                               alpha=0.3)
        ax.add_patch(shadow)
        
        # Draw main box
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h, 
                             boxstyle="round,pad=0.1", 
                             facecolor=step['color'], 
                             edgecolor=PALETTE_NMI['neutral_mid'], 
                             linewidth=0.8)
        ax.add_patch(rect)
        
        # Add text
        ax.text(x, y, step['label'], ha='center', va='center', 
                fontsize=7, fontweight='bold', color='white')
    
    # Draw arrows with Nature styling
    arrow_pairs = [
        ((1.5, 4), (3.5, 4)),  # 1->2
        ((3.5, 4), (5.5, 4)),  # 2->3
        ((5.5, 4), (7.5, 4)),  # 3->4
        ((7.5, 4), (9.5, 4)),  # 4->5
        ((9.5, 4), (11.5, 4)),  # 5->6
        ((11.5, 4), (3, 2)),  # 6->7
        ((3, 2), (7, 2)),  # 7->8
        ((7, 2), (11, 2)),  # 8->9
    ]
    
    for start, end in arrow_pairs:
        ax.annotate('', xy=end, xytext=start,
                   arrowprops=dict(arrowstyle='->', color=PALETTE_NMI['neutral_dark'], 
                                  lw=1.5, connectionstyle="arc3,rad=0.1"))
    
    # Add title with Nature styling
    ax.text(7, 5.5, 'Daily AI News Workflow (8-Step Process)', ha='center', va='center', 
            fontsize=14, fontweight='bold', color=PALETTE_NMI['baseline_dark'])
    
    # Add subtle grid background
    ax.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    return fig

def create_resource_diagram():
    """Create beautiful resource dependency diagram."""
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Define resource categories with Nature-style colors
    categories = {
        'core': {'pos': (6, 9), 'label': 'Core System', 'color': PALETTE['blue_main']},
        'skills': {'pos': (2.5, 7), 'label': 'Skills', 'color': PALETTE['teal']},
        'python': {'pos': (6, 7), 'label': 'Python Libraries', 'color': PALETTE['violet']},
        'external': {'pos': (9.5, 7), 'label': 'External APIs', 'color': PALETTE['red_strong']},
        'data': {'pos': (2.5, 5), 'label': 'Data Storage', 'color': PALETTE_NMI['bg_aqua']},
        'tools': {'pos': (6, 5), 'label': 'Development Tools', 'color': PALETTE_NMI['bg_lilac']},
        'platform': {'pos': (9.5, 5), 'label': 'Platform', 'color': PALETTE_NMI['bg_peach']},
    }
    
    # Define resources under each category
    resources = {
        'core': [
            {'pos': (6, 8), 'label': 'opencode Agent', 'color': PALETTE_NMI['baseline_mid']},
        ],
        'skills': [
            {'pos': (2, 6.5), 'label': 'last30days', 'color': PALETTE_NMI['baseline_soft']},
            {'pos': (3, 6.5), 'label': 'wechat-article-rewrite', 'color': PALETTE_NMI['baseline_soft']},
        ],
        'python': [
            {'pos': (5, 6.5), 'label': 'matplotlib', 'color': PALETTE_NMI['baseline_soft']},
            {'pos': (6, 6.5), 'label': 'numpy', 'color': PALETTE_NMI['baseline_soft']},
            {'pos': (7, 6.5), 'label': 'Pillow', 'color': PALETTE_NMI['baseline_soft']},
        ],
        'external': [
            {'pos': (9, 6.5), 'label': 'Pollinations AI', 'color': PALETTE_NMI['baseline_soft']},
            {'pos': (10, 6.5), 'label': 'WeChat API', 'color': PALETTE_NMI['baseline_soft']},
        ],
        'data': [
            {'pos': (2, 4.5), 'label': 'SQLite', 'color': PALETTE_NMI['baseline_soft']},
            {'pos': (3, 4.5), 'label': 'Markdown Files', 'color': PALETTE_NMI['baseline_soft']},
        ],
        'tools': [
            {'pos': (5, 4.5), 'label': 'Python 3.12', 'color': PALETTE_NMI['baseline_soft']},
            {'pos': (6, 4.5), 'label': 'Node.js v24', 'color': PALETTE_NMI['baseline_soft']},
            {'pos': (7, 4.5), 'label': 'Bash', 'color': PALETTE_NMI['baseline_soft']},
        ],
        'platform': [
            {'pos': (9, 4.5), 'label': 'Linux', 'color': PALETTE_NMI['baseline_soft']},
            {'pos': (10, 4.5), 'label': 'WeChat Official Account', 'color': PALETTE_NMI['baseline_soft']},
        ],
    }
    
    # Draw category boxes with shadows
    for cat_id, cat in categories.items():
        x, y = cat['pos']
        w, h = 2.4, 0.6
        
        # Draw shadow
        shadow = FancyBboxPatch((x - w/2 + 0.05, y - h/2 - 0.05), w, h, 
                               boxstyle="round,pad=0.1", 
                               facecolor='#E0E0E0', 
                               edgecolor='none', 
                               alpha=0.3)
        ax.add_patch(shadow)
        
        # Draw main box
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h, 
                             boxstyle="round,pad=0.1", 
                             facecolor=cat['color'], 
                             edgecolor=PALETTE_NMI['neutral_mid'], 
                             linewidth=0.8)
        ax.add_patch(rect)
        
        # Add text
        ax.text(x, y, cat['label'], ha='center', va='center', 
                fontsize=9, fontweight='bold', color='white')
    
    # Draw resource items with shadows
    for cat_id, items in resources.items():
        for item in items:
            x, y = item['pos']
            w, h = 1.4, 0.4
            
            # Draw shadow
            shadow = FancyBboxPatch((x - w/2 + 0.03, y - h/2 - 0.03), w, h, 
                                   boxstyle="round,pad=0.05", 
                                   facecolor='#E0E0E0', 
                                   edgecolor='none', 
                                   alpha=0.3)
            ax.add_patch(shadow)
            
            # Draw main box
            rect = FancyBboxPatch((x - w/2, y - h/2), w, h, 
                                 boxstyle="round,pad=0.05", 
                                 facecolor=item['color'], 
                                 edgecolor=PALETTE_NMI['neutral_light'], 
                                 linewidth=0.5)
            ax.add_patch(rect)
            
            # Add text
            ax.text(x, y, item['label'], ha='center', va='center', 
                    fontsize=7, color=PALETTE_NMI['baseline_dark'])
    
    # Draw connecting lines with Nature styling
    for cat_id, items in resources.items():
        cat_pos = categories[cat_id]['pos']
        for item in items:
            item_pos = item['pos']
            ax.plot([cat_pos[0], item_pos[0]], [cat_pos[1]-0.3, item_pos[1]+0.2], 
                   color=PALETTE_NMI['neutral_light'], linewidth=0.8, linestyle='-', alpha=0.6)
    
    # Add title with Nature styling
    ax.text(6, 9.7, 'Daily AI News Resource Dependencies', ha='center', va='center', 
            fontsize=14, fontweight='bold', color=PALETTE_NMI['baseline_dark'])
    
    # Add subtle grid background
    ax.set_facecolor('#FAFAFA')
    
    plt.tight_layout()
    return fig

def save_figures():
    """Save all figures in multiple formats."""
    # Create figures
    fig_arch = create_architecture_diagram()
    fig_workflow = create_workflow_diagram()
    fig_resource = create_resource_diagram()
    
    # Save architecture diagram
    save_pub_py(fig_arch, '/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/architecture_diagram')
    
    # Save workflow diagram
    save_pub_py(fig_workflow, '/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/workflow_diagram')
    
    # Save resource diagram
    save_pub_py(fig_resource, '/root/RD/daily_skill_notify/daily_ai_news/软件著作权申请资料/resource_diagram')
    
    print("All figures saved successfully:")
    print("- architecture_diagram.{svg,pdf,png}")
    print("- workflow_diagram.{svg,pdf,png}")
    print("- resource_diagram.{svg,pdf,png}")

if __name__ == "__main__":
    save_figures()