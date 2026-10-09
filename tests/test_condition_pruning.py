# -*- coding: utf-8 -*-
"""
Unit tests for ConditionNode branching and downstream pruning.
"""

import pytest
from opencoze.engine import WorkflowEngine


@pytest.mark.asyncio
async def test_condition_true_branch():
    dsl = {
        "nodes": [
            {"id": "start", "type": "start", "config": {}},
            {
                "id": "check_score",
                "type": "condition",
                "config": {
                    "left_var": "{{start.score}}",
                    "operator": ">=",
                    "right_value": "60"
                }
            },
            {
                "id": "pass_node",
                "type": "code",
                "config": {
                    "code": "def main(inputs):\n    return {'msg': '及格通过'}"
                }
            },
            {
                "id": "fail_node",
                "type": "code",
                "config": {
                    "code": "def main(inputs):\n    return {'msg': '挂科重修'}"
                }
            },
            {
                "id": "end",
                "type": "end",
                "config": {"response": "评定结果: {{pass_node.msg}}{{fail_node.msg}}"}
            }
        ],
        "edges": [
            {"source": "start", "target": "check_score"},
            {"source": "check_score", "target": "pass_node", "branch": "true_branch"},
            {"source": "check_score", "target": "fail_node", "branch": "false_branch"},
            {"source": "pass_node", "target": "end"},
            {"source": "fail_node", "target": "end"}
        ]
    }

    # 测试输入 85（预期命中 true 分支）
    engine = WorkflowEngine(dsl)
    res = await engine.run({"score": 85})
    assert res["result"] == "评定结果: 及格通过"
    assert res["traces"]["pass_node"]["status"] == "SUCCESS"
    assert res["traces"]["fail_node"]["status"] == "SKIPPED"

    # 测试输入 45（预期命中 false 分支）
    engine_fail = WorkflowEngine(dsl)
    res_fail = await engine_fail.run({"score": 45})
    assert res_fail["result"] == "评定结果: 挂科重修"
    assert res_fail["traces"]["pass_node"]["status"] == "SKIPPED"
    assert res_fail["traces"]["fail_node"]["status"] == "SUCCESS"
