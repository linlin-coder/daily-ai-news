#!/usr/bin/env python3.12
# -*- coding: UTF-8 -*-
"""从 pipeline.config.yaml 读取配置并导出为环境变量"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT.parent / "DailyArticlePush" / "pipeline.config.yaml"
ENV_FILE = PROJECT_ROOT / ".env"


def load_config():
    """读取 YAML 配置"""
    try:
        import yaml
    except ImportError:
        # 简单 YAML 解析（无依赖）
        return _simple_yaml_parse(CONFIG_FILE)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _simple_yaml_parse(filepath):
    """简单 YAML 解析（不依赖 PyYAML）"""
    config = {}
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_section = None
    current_subsection = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if value:
                # 去掉引号
                value = value.strip("'\"")
                if current_section and current_subsection:
                    config.setdefault(current_section, {}).setdefault(current_subsection, {})[key] = value
                elif current_section:
                    config.setdefault(current_section, {})[key] = value
            else:
                # 这是一个 section
                if indent == 0:
                    current_section = key
                    current_subsection = None
                elif indent <= 4:
                    current_subsection = key

    return config


def export_to_env(config):
    """导出配置到 .env 文件"""
    env_lines = []
    env_lines.append("# Auto-generated from pipeline.config.yaml")
    env_lines.append(f"# Generated at: {__import__('datetime').datetime.now().isoformat()}")
    env_lines.append("")

    # 微信配置
    wx = config.get("Pusher", {}).get("WeiXinPusher", {})
    if wx:
        env_lines.append("# WeChat Official Account")
        env_lines.append(f"WECHAT_APPID={wx.get('AppID', '')}")
        env_lines.append(f"WECHAT_APPSECRET={wx.get('AppSecret', '')}")
        env_lines.append("")

    # LLM 配置
    llm = config.get("LLM", {}).get("openrouter", {})
    if llm:
        env_lines.append("# LLM (OpenRouter)")
        env_lines.append(f"OPENROUTER_API_KEY={llm.get('API_KEY', '')}")
        env_lines.append(f"OPENROUTER_PROVIDER={llm.get('provider', '')}")
        env_lines.append("")

    # 翻译配置
    trans = config.get("Translation", {})
    if trans:
        chatgpt = trans.get("ChatGPT", {})
        if chatgpt:
            env_lines.append("# Translation (ChatGPT)")
            env_lines.append(f"TRANSLATE_API_KEY={chatgpt.get('api_key', '')}")
            env_lines.append(f"TRANSLATE_API_URL={chatgpt.get('url', '')}")
            env_lines.append("")

    # 数据库配置
    db = config.get("DataBase", {})
    if db:
        mongo = db.get("mongoDB", {})
        if mongo:
            env_lines.append("# MongoDB")
            env_lines.append(f"MONGO_HOST={mongo.get('HOST', '')}")
            env_lines.append(f"MONGO_PORT={mongo.get('PORT', '')}")
            env_lines.append(f"MONGO_DB={mongo.get('NAME', '')}")
            env_lines.append("")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(env_lines))

    print(f"[config] Exported to {ENV_FILE}")
    return ENV_FILE


def load_env():
    """加载 .env 文件到环境变量"""
    if not ENV_FILE.exists():
        print(f"[config] .env not found, generating from pipeline.config.yaml")
        config = load_config()
        export_to_env(config)

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
    config = load_config()
    print("[config] Loaded config:")
    for section, values in config.items():
        if isinstance(values, dict):
            print(f"  {section}:")
            for k, v in values.items():
                if isinstance(v, dict):
                    print(f"    {k}:")
                    for kk, vv in v.items():
                        print(f"      {kk}: {vv[:10]}..." if len(str(vv)) > 10 else f"      {kk}: {vv}")
                else:
                    print(f"    {k}: {v[:10]}..." if len(str(v)) > 10 else f"    {k}: {v}")
        else:
            print(f"  {section}: {values}")

    export_to_env(config)
