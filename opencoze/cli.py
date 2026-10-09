# -*- coding: utf-8 -*-
"""
OpenCoze CLI: Command Line Tool for running workflows directly in terminal.
"""

import sys
import json
import asyncio
import argparse
from typing import Dict, Any

from opencoze.engine import WorkflowEngine
from opencoze.config import get_llm_client
from opencoze.templates import BUILTIN_TEMPLATES

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


async def execute_cli(workflow_dsl: Dict[str, Any], inputs: Dict[str, Any]):
    client, model, provider = get_llm_client()
    print(f"\n🚀 [OpenCoze CLI] 正在执行工作流: {workflow_dsl.get('name', '未命名工作流')}")
    print(f"🔗 模型运行时: {provider} ({model})")
    print(f"📥 运行入参: {json.dumps(inputs, ensure_ascii=False)}")
    print("-" * 65)

    engine = WorkflowEngine(workflow_dsl, llm_client=client)
    res = await engine.run(inputs)

    print("\n🔍 【节点执行追踪 (Execution Traces)】:")
    for nid, t in res["traces"].items():
        status_icon = "🟢" if t["status"] == "SUCCESS" else ("🟡" if t["status"] == "SKIPPED" else "🔴")
        print(f"  {status_icon} [{t['node_type'].upper()}] {nid:<18} -> 状态: {t['status']:<8} 耗时: {t['duration_ms']}ms Tokens: {t['tokens']}")

    print("\n" + "=" * 65)
    print("📑 【工作流最终输出结果 (Final Output)】:")
    print("=" * 65)
    print(res["result"])
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="OpenCoze AI Workflow CLI Runner")
    parser.add_argument("workflow", help="模板名称 (如 competitor_analysis, ticket_router) 或本地 JSON 路径")
    parser.add_argument("--inputs", "-i", default="{}", help="JSON 格式运行入参字符串")

    args = parser.parse_args()

    # 1. 加载 DSL
    if args.workflow in BUILTIN_TEMPLATES:
        dsl = BUILTIN_TEMPLATES[args.workflow]
    else:
        try:
            with open(args.workflow, "r", encoding="utf-8") as f:
                dsl = json.load(f)
        except Exception as e:
            print(f"❌ 无法加载工作流定义: {e}")
            sys.exit(1)

    # 2. 解析参数
    try:
        inputs = json.loads(args.inputs)
    except Exception as e:
        print(f"❌ 入参 JSON 格式错误: {e}")
        sys.exit(1)

    asyncio.run(execute_cli(dsl, inputs))


if __name__ == "__main__":
    main()
