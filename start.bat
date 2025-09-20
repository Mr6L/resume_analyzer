@echo off
echo 正在启动简历分析系统...
echo.

echo [1/2] 启动后端服务...
cd backend
start "后端服务" cmd /k "python app.py"

echo 等待后端服务启动...
timeout /t 3 /nobreak > nul

echo [2/2] 启动前端界面...
cd ..\frontend
start "前端界面" cmd /k "python gradio_app.py"

echo.
echo 启动完成！
echo 后端服务: http://127.0.0.1:5000
echo 前端界面: http://127.0.0.1:7860
echo.
echo 按任意键退出...
pause > nul