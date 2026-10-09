# -*- coding: utf-8 -*-
"""
Start Node: Validates initial workflow inputs and outputs them to context.
"""

from typing import Dict, Any
from opencoze.nodes.base import BaseNode
from opencoze.context import ExecutionContext


class StartNode(BaseNode):
    """1. 工作流起点节点：接收并向后传递工作流全局输入参数"""
    node_type = "start"

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        # 可以基于 config 中的 schema 进行类型校验与默认值回填
        fields = self.config.get("fields", {})
        result = dict(inputs or {})
        for field_name, field_def in fields.items():
            if field_name not in result and "default" in field_def:
                result[field_name] = field_def["default"]
        return result
