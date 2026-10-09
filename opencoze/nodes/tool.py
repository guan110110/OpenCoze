# -*- coding: utf-8 -*-
"""
Tool / HTTP Node: Executes external API requests or local utility functions.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, Any
from opencoze.nodes.base import BaseNode
from opencoze.context import ExecutionContext
from opencoze.variable import VariableResolver


class ToolNode(BaseNode):
    """6. 工具/插件节点：支持发起标准 REST HTTP 请求或调用系统内置能力"""
    node_type = "tool"

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        tool_action = self.config.get("tool_action", "http")

        # 1. 内置日期与时间工具
        if tool_action == "datetime":
            now = datetime.now()
            return {
                "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "timestamp": int(now.timestamp())
            }

        # 2. 内置数学计算小工具
        if tool_action == "calc":
            expr = VariableResolver.resolve(self.config.get("expression", "0"), context.node_outputs)
            try:
                # 仅允许算术字符
                safe_expr = "".join(c for c in str(expr) if c in "0123456789+-*/(). ")
                val = eval(safe_expr)
                return {"result": val, "expression": safe_expr}
            except Exception as e:
                return {"error": str(e), "result": 0}

        # 3. 标准外部 HTTP 接口请求
        url = VariableResolver.resolve(self.config.get("url", ""), context.node_outputs)
        method = self.config.get("method", "GET").upper()
        headers = VariableResolver.resolve(self.config.get("headers", {}), context.node_outputs)
        body = VariableResolver.resolve(self.config.get("body", {}), context.node_outputs)

        if not url:
            # 模拟返回，确保演示零外网也可稳定运行
            return {
                "status": 200,
                "data": {"mock_response": "HTTP 请求成功", "target_url": url or "mock://api.service"}
            }

        try:
            req_data = None
            if method in ["POST", "PUT", "PATCH"] and body:
                req_data = json.dumps(body).encode("utf-8")
                headers["Content-Type"] = "application/json"

            req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=5) as resp:
                resp_text = resp.read().decode("utf-8")
                try:
                    resp_json = json.loads(resp_text)
                    return {"status": resp.status, "data": resp_json}
                except Exception:
                    return {"status": resp.status, "data": resp_text}
        except Exception as e:
            return {"status": 500, "error": str(e), "data": {}}
