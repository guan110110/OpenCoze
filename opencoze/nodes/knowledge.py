# -*- coding: utf-8 -*-
"""
Knowledge Node: Handles Knowledge Base RAG document retrieval for AI workflows.
"""

from typing import Dict, Any, List
from opencoze.nodes.base import BaseNode
from opencoze.context import ExecutionContext
from opencoze.variable import VariableResolver


class KnowledgeNode(BaseNode):
    """7. 知识库节点：根据 Query 检索本地向量知识库或知识块数据"""
    node_type = "knowledge"

    # 内置默认知识库示例
    DEFAULT_DOCS = [
        {"title": "OpenCoze 工作流引擎设计原则", "content": "OpenCoze 采用 DAG 有向无环图作为计算核心，支持变量拓扑依赖解析与异步并发调度。"},
        {"title": "节点与数据流管道说明", "content": "节点之间通过 {{node_id.field}} 语法实现严格的数据解耦绑定，支持条件分支智能剪枝与错误回退。"},
        {"title": "企业级私有化与扩展", "content": "OpenCoze 支持直连 Ollama 本地模型、智谱 GLM-4-Flash 与 DeepSeek，数据完全可留在内网。"},
        {"title": "售后退换货保障规范", "content": "自签收之日起7天内支持无理由退换货；质量问题商家承担来回运费，普通退货由买家寄回。"}
    ]

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        query_tmpl = self.config.get("query", "")
        query = VariableResolver.resolve(query_tmpl, context.node_outputs)
        top_k = int(self.config.get("top_k", 2))
        docs: List[Dict[str, Any]] = self.config.get("dataset") or self.DEFAULT_DOCS

        if not query:
            return {"chunks": [], "context": ""}

        # 相似度打分（词法重合度与关键词匹配）
        query_chars = set(str(query).lower())
        scored_docs = []
        for doc in docs:
            c_text = f"{doc.get('title', '')} {doc.get('content', '')}".lower()
            overlap = len(query_chars & set(c_text))
            scored_docs.append((overlap, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = [d[1] for d in scored_docs[:top_k]]
        joined_context = "\n---\n".join([f"【{d.get('title')}】\n{d.get('content')}" for d in top_docs])

        return {
            "query": query,
            "chunks": top_docs,
            "context": joined_context
        }
