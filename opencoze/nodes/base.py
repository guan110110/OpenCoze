# -*- coding: utf-8 -*-
"""
Base Node Protocol and Interface Definition.
"""

from typing import Dict, Any
from opencoze.context import ExecutionContext
from opencoze.variable import VariableResolver


class BaseNode:
    """所有工作流执行节点的抽象基类"""
    node_type: str = "base"

    def __init__(self, node_id: str, name: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.name = name
        self.config = config or {}

    def resolve_config(self, context: ExecutionContext) -> Dict[str, Any]:
        """使用当前上下文数据，自动解析 config 中包含的所有变量插值占位符"""
        return VariableResolver.resolve(self.config, context.node_outputs)

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """
        节点执行入口（必须由子类实现）。
        :param inputs: 工作流全局初始输入参数
        :param context: 工作流执行全局上下文（包含所有上游节点的输出）
        :return: 当前节点产出的结构化字典输出
        """
        raise NotImplementedError(f"Node {self.node_type} must implement execute()")
