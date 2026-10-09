# -*- coding: utf-8 -*-
"""
Tests for template persistence and dynamic workflow creation.
"""

import pytest
from opencoze.engine import WorkflowEngine
from opencoze.templates import BUILTIN_TEMPLATES


def test_builtin_templates_integrity():
    """验证所有内置模板的结构完整性"""
    assert len(BUILTIN_TEMPLATES) >= 3
    for key, wf in BUILTIN_TEMPLATES.items():
        assert "nodes" in wf
        assert "edges" in wf
        assert len(wf["nodes"]) >= 3
        # 验证 DAG 无环
        engine = WorkflowEngine(wf)
        assert engine.validate_dag() is True


@pytest.mark.asyncio
async def test_dynamic_node_addition_and_execution():
    """测试在运行时动态追加新节点（如在 Start 和 End 之间动态插入 Python Code 节点）并成功调度执行"""
    # 基础流程
    dynamic_wf = {
        "nodes": [
            {"id": "start", "type": "start", "config": {}},
            {"id": "end", "type": "end", "config": {"response": "输出: {{code_added.doubled}}"}}
        ],
        "edges": []
    }

    # 动态插入一个新 CodeNode
    new_node = {
        "id": "code_added",
        "type": "code",
        "config": {
            "input_vars": {"val": "{{start.num}}"},
            "code": "def main(inputs):\n    return {'doubled': int(inputs['val']) * 10}"
        }
    }
    dynamic_wf["nodes"].append(new_node)
    dynamic_wf["edges"].append({"source": "start", "target": "code_added"})
    dynamic_wf["edges"].append({"source": "code_added", "target": "end"})

    engine = WorkflowEngine(dynamic_wf)
    res = await engine.run({"num": 5})

    assert res["result"] == "输出: 50"
    assert res["traces"]["code_added"]["status"] == "SUCCESS"
    assert res["traces"]["end"]["status"] == "SUCCESS"
