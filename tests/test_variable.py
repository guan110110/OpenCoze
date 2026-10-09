# -*- coding: utf-8 -*-
"""
Unit tests for OpenCoze Variable Resolver.
"""

from opencoze.variable import VariableResolver


def test_single_variable_interpolation():
    outputs = {
        "start": {"topic": "AI", "num": 42},
        "code_1": {"summary": "深度分析"}
    }

    # 1. 混合文本替换
    text = "当前领域：{{start.topic}}，摘要：{{code_1.summary}}"
    res = VariableResolver.resolve(text, outputs)
    assert res == "当前领域：AI，摘要：深度分析"

    # 2. 单占位符保留原始数据类型（数字、字典）
    raw_num = VariableResolver.resolve("{{start.num}}", outputs)
    assert raw_num == 42
    assert isinstance(raw_num, int)


def test_nested_dict_and_list_resolution():
    outputs = {
        "user": {"name": "Alice", "tags": ["VIP", "Core"]}
    }

    template_dict = {
        "greeting": "Hello {{user.name}}",
        "sub": {
            "title": "Welcome {{user.name}}",
            "items": ["User: {{user.name}}", "Fixed"]
        }
    }

    res = VariableResolver.resolve(template_dict, outputs)
    assert res["greeting"] == "Hello Alice"
    assert res["sub"]["title"] == "Welcome Alice"
    assert res["sub"]["items"][0] == "User: Alice"
    assert res["sub"]["items"][1] == "Fixed"
