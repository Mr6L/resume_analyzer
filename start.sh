#!/bin/bash

echo "正在启动简历分析系统..."
echo

echo "[1/2] 启动后端服务..."
cd backend
python app.py &
BACKEND_PID=$!

echo "等待后端服务启动..."
sleep 3

echo "[2/2] 启动前端界面..."
cd ../frontend
python gradio_app.py &
FRONTEND_PID=$!

echo
echo "启动完成！"
echo "后端服务: http://127.0.0.1:5000"
echo "前端界面: http://127.0.0.1:7860"
echo
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait