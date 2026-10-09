# -*- coding: utf-8 -*-
"""
LLM Node: Handles Prompt interpolation, system instructions, and multi-model generation.
"""

from typing import Dict, Any
from opencoze.nodes.base import BaseNode
from opencoze.context import ExecutionContext
from opencoze.variable import VariableResolver


class LLMNode(BaseNode):
    """3. 大模型节点：负责动态提示词插值并调用 LLM 生成内容"""
    node_type = "llm"

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        prompt_tmpl = self.config.get("prompt", "")
        system_tmpl = self.config.get("system", "你是一个专业、严谨、客观的人工智能业务专家。")
        temperature = float(self.config.get("temperature", 0.7))
        model_name = self.config.get("model", "glm-4-flash")

        # 动态解析提示词与系统设定中的变量
        resolved_prompt = VariableResolver.resolve(prompt_tmpl, context.node_outputs)
        resolved_system = VariableResolver.resolve(system_tmpl, context.node_outputs)

        client = self.config.get("_client")

        # 1. 若配置了大模型客户端，发起真实 API 请求
        if client:
            try:
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": resolved_system},
                        {"role": "user", "content": resolved_prompt}
                    ],
                    temperature=temperature
                )
                output_text = resp.choices[0].message.content or ""
                tokens = getattr(resp.usage, "total_tokens", 0) if hasattr(resp, "usage") else len(output_text)
                return {
                    "text": output_text,
                    "model": model_name,
                    "tokens": tokens
                }
            except Exception as e:
                # 若外部调用异常，提供兜底输出
                return {
                    "text": f"【大模型调用异常】{str(e)}",
                    "model": model_name,
                    "tokens": 0
                }

        # 2. 离线仿真 Mock 降级生成
        mock_output = (
            f"【Mock 深度研报分析】\n"
            f"基于提示词：{resolved_prompt[:60]}...\n\n"
            f"1. 核心业务痛点与技术壁垒评估：该方向展现出极高市场关注度，技术生态正从单一模型调用转向工程化工作流编排。\n"
            f"2. 商业竞争力对比：在产品易用性与二次开发门槛上具备明显优势。\n"
            f"3. 未来战略建议：建议加速与企业中台及私有知识库打通。"
        )
        return {
            "text": mock_output,
            "model": "mock-llm",
            "tokens": len(mock_output)
        }
