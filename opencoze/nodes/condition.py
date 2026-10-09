# -*- coding: utf-8 -*-
"""
Condition Node: Handles logical branching (If-Else) for workflow routing.
"""

from typing import Dict, Any
from opencoze.nodes.base import BaseNode
from opencoze.context import ExecutionContext
from opencoze.variable import VariableResolver


class ConditionNode(BaseNode):
    """5. 条件分支节点：对变量进行逻辑判定，决定激活的分支通道"""
    node_type = "condition"

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        left_tmpl = self.config.get("left_var", "")
        left_val = VariableResolver.resolve(left_tmpl, context.node_outputs)
        operator = self.config.get("operator", "==")
        right_tmpl = self.config.get("right_value", "")
        right_val = VariableResolver.resolve(right_tmpl, context.node_outputs)

        is_match = False
        if operator == "==":
            is_match = str(left_val).strip() == str(right_val).strip()
        elif operator == "!=":
            is_match = str(left_val).strip() != str(right_val).strip()
        elif operator == "contains":
            is_match = str(right_val) in str(left_val)
        elif operator == "not_contains":
            is_match = str(right_val) not in str(left_val)
        elif operator in [">", ">=", "<", "<="]:
            try:
                n1, n2 = float(left_val), float(right_val)
                if operator == ">": is_match = n1 > n2
                elif operator == ">=": is_match = n1 >= n2
                elif operator == "<": is_match = n1 < n2
                elif operator == "<=": is_match = n1 <= n2
            except (ValueError, TypeError):
                is_match = False

        chosen_branch = "true_branch" if is_match else "false_branch"
        return {
            "branch": chosen_branch,
            "evaluated": is_match,
            "left_val": left_val,
            "right_val": right_val
        }
