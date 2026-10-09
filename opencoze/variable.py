# -*- coding: utf-8 -*-
"""
Variable Reference Resolver for Coze-like data piping: {{node_id.field_name}}.
"""

import re
from typing import Any, Dict


class VariableResolver:
    """解析并替换 {{node_id.key}} 形式的变量插值表达式"""

    PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\s*\}\}")

    @classmethod
    def resolve(cls, value: Any, outputs: Dict[str, Dict[str, Any]]) -> Any:
        """
        递归对字符串、字典、列表中的变量占位符进行求值。
        当字符串完全等于单占位符（如 '{{node.data}}'）且目标值为非字符串时，保留原始数据类型（dict/list/int等）。
        """
        if isinstance(value, str):
            # 1. 检查是否为单一纯占位符
            match = cls.PATTERN.fullmatch(value.strip())
            if match:
                node_id, field = match.group(1), match.group(2)
                if node_id in outputs and field in outputs[node_id]:
                    return outputs[node_id][field]
                return ""

            # 2. 多变量混合文本字符串插值
            def _replace(m):
                n_id, field = m.group(1), m.group(2)
                val = outputs.get(n_id, {}).get(field, "")
                return str(val) if val is not None else ""

            return cls.PATTERN.sub(_replace, value)

        elif isinstance(value, dict):
            return {k: cls.resolve(v, outputs) for k, v in value.items()}

        elif isinstance(value, list):
            return [cls.resolve(item, outputs) for item in value]

        return value
