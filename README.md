# 每日AI热点新闻 (Daily AI News)

每日自动追踪AI领域最大热点，生成中文深度报告推送到微信公众号。

## 架构

```
cron (每天06:00)
  → opencode run (agent 驱动)
    → last30days skill 采集数据 (HN / GitHub / Web)
    → 政治敏感过滤
    → 内容去重（7天内已覆盖跳过）
    → 生成深度中文报告（5种类型轮换）
    → 去AI化改写（wechat-article-rewrite skill）
    → 生成封面图 (Pollinations AI)
    → 生成数据图表 (matplotlib, 仅当有数据时)
    → 生成微信HTML + 上传图片
    → 创建微信草稿
    → 保存数据到 SQLite
```

## 内容质量保障

为避免微信"低创作度"限流，agent 会：
- **5种报告类型轮换**：深度解读、对比评测、趋势观点、实操教程、槽点合集
- **原创分析占比 ≥ 40%**：不是搬运新闻，而是加入个人分析、判断、建议
- **标题多样化**：每篇独立标题，不使用"AI前沿日报"等泛化模板
- **内容去重**：7天内已覆盖的话题自动跳过
- **去AI化改写**：每篇报告经过 wechat-article-rewrite skill 改写，消除AI痕迹

## 依赖安装

### 1. 运行时环境

```bash
# Python 3.12+
python3 --version  # 需要 3.12+

# Node.js (opencode 依赖)
# 推荐使用 nvm 安装
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 24
node --version  # 需要 18+
```

### 2. opencode

```bash
npm install -g opencode
opencode --version
```

文档: https://opencode.ai

### 3. last30days skill

```bash
# 克隆 skill 到 ~/.agents/skills/
mkdir -p ~/.agents/skills
git clone https://github.com/mvanhorn/last30days-skill.git ~/.agents/skills/last30days
```

文档: https://github.com/mvanhorn/last30days-skill

### 4. Python 依赖

```bash
pip install matplotlib numpy Pillow
```

| 包 | 用途 |
|---|------|
| `matplotlib` | 数据图表生成 |
| `numpy` | 数值计算 |
| `Pillow` | 图片处理 |

> `sqlite3` 为 Python 内置模块，无需额外安装。

### 5. 系统字体（中文图表）

```bash
# Ubuntu/Debian
apt install fonts-wqy-zenhei

# CentOS/RHEL
yum install wqy-zenhei-fonts
```

## 项目配置

### 环境变量

在项目根目录创建 `.env` 文件：

```bash
cd daily_ai_news
cat > .env << 'EOF'
WECHAT_APPID=你的公众号AppID
WECHAT_APPSECRET=你的公众号AppSecret
EOF
```

### 微信公众号设置

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 开发 → 基本配置 → IP白名单 → 添加: `你的服务器IP`
3. 开发 → 基本配置 → 获取 AppID 和 AppSecret

### opencode 权限

项目已包含 `opencode.json`，配置了访问 skills 目录的权限，无需额外设置。

### 定时任务

```bash
# 添加到 crontab（每天早上6点执行）
crontab -e
# 添加这行：
0 6 * * * /root/RD/daily_skill_notify/daily_ai_news/run_daily.sh
```

## 手动执行

```bash
# 完整流程（推荐）
bash run_daily.sh

# 或直接 opencode run
cd daily_ai_news
opencode run "$(cat AGENTS.md)" --dir "$(pwd)"
```

## 文件结构

```
daily_ai_news/
├── AGENTS.md           # Agent 执行指令
├── run_daily.sh        # cron 运行脚本
├── opencode.json       # opencode 权限配置
├── .env                # 微信配置（不入 git）
├── .gitignore
├── LICENSE             # MIT
├── README.md
├── tools/
│   ├── config.py       # .env 配置加载
│   ├── wechat.py       # 微信公众号 API
│   ├── cover.py        # Pollinations AI 封面生成
│   ├── report.py       # Markdown → 微信 HTML
│   ├── chart.py        # matplotlib 数据图表
│   └── db.py           # SQLite 数据存储
├── data/               # SQLite 数据库（不入 git）
├── output/             # 报告、图表、封面（不入 git）
└── logs/               # 运行日志（不入 git）
```

## 数据源

- **last30days skill** — 综合采集 Hacker News / GitHub / Web
- 政治敏感内容自动过滤
- 数据自动存入 SQLite 便于历史查询

## License

MIT
