# -*- coding: utf-8 -*-
"""
LLM Provider Configuration & Discovery.
"""

import os
import urllib.request
from typing import Dict, Any, Tuple, Optional
from openai import OpenAI


def load_dotenv():
    """轻量自动加载 .env 配置文件，零外部依赖"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

load_dotenv()


def is_ollama_alive(url: str = "http://localhost:11434") -> bool:
    """探测本地是否运行了 Ollama 服务"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OpenCoze"})
        with urllib.request.urlopen(req, timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_llm_client() -> Tuple[Optional[OpenAI], str, str]:
    """
    智能解析最适合的 LLM 运行时：
    返回: (client, default_model, provider_name)
    """
    # 1. 智谱 GLM-4-Flash (官方永久免费首选)
    if os.getenv("ZHIPU_API_KEY"):
        client = OpenAI(
            api_key=os.getenv("ZHIPU_API_KEY"),
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )
        return client, "glm-4-flash", "智谱 AI (GLM-4-Flash 永久免费)"

    # 2. DeepSeek 官方
    if os.getenv("DEEPSEEK_API_KEY"):
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("BASE_URL", "https://api.deepseek.com")
        )
        return client, "deepseek-chat", "DeepSeek 官方 API"

    # 3. OpenAI
    if os.getenv("OPENAI_API_KEY"):
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("BASE_URL", "https://api.openai.com/v1")
        )
        return client, "gpt-4o-mini", "OpenAI (gpt-4o-mini)"

    # 4. 本地 Ollama (离线免费)
    if is_ollama_alive():
        client = OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )
        return client, "qwen2.5:7b", "本地 Ollama (离线免密)"

    # 5. 内置离线 Mock 引擎
    return None, "mock-agent", "内置 Mock 仿真引擎 (离线演示)"
