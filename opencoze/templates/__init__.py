# -*- coding: utf-8 -*-
"""
OpenCoze Pre-built Workflow Templates Catalog.
"""

from opencoze.templates.competitor_analysis import COMPETITOR_ANALYSIS_WORKFLOW
from opencoze.templates.ticket_router import TICKET_ROUTER_WORKFLOW
from opencoze.templates.knowledge_rag import KNOWLEDGE_RAG_WORKFLOW

BUILTIN_TEMPLATES = {
    "competitor_analysis": COMPETITOR_ANALYSIS_WORKFLOW,
    "ticket_router": TICKET_ROUTER_WORKFLOW,
    "knowledge_rag": KNOWLEDGE_RAG_WORKFLOW,
}

__all__ = [
    "COMPETITOR_ANALYSIS_WORKFLOW",
    "TICKET_ROUTER_WORKFLOW",
    "KNOWLEDGE_RAG_WORKFLOW",
    "BUILTIN_TEMPLATES",
]
