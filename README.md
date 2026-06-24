# 每日AI热点新闻 (Daily AI News)

每日自动追踪AI领域最大热点，生成中文深度报告推送到微信公众号。

## 架构

```
cron (每天06:00)
  → opencode run (agent 驱动)
    → last30days skill 采集数据 (HN / GitHub / Web)
    → 政治敏感过滤
    → 生成深度中文报告
    → 生成封面图 (Pollinations AI)
    → 生成数据图表 (matplotlib, 仅当有数据时)
    → 生成微信HTML + 上传图片
    → 创建微信草稿
    → 保存数据到 SQLite
```

## 手动执行

```bash
# 完整流程（推荐）
bash /root/RD/daily_skill_notify/daily_ai_news/run_daily.sh

# 或直接 opencode run
cd /root/RD/daily_skill_notify/daily_ai_news
opencode run "$(cat AGENTS.md)" --dir "$(pwd)"
```

## 配置

配置从项目根目录 `.env` 文件读取：

```
WECHAT_APPID=...
WECHAT_APPSECRET=...
```

### IP白名单

微信公众号后台 → 开发 → 基本配置 → IP白名单 → 添加: `211.159.179.85`

## 文件结构

```
daily_ai_news/
├── AGENTS.md           # Agent 执行指令
├── run_daily.sh        # cron 运行脚本
├── opencode.json       # opencode 权限配置
├── .env                # 微信配置（不入 git）
├── .gitignore
├── tools/
│   ├── config.py       # .env 配置加载
│   ├── wechat.py       # 微信公众号 API
│   ├── cover.py        # Pollinations AI 封面生成
│   ├── report.py       # Markdown → 微信 HTML
│   ├── chart.py        # matplotlib 数据图表
│   └── db.py           # SQLite 数据存储
├── data/               # SQLite 数据库（不入 git）
├── output/             # 报告、图表、封面
└── logs/               # 运行日志
```

## 数据源

- **last30days skill** — 综合采集 Hacker News / GitHub / Web
- 政治敏感内容自动过滤
- 数据自动存入 SQLite 便于历史查询
