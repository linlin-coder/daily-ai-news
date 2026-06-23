# 每日AI热点新闻 (Daily AI News)

每日自动追踪AI领域最大热点（科研、工具、产业、应用），偏生物医药方向，生成中文报告推送到微信公众号。

## 架构

```
cron (每天8:00) 
  → opencode run (非交互模式)
    → agent 执行研究流程
      → HN/GitHub API 采集数据
      → 生成中文报告
      → 生成微信HTML
      → 推送到微信公众号
```

## 手动执行

```bash
# 方式1：通过 opencode run（推荐，agent会执行完整流程）
opencode run "执行每日AI热点新闻研究并推送到微信" --dir /root/RD/daily_skill_notify/daily_ai_news

# 方式2：直接运行脚本（仅生成报告，不推送微信）
cd /root/RD/daily_skill_notify/daily_ai_news
python3.12 -c "
import sys; sys.path.insert(0, 'tools')
from research import research_ai_hotspots
from report import generate_chinese_report, markdown_to_wechat_html
results = research_ai_hotspots(days_back=1)
title, digest, report = generate_chinese_report(results)
html = markdown_to_wechat_html(report)
print(report[:500])
"
```

## 配置

微信配置自动从 `../DailyArticlePush/pipeline.config.yaml` 读取，写入 `.env`。

### IP白名单

微信公众号后台 → 开发 → 基本配置 → IP白名单 → 添加: `211.159.179.85`

## 文件结构

```
daily_ai_news/
├── AGENTS.md           # Agent指令（opencode run时读取）
├── run_daily.sh        # cron运行脚本（调用opencode run）
├── .env                # 配置（自动生成，不入git）
├── .gitignore
├── README.md
├── tools/
│   ├── config.py       # 配置读取（pipeline.config.yaml → .env）
│   ├── research.py     # 研究工具（HN + GitHub API）
│   ├── report.py       # 报告生成（中文 + 微信HTML）
│   └── wechat.py       # 微信公众号API
├── output/             # 报告输出
└── logs/               # 运行日志
```

## 数据源

- **Hacker News** (Algolia API) - AI热点讨论
- **GitHub API** - 趋势AI项目
- 自动去重、按热度排序

## 主题方向

- AI科研突破（论文、模型、算法）
- AI工具发布（开源项目、产品更新）
- AI产业动态（融资、合作、应用）
- **偏向**: AI药物发现、医疗AI、蛋白质设计、基因组学
