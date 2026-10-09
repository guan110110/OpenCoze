# -*- coding: utf-8 -*-
"""
OpenCoze Web Server: FastAPI Backend & Workflow Studio API.
"""

import os
import sys
import json
from typing import Dict, Any, Optional

# 注入项目根路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from opencoze.engine import WorkflowEngine
from opencoze.config import get_llm_client
from opencoze.templates import BUILTIN_TEMPLATES

app = FastAPI(title="OpenCoze AI Workflow Studio", version="1.0.0")

# 缓存当前大模型客户端
client, default_model, provider_name = get_llm_client()


class WorkflowRunRequest(BaseModel):
    workflow: Dict[str, Any] = Field(..., description="工作流 DSL 结构字典")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="用户运行参数")


@app.get("/api/info")
async def get_system_info():
    """获取当前系统大模型运行时信息"""
    return {
        "provider": provider_name,
        "default_model": default_model,
        "status": "ready"
    }


@app.get("/api/templates")
async def list_templates():
    """获取系统预置的精品工作流模板列表"""
    result = []
    for k, wf in BUILTIN_TEMPLATES.items():
        result.append({
            "key": k,
            "id": wf.get("id"),
            "name": wf.get("name"),
            "description": wf.get("description"),
            "node_count": len(wf.get("nodes", []))
        })
    return result


@app.get("/api/template/{template_key}")
async def get_template(template_key: str):
    """获取指定模板的工作流 DSL JSON"""
    if template_key not in BUILTIN_TEMPLATES:
        raise HTTPException(status_code=404, detail="模板不存在")
    return BUILTIN_TEMPLATES[template_key]


@app.post("/api/workflow/run")
async def run_workflow(req: WorkflowRunRequest):
    """执行工作流并返回全链路节点 Trace 与最终结果"""
    try:
        engine = WorkflowEngine(req.workflow, llm_client=client)
        result = await engine.run(req.inputs)
        return {
            "success": True,
            "result": result["result"],
            "traces": result["traces"],
            "outputs": result["outputs"]
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


@app.get("/", response_class=HTMLResponse)
async def serve_studio():
    """加载单文件轻量化可视化工作流 Studio 画布前端"""
    html_path = os.path.join(os.path.dirname(__file__), "studio.html")
    if not os.path.exists(html_path):
        return HTMLResponse("<h1>Studio HTML not found</h1>", status_code=404)
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    import uvicorn
    print("\n[OpenCoze] AI 工作流编排工作台正在启动...")
    print("本地访问地址: http://127.0.0.1:8502")
    uvicorn.run("opencoze.web.server:app", host="127.0.0.1", port=8502, reload=False)
