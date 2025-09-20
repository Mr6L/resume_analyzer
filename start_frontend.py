#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量避免编码问题
os.environ['PYTHONIOENCODING'] = 'utf-8'

import gradio as gr
import requests

def analyze_resume(file):
    """简单的文件分析函数"""
    if file is None:
        return "请上传文件", "请上传文件", "请上传文件"

    try:
        # 调用后端API
        files = {'file': (file.name, open(file.name, 'rb'))}
        response = requests.post("http://127.0.0.1:5000/full_analysis", files=files, timeout=60)
        files['file'][1].close()

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                # 简单格式化
                parsed = str(result.get('parsed_data', ''))
                analysis = str(result.get('analysis', ''))
                recommendations = str(result.get('recommendations', ''))
                return parsed, analysis, recommendations
            else:
                error = result.get('error', '未知错误')
                return f"错误: {error}", "", ""
        else:
            return f"HTTP错误: {response.status_code}", "", ""
    except Exception as e:
        return f"异常: {str(e)}", "", ""

def check_backend():
    """检查后端状态"""
    try:
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        return "后端正常" if response.status_code == 200 else f"后端异常: {response.status_code}"
    except:
        return "无法连接后端"

# 创建界面
with gr.Blocks(title="简历分析") as demo:
    gr.Markdown("# 简历分析系统")

    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="上传简历(.docx)", file_types=[".docx"])
            analyze_btn = gr.Button("开始分析")
            status_btn = gr.Button("检查后端")
            status_text = gr.Textbox(label="状态", lines=1)

        with gr.Column():
            with gr.Tabs():
                with gr.TabItem("解析结果"):
                    parsed_output = gr.Textbox(label="解析", lines=10)
                with gr.TabItem("AI分析"):
                    analysis_output = gr.Textbox(label="分析", lines=10)
                with gr.TabItem("岗位推荐"):
                    recommendations_output = gr.Textbox(label="推荐", lines=10)

    # 绑定事件
    analyze_btn.click(analyze_resume, inputs=[file_input], outputs=[parsed_output, analysis_output, recommendations_output])
    status_btn.click(check_backend, outputs=[status_text])

if __name__ == "__main__":
    print("启动简历分析系统...")
    print("检查后端连接...")
    print(check_backend())
    print("启动前端界面...")
    demo.launch(server_name="127.0.0.1", server_port=7861, share=False)