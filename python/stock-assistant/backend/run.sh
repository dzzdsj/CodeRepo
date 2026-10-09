#!/bin/bash
# 启动脚本：激活后端 venv 并以 reload 模式运行 uvicorn
cd "$(dirname "$0")"
source .venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
