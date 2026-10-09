# -*- coding: utf-8 -*-
"""
OpenCoze Web Server: FastAPI Backend & Workflow Studio API with Custom Workflow & Template Persistence.
"""

import os
import sys
import json
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

# 注入项目根路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from opencoze.engine import WorkflowEngine
from opencoze.config import get_llm_client
from opencoze.templates import BUILTIN_TEMPLATES

app = FastAPI(title="OpenCoze AI Workflow Studio", version="1.1.0")

# 缓存当前大模型客户端
client, default_model, provider_name = get_llm_client()

# 本地自定义工作流模板持久化存储目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "workflows")
os.makedirs(DATA_DIR, exist_ok=True)


class WorkflowRunRequest(BaseModel):
    workflow: Dict[str, Any] = Field(..., description="工作流 DSL 结构字典")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="用户运行参数")


class SaveTemplateRequest(BaseModel):
    key: str = Field(..., description="模板唯一标识键名 (如 my_custom_flow)")
    workflow: Dict[str, Any] = Field(..., description="工作流 DSL 结构")


def get_custom_templates() -> Dict[str, Dict[str, Any]]:
    """读取保存在本地 data/workflows 下的自定义模板"""
    custom = {}
    if os.path.exists(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            if fname.endswith(".json"):
                k = fname[:-5]
                fp = os.path.join(DATA_DIR, fname)
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        custom[k] = json.load(f)
                except Exception:
                    pass
    return custom


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
    """获取系统模板列表（包含官方内置精品模板与用户保存的自定义模板）"""
    result = []
    
    # 1. 官方内置模板
    for k, wf in BUILTIN_TEMPLATES.items():
        result.append({
            "key": k,
            "id": wf.get("id"),
            "name": wf.get("name"),
            "description": wf.get("description"),
            "node_count": len(wf.get("nodes", [])),
            "is_builtin": True
        })

    # 2. 用户自定义模板
    custom_templates = get_custom_templates()
    for k, wf in custom_templates.items():
        result.append({
            "key": k,
            "id": wf.get("id", k),
            "name": wf.get("name", k),
            "description": wf.get("description", "用户自定义工作流模板"),
            "node_count": len(wf.get("nodes", [])),
            "is_builtin": False
        })

    return result


@app.get("/api/template/{template_key}")
async def get_template(template_key: str):
    """获取指定模板的工作流 DSL JSON"""
    if template_key in BUILTIN_TEMPLATES:
        return BUILTIN_TEMPLATES[template_key]

    custom_templates = get_custom_templates()
    if template_key in custom_templates:
        return custom_templates[template_key]

    raise HTTPException(status_code=404, detail="模板不存在")


@app.post("/api/template")
async def save_template(req: SaveTemplateRequest):
    """将工作流保存为新模板（持久化存储到本地磁盘）"""
    key = req.key.strip()
    if not key:
        raise HTTPException(status_code=400, detail="模板标识键名不能为空")

    fp = os.path.join(DATA_DIR, f"{key}.json")
    try:
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(req.workflow, f, ensure_ascii=False, indent=2)
        return {"success": True, "key": key, "message": "模板保存成功！"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {e}")


@app.delete("/api/template/{template_key}")
async def delete_template(template_key: str):
    """删除指定的自定义工作流模板"""
    if template_key in BUILTIN_TEMPLATES:
        raise HTTPException(status_code=400, detail="系统官方内置模板不可删除")

    fp = os.path.join(DATA_DIR, f"{template_key}.json")
    if os.path.exists(fp):
        try:
            os.remove(fp)
            return {"success": True, "message": "模板已删除"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"删除失败: {e}")
    else:
        raise HTTPException(status_code=404, detail="模板文件不存在")


@app.post("/api/workflow/new")
async def create_new_blank_workflow(name: str = Body(default="新建空白工作流")):
    """创建一个带 Start 和 End 基础骨架的标准空白工作流"""
    wf_id = f"wf_{uuid.uuid4().hex[:8]}"
    return {
        "id": wf_id,
        "name": name,
        "description": "全新的可编排 AI 工作流",
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "name": "开始输入",
                "config": {
                    "fields": {
                        "input_text": {
                            "type": "string",
                            "default": "请为我的新产品起一个好听的名字"
                        }
                    }
                }
            },
            {
                "id": "llm_1",
                "type": "llm",
                "name": "大模型处理",
                "config": {
                    "model": "glm-4-flash",
                    "system": "你是一个充满创意和商业洞察力的品牌起名大师。",
                    "prompt": "请基于用户的需求【{{start.input_text}}】，构思 3 个好听、有寓意的品牌名并附上命名理由："
                }
            },
            {
                "id": "end",
                "type": "end",
                "name": "结果呈现",
                "config": {
                    "response": "### 💡 智能品牌命名建议\n\n{{llm_1.text}}"
                }
            }
        ],
        "edges": [
            {"source": "start", "target": "llm_1"},
            {"source": "llm_1", "target": "end"}
        ]
    }


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
