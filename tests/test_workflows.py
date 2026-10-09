# -*- coding: utf-8 -*-
"""
End-to-End tests for all built-in workflow templates.
"""

import pytest
from opencoze.engine import WorkflowEngine
from opencoze.templates import (
    COMPETITOR_ANALYSIS_WORKFLOW,
    TICKET_ROUTER_WORKFLOW,
    KNOWLEDGE_RAG_WORKFLOW
)
from opencoze.config import get_llm_client


@pytest.mark.asyncio
async def test_competitor_analysis_template_e2e():
    client, default_model, provider_name = get_llm_client()
    engine = WorkflowEngine(COMPETITOR_ANALYSIS_WORKFLOW, llm_client=client)
    inputs = {
        "topic": "新一代多模态大模型",
        "target": "OpenAI GPT-4o"
    }
    result = await engine.run(inputs)
    assert result is not None
    assert len(result["result"]) > 20
    assert "OpenAI GPT-4o" in result["result"]
    assert result["traces"]["code_preprocess"]["status"] == "SUCCESS"
    assert result["traces"]["llm_report"]["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_ticket_router_template_e2e():
    client, default_model, provider_name = get_llm_client()
    engine = WorkflowEngine(TICKET_ROUTER_WORKFLOW, llm_client=client)
    inputs = {
        "customer_message": "我等了三天还没发货，再不解决我就直接打12315投诉！",
        "user_id": "TEST_USER_888"
    }
    result = await engine.run(inputs)
    assert result is not None
    assert "TEST_USER_888" in result["result"]
    assert result["traces"]["condition_branch"]["status"] == "SUCCESS"
    # 命中紧急分支
    assert result["traces"]["tool_create_ticket"]["status"] == "SUCCESS"
    assert result["traces"]["llm_calm_response"]["status"] == "SUCCESS"
    assert result["traces"]["llm_normal_reply"]["status"] == "SKIPPED"


@pytest.mark.asyncio
async def test_knowledge_rag_template_e2e():
    client, default_model, provider_name = get_llm_client()
    engine = WorkflowEngine(KNOWLEDGE_RAG_WORKFLOW, llm_client=client)
    inputs = {
        "question": "OpenCoze 的架构核心是什么？"
    }
    result = await engine.run(inputs)
    assert result is not None
    assert "OpenCoze" in result["result"]
    assert result["traces"]["knowledge_retriever"]["status"] == "SUCCESS"
    assert result["traces"]["llm_grounded_qa"]["status"] == "SUCCESS"
