#!/bin/bash
# 每日AI热点新闻 - 由 opencode agent 执行
cd /root/RD/daily_skill_notify/daily_ai_news
mkdir -p output

export LAST30DAYS_MEMORY_DIR="$(pwd)/output"

# 使用 opencode run 调用 agent 执行完整流程
opencode run \
  "$(cat AGENTS.md)" \
  --dir "$(pwd)" \
  2>&1 | tee -a "logs/$(date +%Y-%m-%d).log"
