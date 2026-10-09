# -*- coding: utf-8 -*-
"""
Example: Run a pre-built workflow programmatically via Python SDK.
"""

import os
import sys
import asyncio

# 注入项目根路径并设置控制台 UTF-8 输出
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from opencoze.engine import WorkflowEngine
from opencoze.templates import COMPETITOR_ANALYSIS_WORKFLOW
from opencoze.config import get_llm_client


async def main():
    print("=== OpenCoze 工作流 SDK 演示 ===")
    
    # 1. 自动发现大模型客户端
    client, model, provider = get_llm_client()
    print(f"当前已激活模型供应商: {provider}")

    # 2. 实例化工作流引擎
    engine = WorkflowEngine(COMPETITOR_ANALYSIS_WORKFLOW, llm_client=client)

    # 3. 准备启动入参
    inputs = {
        "topic": "企业级低代码 AI 智能体编排平台",
        "target": "Dify vs Coze"
    }

    # 4. 执行工作流
    print("\n正在并发调度并执行工作流...")
    result = await engine.run(inputs)

    # 5. 查看执行报告
    print("\n--- 全链路 Trace 监控 ---")
    for nid, trace in result["traces"].items():
        print(f"[{trace['node_type'].upper()}] 节点: {nid} | 状态: {trace['status']} | 耗时: {trace['duration_ms']}ms")

    print("\n--- 最终产出结果 ---")
    print(result["result"])


if __name__ == "__main__":
    asyncio.run(main())
