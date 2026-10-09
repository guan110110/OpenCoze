# -*- coding: utf-8 -*-
"""
Execution Context, Node Lifecycle States, and Observability Traces.
"""

from enum import Enum
from typing import Dict, Any, Optional, Set
from pydantic import BaseModel, Field


class NodeStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class NodeTrace(BaseModel):
    node_id: str
    node_type: str
    status: NodeStatus = NodeStatus.PENDING
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    start_time: float = 0.0
    duration_ms: float = 0.0
    tokens: int = 0


class ExecutionContext:
    """管理单次工作流执行全生命周期状态、全局变量表与节点追溯"""
    def __init__(self, initial_inputs: Optional[Dict[str, Any]] = None):
        self.node_outputs: Dict[str, Dict[str, Any]] = {
            "start": initial_inputs or {}
        }
        self.traces: Dict[str, NodeTrace] = {}
        self.skipped_nodes: Set[str] = set()

    def set_output(self, node_id: str, outputs: Dict[str, Any]):
        """记录指定节点的输出数据包"""
        self.node_outputs[node_id] = outputs or {}

    def get_output(self, node_id: str, field: Optional[str] = None) -> Any:
        """获取指定节点或其特定字段的输出值"""
        node_dict = self.node_outputs.get(node_id, {})
        if field is None:
            return node_dict
        return node_dict.get(field)

    def mark_skipped(self, node_id: str, node_type: str = "base"):
        """将节点标记为分支剪枝跳过"""
        self.skipped_nodes.add(node_id)
        if node_id not in self.traces:
            self.traces[node_id] = NodeTrace(node_id=node_id, node_type=node_type, status=NodeStatus.SKIPPED)
        else:
            self.traces[node_id].status = NodeStatus.SKIPPED
