# -*- coding: utf-8 -*-
"""
Unit tests for WorkflowEngine DAG Scheduling & Execution.
"""

import pytest
from opencoze.engine import WorkflowEngine


@pytest.mark.asyncio
async def test_linear_dag_execution():
    dsl = {
        "nodes": [
            {"id": "start", "type": "start", "config": {}},
            {
                "id": "code_step",
                "type": "code",
                "config": {
                    "input_vars": {"val": "{{start.x}}"},
                    "code": "def main(inputs):\n    return {'doubled': int(inputs['val']) * 2}"
                }
            },
            {
                "id": "end",
                "type": "end",
                "config": {"response": "Result is {{code_step.doubled}}"}
            }
        ],
        "edges": [
            {"source": "start", "target": "code_step"},
            {"source": "code_step", "target": "end"}
        ]
    }

    engine = WorkflowEngine(dsl)
    result = await engine.run({"x": 21})
    assert result["result"] == "Result is 42"
    assert result["traces"]["code_step"]["status"] == "SUCCESS"
    assert result["traces"]["end"]["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_cycle_detection():
    # 构造环形依赖 A -> B -> A
    dsl = {
        "nodes": [
            {"id": "node_a", "type": "start", "config": {}},
            {"id": "node_b", "type": "end", "config": {}}
        ],
        "edges": [
            {"source": "node_a", "target": "node_b"},
            {"source": "node_b", "target": "node_a"}
        ]
    }

    engine = WorkflowEngine(dsl)
    with pytest.raises(ValueError, match="存在环路依赖"):
        await engine.run({})
