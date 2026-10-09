# -*- coding: utf-8 -*-
"""
OpenCoze Workflow Engine: High-performance DAG Topology Scheduler with Parallelism,
Variable Resolution, Branch Pruning, and Full-link Traceability.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Set, Callable, Coroutine
from opencoze.context import ExecutionContext, NodeTrace, NodeStatus
from opencoze.nodes import NODE_REGISTRY, BaseNode


class WorkflowEngine:
    """有向无环图 (DAG) 工作流调度引擎"""

    def __init__(self, workflow_dsl: Dict[str, Any], llm_client: Optional[Any] = None):
        self.dsl = workflow_dsl
        self.llm_client = llm_client
        self.nodes: Dict[str, BaseNode] = {}
        # 节点出边表: node_id -> [ {"target": dst_id, "branch": branch_name} ]
        self.downstream_edges: Dict[str, List[Dict[str, Any]]] = {}
        self.in_degrees: Dict[str, int] = {}
        self._build_graph()

    def _build_graph(self):
        """解析工作流定义，实例化节点并构建拓扑有向图"""
        raw_nodes = self.dsl.get("nodes", [])
        raw_edges = self.dsl.get("edges", [])

        # 1. 实例化各个节点
        for n_meta in raw_nodes:
            nid = n_meta["id"]
            ntype = n_meta.get("type", "base")
            name = n_meta.get("name", nid)
            cfg = dict(n_meta.get("config", {}))

            if ntype == "llm" and self.llm_client:
                cfg["_client"] = self.llm_client

            node_cls = NODE_REGISTRY.get(ntype, BaseNode)
            self.nodes[nid] = node_cls(nid, name, cfg)
            self.downstream_edges[nid] = []
            self.in_degrees[nid] = 0

        # 2. 映射有向边
        for edge in raw_edges:
            src = edge["source"]
            dst = edge["target"]
            branch = edge.get("branch")  # 可选分支标识，如 'true_branch' / 'false_branch'
            if src in self.downstream_edges and dst in self.nodes:
                self.downstream_edges[src].append({"target": dst, "branch": branch})
                self.in_degrees[dst] += 1

    def validate_dag(self) -> bool:
        """拓扑排序校验是否存在环形死锁"""
        degrees = dict(self.in_degrees)
        queue = [nid for nid, deg in degrees.items() if deg == 0]
        visited_count = 0

        while queue:
            curr = queue.pop(0)
            visited_count += 1
            for edge in self.downstream_edges.get(curr, []):
                target = edge["target"]
                degrees[target] -= 1
                if degrees[target] == 0:
                    queue.append(target)

        return visited_count == len(self.nodes)

    def _prune_downstream(self, node_id: str, context: ExecutionContext, in_degrees: Dict[str, int], ready_queue: asyncio.Queue):
        """递归剪枝未命中的分支子树"""
        if node_id in context.skipped_nodes:
            return
        ntype = self.nodes[node_id].node_type if node_id in self.nodes else "base"
        context.mark_skipped(node_id, ntype)
        
        # 将被剪枝节点的下游入度扣除
        for edge in self.downstream_edges.get(node_id, []):
            nxt = edge["target"]
            in_degrees[nxt] -= 1
            if in_degrees[nxt] == 0:
                # 若其所有前置均被剪枝或完成，下游节点也自动转为剪枝流程
                self._prune_downstream(nxt, context, in_degrees, ready_queue)

    async def run(
        self,
        initial_inputs: Dict[str, Any],
        on_node_event: Optional[Callable[[Dict[str, Any]], Coroutine]] = None
    ) -> Dict[str, Any]:
        """
        全异步并发执行工作流
        :param initial_inputs: 工作流启动初始入参
        :param on_node_event: 可选节点生命周期事件回调（用于实时推送流式运行状态）
        :return: 包含最终结果与全链路 Trace 的结果字典
        """
        if not self.validate_dag():
            raise ValueError("工作流结构存在环路依赖 (Cycle Detected)，无法执行！")

        context = ExecutionContext(initial_inputs)
        in_degrees = dict(self.in_degrees)

        # 查找无前置依赖的起始节点（入度为 0）
        ready_queue: asyncio.Queue[str] = asyncio.Queue()
        for nid, deg in in_degrees.items():
            if deg == 0:
                ready_queue.put_nowait(nid)

        while not ready_queue.empty():
            # 取出当前层级所有准备就绪的节点，实施批量并发调度
            current_batch: List[str] = []
            while not ready_queue.empty():
                current_batch.append(ready_queue.get_nowait())

            async def _run_single(nid: str):
                node = self.nodes[nid]
                trace = NodeTrace(node_id=nid, node_type=node.node_type)
                context.traces[nid] = trace

                # 检查是否在前置条件中被标记跳过
                if nid in context.skipped_nodes:
                    trace.status = NodeStatus.SKIPPED
                    if on_node_event:
                        await on_node_event({"event": "node_skipped", "trace": trace.model_dump()})
                    return

                trace.status = NodeStatus.RUNNING
                trace.start_time = time.time()
                trace.inputs = node.resolve_config(context)

                if on_node_event:
                    await on_node_event({"event": "node_running", "trace": trace.model_dump()})

                try:
                    outputs = await node.execute(initial_inputs, context)
                    trace.outputs = outputs
                    trace.status = NodeStatus.SUCCESS
                    trace.tokens = outputs.get("tokens", 0)
                    context.set_output(nid, outputs)

                    # 分支决策处理：若为条件节点，自动识别激活分支并剪枝反向分支
                    if node.node_type == "condition":
                        active_branch = outputs.get("branch")
                        for edge in self.downstream_edges.get(nid, []):
                            branch_req = edge.get("branch")
                            if branch_req and branch_req != active_branch:
                                self._prune_downstream(edge["target"], context, in_degrees, ready_queue)

                    if on_node_event:
                        await on_node_event({"event": "node_success", "trace": trace.model_dump()})

                except Exception as e:
                    trace.status = NodeStatus.FAILED
                    trace.error = str(e)
                    if on_node_event:
                        await on_node_event({"event": "node_failed", "trace": trace.model_dump()})
                    raise e
                finally:
                    trace.duration_ms = round((time.time() - trace.start_time) * 1000, 2)

            # 并发执行当前批次
            await asyncio.gather(*[_run_single(nid) for nid in current_batch])

            # 推进下游依赖入度扣减
            for nid in current_batch:
                # 如果当前节点已被跳过，下游已经在剪枝逻辑中处理
                if nid in context.skipped_nodes:
                    continue
                for edge in self.downstream_edges.get(nid, []):
                    target = edge["target"]
                    if target in context.skipped_nodes:
                        continue
                    in_degrees[target] -= 1
                    if in_degrees[target] == 0:
                        ready_queue.put_nowait(target)

        # 确保所有未被调度的节点（剪枝节点或待执行节点）都具备完整 Trace
        for nid, node in self.nodes.items():
            if nid not in context.traces:
                status = NodeStatus.SKIPPED if nid in context.skipped_nodes else NodeStatus.PENDING
                context.traces[nid] = NodeTrace(node_id=nid, node_type=node.node_type, status=status)

        # 提取结束节点输出
        end_node_id = next((nid for nid, n in self.nodes.items() if n.node_type == "end"), None)
        final_output = context.node_outputs.get(end_node_id, {}) if end_node_id else {}
        final_result = final_output.get("result", "")

        return {
            "result": final_result,
            "traces": {nid: t.model_dump() for nid, t in context.traces.items()},
            "outputs": context.node_outputs
        }
