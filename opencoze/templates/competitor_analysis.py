# -*- coding: utf-8 -*-
"""
Template 1: 竞品智能深度分析与研报生成工作流
"""

COMPETITOR_ANALYSIS_WORKFLOW = {
    "id": "wf_competitor_analysis",
    "name": "📊 标杆竞品深度商业研报流",
    "description": "输入行业领域与标杆产品，由代码节点自动构建多维评估矩阵，再由大模型撰写深度商业研报",
    "nodes": [
        {
            "id": "start",
            "type": "start",
            "name": "输入分析目标",
            "config": {
                "fields": {
                    "topic": {"type": "string", "default": "AI工作流与智能体编排平台"},
                    "target": {"type": "string", "default": "字节跳动 Coze (扣子)"}
                }
            }
        },
        {
            "id": "code_preprocess",
            "type": "code",
            "name": "构建评估维度矩阵",
            "config": {
                "input_vars": {
                    "topic": "{{start.topic}}",
                    "target": "{{start.target}}"
                },
                "code": (
                    "def main(inputs):\n"
                    "    topic = inputs.get('topic', '前沿科技')\n"
                    "    target = inputs.get('target', '标杆产品')\n"
                    "    dimensions = [\n"
                    "        '1. 核心产品架构与核心护城河',\n"
                    "        '2. 商业化变现与企业级落地场景',\n"
                    "        '3. 开发者生态与二次开发门槛',\n"
                    "        '4. 核心优劣势对比与短板分析'\n"
                    "    ]\n"
                    "    outline_str = '\\n'.join(dimensions)\n"
                    "    return {\n"
                    "        'outline': outline_str,\n"
                    "        'meta_title': f'针对【{target}】在【{topic}】领域的深度商业洞察报告'\n"
                    "    }\n"
                )
            }
        },
        {
            "id": "llm_report",
            "type": "llm",
            "name": "战略级深度研报撰写",
            "config": {
                "model": "glm-4-flash",
                "system": "你是一位拥有 10 年高科技与互联网战略投资经验的顶级行业分析师。",
                "prompt": (
                    "请围绕报告主题【{{code_preprocess.meta_title}}】，结合以下战略评估维度深入撰写一份结构化、洞察深刻的研报：\n\n"
                    "{{code_preprocess.outline}}\n\n"
                    "要求：观点犀利，条理清晰，多用数据与行业案例支撑，篇幅详实。"
                ),
                "temperature": 0.7
            }
        },
        {
            "id": "end",
            "type": "end",
            "name": "输出最终研报",
            "config": {
                "response": (
                    "# 📑 {{code_preprocess.meta_title}}\n\n"
                    "**分析标的**：{{start.target}}  \n"
                    "**所在领域**：{{start.topic}}  \n\n"
                    "---\n\n"
                    "{{llm_report.text}}"
                )
            }
        }
    ],
    "edges": [
        {"source": "start", "target": "code_preprocess"},
        {"source": "code_preprocess", "target": "llm_report"},
        {"source": "llm_report", "target": "end"}
    ]
}
