#!/bin/bash
# 每日AI热点新闻 - 由 opencode agent 驱动
set -euo pipefail

PROJECT_DIR="/root/RD/daily_skill_notify/daily_ai_news"
LOG_DIR="${PROJECT_DIR}/logs"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="${LOG_DIR}/${TODAY}.log"

mkdir -p "${LOG_DIR}" "${PROJECT_DIR}/output"

cd "${PROJECT_DIR}"

exec >> "${LOG_FILE}" 2>&1
echo "=========================================="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Daily AI News cron start"
echo "=========================================="

export LAST30DAYS_MEMORY_DIR="${PROJECT_DIR}/output"
export PATH="/root/.nvm/versions/node/v24.13.0/bin:$PATH"

# opencode run 驱动 agent 执行 AGENTS.md 中的完整流程
opencode run "$(cat AGENTS.md)" --dir "${PROJECT_DIR}"

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Done successfully"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Failed with exit code $EXIT_CODE"
fi
