# -*- coding: utf-8 -*-
"""
End Node: Formats and outputs the final result of the workflow.
"""

from typing import Dict, Any
from opencoze.nodes.base import BaseNode
from opencoze.context import ExecutionContext
from opencoze.variable import VariableResolver


class EndNode(BaseNode):
    """2. 工作流终点节点：格式化并呈现工作流最终输出"""
    node_type = "end"

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        response_template = self.config.get("response", "")
        if response_template:
            # 模板字符串插值
            resolved_text = VariableResolver.resolve(response_template, context.node_outputs)
            return {"result": resolved_text}
        
        # 若未配置 response 模板，直接收集并输出 config 中指定的字段字典
        output_mapping = self.config.get("outputs", {})
        if output_mapping:
            return VariableResolver.resolve(output_mapping, context.node_outputs)

        # 默认取最近一个执行成功节点的输出
        return {"result": "工作流执行完毕"}
