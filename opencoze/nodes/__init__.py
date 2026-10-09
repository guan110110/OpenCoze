# -*- coding: utf-8 -*-
"""
OpenCoze Standard Node Library Registry.
"""

from opencoze.nodes.base import BaseNode
from opencoze.nodes.start import StartNode
from opencoze.nodes.end import EndNode
from opencoze.nodes.llm import LLMNode
from opencoze.nodes.code import CodeNode
from opencoze.nodes.condition import ConditionNode
from opencoze.nodes.tool import ToolNode
from opencoze.nodes.knowledge import KnowledgeNode

NODE_REGISTRY = {
    "start": StartNode,
    "end": EndNode,
    "llm": LLMNode,
    "code": CodeNode,
    "condition": ConditionNode,
    "tool": ToolNode,
    "knowledge": KnowledgeNode,
}

__all__ = [
    "BaseNode",
    "StartNode",
    "EndNode",
    "LLMNode",
    "CodeNode",
    "ConditionNode",
    "ToolNode",
    "KnowledgeNode",
    "NODE_REGISTRY",
]
