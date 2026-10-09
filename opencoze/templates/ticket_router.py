# -*- coding: utf-8 -*-
"""
Template 2: 客户工单智能意图分类、条件分流与自动回复流
"""

TICKET_ROUTER_WORKFLOW = {
    "id": "wf_ticket_router",
    "name": "🛡️ 客诉意图智能分类与自动分流流",
    "description": "实时解析客户消息情绪与意图，判定是否紧急，并自动分流至加急人工工单或自助解答",
    "nodes": [
        {
            "id": "start",
            "type": "start",
            "name": "接收客户咨询",
            "config": {
                "fields": {
                    "customer_message": {
                        "type": "string",
                        "default": "你们这什么破系统！再不给我退款我直接打12315投诉曝光你们！"
                    },
                    "user_id": {"type": "string", "default": "USR_9981"}
                }
            }
        },
        {
            "id": "code_sentiment",
            "type": "code",
            "name": "情绪敏感词与特征粗筛",
            "config": {
                "input_vars": {
                    "msg": "{{start.customer_message}}"
                },
                "code": (
                    "def main(inputs):\n"
                    "    msg = inputs.get('msg', '')\n"
                    "    urgent_keywords = ['12315', '投诉', '退钱', '垃圾', '曝光', '骗子', '法院']\n"
                    "    hits = [kw for kw in urgent_keywords if kw in msg]\n"
                    "    is_urgent = 'true' if len(hits) >= 1 else 'false'\n"
                    "    return {'is_urgent': is_urgent, 'hits': hits}\n"
                )
            }
        },
        {
            "id": "condition_branch",
            "type": "condition",
            "name": "紧急程度路由门",
            "config": {
                "left_var": "{{code_sentiment.is_urgent}}",
                "operator": "==",
                "right_value": "true"
            }
        },
        {
            "id": "tool_create_ticket",
            "type": "tool",
            "name": "创建紧急人工支持工单",
            "config": {
                "tool_action": "datetime",
                "memo": "模拟调用工单中台 API"
            }
        },
        {
            "id": "llm_calm_response",
            "type": "llm",
            "name": "情绪共情安抚话术生成",
            "config": {
                "model": "glm-4-flash",
                "system": "你是一位金牌客服主管，擅长高难度客户冲突沟通与共情安抚。",
                "prompt": (
                    "客户十分愤怒，发来消息：【{{start.customer_message}}】。\n"
                    "后台已自动为其创建紧急加急特快工单，请生成一段诚恳道歉、表达重视、并告知主管已介入处理的安抚话术。"
                )
            }
        },
        {
            "id": "llm_normal_reply",
            "type": "llm",
            "name": "常规业务自助解答",
            "config": {
                "model": "glm-4-flash",
                "system": "你是一位热情专业的智能客服助手。",
                "prompt": "针对客户的常规咨询【{{start.customer_message}}】，给出清晰专业的业务解答指引。"
            }
        },
        {
            "id": "end",
            "type": "end",
            "name": "反馈用户处理结论",
            "config": {
                "response": (
                    "### 🎯 客服调度中枢处理结果\n\n"
                    "**用户编号**：{{start.user_id}}  \n"
                    "**紧急客诉判定**：{{code_sentiment.is_urgent}}  \n\n"
                    "---\n\n"
                    "{{llm_calm_response.text}}{{llm_normal_reply.text}}"
                )
            }
        }
    ],
    "edges": [
        {"source": "start", "target": "code_sentiment"},
        {"source": "code_sentiment", "target": "condition_branch"},
        {"source": "condition_branch", "target": "tool_create_ticket", "branch": "true_branch"},
        {"source": "tool_create_ticket", "target": "llm_calm_response"},
        {"source": "llm_calm_response", "target": "end"},
        {"source": "condition_branch", "target": "llm_normal_reply", "branch": "false_branch"},
        {"source": "llm_normal_reply", "target": "end"}
    ]
}
