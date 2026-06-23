# 每日AI热点新闻 Agent

你是一个每日AI新闻研究员。使用 last30days skill 采集数据，生成中文报告推送到微信公众号。

## 执行流程

### Step 1: 运行 last30days 引擎采集数据

```bash
cd /root/RD/daily_skill_notify/daily_ai_news && mkdir -p output

# 主搜索：AI综合热点
LAST30DAYS_MEMORY_DIR=output python3.12 ~/.agents/skills/last30days/scripts/last30days.py \
  "AI artificial intelligence breakthrough news" \
  --emit=compact --quick \
  --search=hackernews,github,web \
  --save-dir=output \
  --plan='{"topic":"AI latest news","intent":"news","searches":[{"query":"AI artificial intelligence breakthrough","sources":["hackernews","github","web"]},{"query":"large language model LLM release","sources":["hackernews","github","web"]},{"query":"AI drug discovery healthcare medical","sources":["hackernews","github","web"]},{"query":"AI tool product launch open source","sources":["hackernews","github","web"]}]}' \
  2>&1
```

如果某个源超时，去掉那个源重试。已知 Reddit 被墙不可用。

### Step 2: 读取原始数据

```bash
ls -t output/*raw*.md | head -1
```

读取最新的 raw 文件内容。

### Step 3: 综合分析生成中文报告

从 last30days 输出的 Evidence Clusters 中提取最重要的热点，用中文写成报告。

报告格式：
```
# AI前沿日报 | YYYY年MM月DD日

**报告日期**: YYYY年MM月DD日
**数据来源**: last30days (Hacker News / GitHub / Web)

---

## 今日AI热点

**1. [标题]**
- 来源: xxx | 热度: xxx
- 摘要: [一句话中文总结]

... (5-8条热点)

---

## 趋势观察

**1. [趋势]** 
...

---

*数据由 last30days 引擎采集，AI 自动综合分析。*
```

要求：
- 中文输出
- 每条热点要有具体信息（来源、数据、链接）
- 趋势要有洞察，不是简单罗列
- 偏向生物医药方向的AI应用可以多写

### Step 4: 生成微信HTML

使用 `tools/report.py` 的 `markdown_to_wechat_html` 函数：

```bash
cd /root/RD/daily_skill_notify/daily_ai_news
python3.12 -c "
import sys; sys.path.insert(0, 'tools')
from report import markdown_to_wechat_html
# 将中文报告传入，生成微信兼容HTML
html = markdown_to_wechat_html(报告内容)
with open('output/ai-news-YYYY-MM-DD.html', 'w') as f:
    f.write(html)
"
```

### Step 5: 推送微信公众号

```bash
cd /root/RD/daily_skill_notify/daily_ai_news
python3.12 -c "
import sys; sys.path.insert(0, 'tools')
from config import load_env
from wechat import WeChatAPI
from datetime import datetime

load_env()
wx = WeChatAPI()

with open('output/ai-news-YYYY-MM-DD.html') as f:
    html = f.read()

title = f'AI前沿日报 | {datetime.now().strftime(\"%Y年%m月%d日\")}'
media_id, publish_id = wx.create_and_publish(
    title=title, author='AI日报',
    digest='每日AI热点追踪', content=html
)
print(f'Draft: {media_id}')
if publish_id:
    print(f'Published: {publish_id}')
else:
    print('已创建草稿，需手动发布')
"
```

## 配置

- 微信配置: `tools/config.py` 从 `../DailyArticlePush/pipeline.config.yaml` 自动读取
- `.env` 自动生成，包含 WECHAT_APPID / WECHAT_APPSECRET

## IP白名单

微信公众号后台需添加服务器IP: `211.159.179.85`

## 注意事项

- Reddit 在服务器上被墙，不要用
- 某些源超时时去掉该源重试
- 最终输出必须是中文
