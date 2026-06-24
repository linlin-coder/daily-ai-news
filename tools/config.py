#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""从 .env 文件加载配置"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


def load_env():
    """加载 .env 文件到环境变量"""
    if not ENV_FILE.exists():
        raise FileNotFoundError(f".env not found at {ENV_FILE}")

    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip()

    return dict(os.environ)


def get_wechat_config():
    """获取微信公众号配置"""
    env = load_env()
    return {
        "appid": env.get("WECHAT_APPID", ""),
        "appsecret": env.get("WECHAT_APPSECRET", ""),
    }


if __name__ == "__main__":
    env = load_env()
    print(f"[config] Loaded .env from {ENV_FILE}")
    print(f"  WECHAT_APPID: {env.get('WECHAT_APPID', 'NOT SET')[:8]}...")
