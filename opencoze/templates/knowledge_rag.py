# -*- coding: utf-8 -*-
"""
Template 3: 知识库 RAG 增强检索与严谨问答流
"""

KNOWLEDGE_RAG_WORKFLOW = {
    "id": "wf_knowledge_rag",
    "name": "📚 知识库 RAG 严谨问答流",
    "description": "基于用户提问检索企业专属知识库，利用精准上下文驱动大模型输出无幻觉权威解答",
    "nodes": [
        {
            "id": "start",
            "type": "start",
            "name": "用户提问输入",
            "config": {
                "fields": {
                    "question": {
                        "type": "string",
                        "default": "请问 OpenCoze 的核心架构设计原则是什么？数据在节点间如何传递？"
                    }
                }
            }
        },
        {
            "id": "knowledge_retriever",
            "type": "knowledge",
            "name": "企业知识库语义检索",
            "config": {
                "query": "{{start.question}}",
                "top_k": 2
            }
        },
        {
            "id": "llm_grounded_qa",
            "type": "llm",
            "name": "知识库约束大模型问答",
            "config": {
                "model": "glm-4-flash",
                "system": (
                    "你是一个严谨的企业级技术顾问。请严格基于提供的知识库上下文回答用户问题，"
                    "不得主观捏造或发散。如知识库未提及，请如实说明。"
                ),
                "prompt": (
                    "【参考知识库切片】\n"
                    "{{knowledge_retriever.context}}\n\n"
                    "【用户提问】\n"
                    "{{start.question}}\n\n"
                    "请给出结构化、权威的专业解答："
                )
            }
        },
        {
            "id": "end",
            "type": "end",
            "name": "输出权威解答",
            "config": {
                "response": (
                    "### 💡 智能问答结果 (RAG Grounded QA)\n\n"
                    "**用户问题**：{{start.question}}  \n\n"
                    "---\n\n"
                    "{{llm_grounded_qa.text}}\n\n"
                    "---\n"
                    "ℹ️ *本答案由企业内部知识库切片检索增强生成，无外部幻觉。*"
                )
            }
        }
    ],
    "edges": [
        {"source": "start", "target": "knowledge_retriever"},
        {"source": "knowledge_retriever", "target": "llm_grounded_qa"},
        {"source": "llm_grounded_qa", "target": "end"}
    ]
}
