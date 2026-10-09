# -*- coding: utf-8 -*-
"""
Code Node: Executes custom Python scripts for data transformation and business logic.
"""

from typing import Dict, Any
from opencoze.nodes.base import BaseNode
from opencoze.context import ExecutionContext
from opencoze.variable import VariableResolver


class CodeNode(BaseNode):
    """4. 代码节点：执行轻量 Python 脚本进行定制化数据清洗、聚合或数学计算"""
    node_type = "code"

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        # 1. 解析传入代码节点的输入参数
        input_vars_config = self.config.get("input_vars", {})
        resolved_inputs = VariableResolver.resolve(input_vars_config, context.node_outputs)

        # 2. 提取 Python 源码，默认包含 main(inputs)
        code_str = self.config.get("code", "def main(inputs):\n    return {'out': inputs}")

        # 3. 构造安全执行环境
        local_scope: Dict[str, Any] = {}
        safe_globals = {
            "__builtins__": {
                k: v for k, v in __builtins__.__dict__.items()
                if k not in ["exit", "quit", "__import__"]
            } if hasattr(__builtins__, "__dict__") else __builtins__
        }

        try:
            exec(code_str, safe_globals, local_scope)
        except Exception as e:
            raise RuntimeError(f"代码编译语法错误: {e}")

        if "main" not in local_scope or not callable(local_scope["main"]):
            raise ValueError("代码节点必须包含入口函数 def main(inputs):")

        try:
            result = local_scope["main"](resolved_inputs)
        except Exception as e:
            raise RuntimeError(f"代码执行运行时异常: {e}")

        if isinstance(result, dict):
            return result
        return {"result": result}
