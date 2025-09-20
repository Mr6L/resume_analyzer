#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版前端启动脚本
解决Windows控制台编码问题
"""

import gradio as gr
import requests
import json
import os
from typing import Optional, Tuple

class SimpleResumeAnalyzer:
    """简化的简历分析器前端"""

    def __init__(self, backend_url: str = "http://127.0.0.1:5000"):
        self.backend_url = backend_url

    def analyze_resume(self, file) -> Tuple[str, str, str]:
        """分析上传的简历文件"""
        if file is None:
            return "请先上传简历文件", "", ""

        try:
            print(f"处理文件: {file.name}")

            # 准备文件上传
            files = {'file': (file.name, open(file.name, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}

            print("发送请求到后端...")
            response = requests.post(f"{self.backend_url}/full_analysis", files=files, timeout=120)

            # 关闭文件
            files['file'][1].close()

            print(f"后端响应状态: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                if result.get('success'):
                    print("分析成功，格式化结果...")

                    # 格式化解析结果
                    parsed_info = self._format_parsed_data(result.get('parsed_data'))
                    analysis_text = self._format_analysis(result.get('analysis'))
                    recommendations_text = self._format_recommendations(result.get('recommendations'))

                    return parsed_info, analysis_text, recommendations_text
                else:
                    error_msg = result.get('error', '未知错误')
                    print(f"后端返回错误: {error_msg}")
                    return f"分析失败: {error_msg}", "", ""
            else:
                print(f"HTTP请求失败: {response.status_code}")
                return f"请求失败: HTTP {response.status_code}", "", ""

        except requests.exceptions.Timeout:
            print("请求超时")
            return "请求超时，请检查网络连接或稍后重试", "", ""
        except requests.exceptions.ConnectionError:
            print("连接错误")
            return "无法连接到后端服务，请确认后端服务已启动", "", ""
        except Exception as e:
            print(f"分析过程发生异常: {str(e)}")
            return f"分析过程出错: {str(e)}", "", ""

    def _format_parsed_data(self, parsed_data: dict) -> str:
        """格式化解析的简历数据"""
        if not parsed_data:
            return "未能解析出有效信息"

        formatted_text = "## 简历信息解析结果\n\n"

        # 个人信息
        if parsed_data.get('personal_info'):
            formatted_text += "### 个人信息\n"
            for key, value in parsed_data['personal_info'].items():
                formatted_text += f"- **{key}**: {value}\n"
            formatted_text += "\n"

        # 教育背景
        if parsed_data.get('education'):
            formatted_text += "### 教育背景\n"
            for edu in parsed_data['education']:
                formatted_text += f"- {edu.get('内容', '')}\n"
            formatted_text += "\n"

        # 工作经历
        if parsed_data.get('work_experience'):
            formatted_text += "### 工作经历\n"
            for work in parsed_data['work_experience']:
                formatted_text += f"- {work.get('内容', '')}\n"
            formatted_text += "\n"

        # 技能
        if parsed_data.get('skills'):
            formatted_text += "### 技能\n"
            for skill in parsed_data['skills']:
                formatted_text += f"- {skill}\n"
            formatted_text += "\n"

        # 项目经历
        if parsed_data.get('projects'):
            formatted_text += "### 项目经历\n"
            for project in parsed_data['projects']:
                formatted_text += f"- {project.get('内容', '')}\n"
            formatted_text += "\n"

        return formatted_text

    def _format_analysis(self, analysis: dict) -> str:
        """格式化分析结果"""
        if not analysis:
            return "暂无分析结果"

        formatted_text = "## AI智能分析建议\n\n"
        for section, content in analysis.items():
            if content.strip():
                formatted_text += f"### {section}\n{content}\n\n"

        return formatted_text

    def _format_recommendations(self, recommendations: str) -> str:
        """格式化岗位推荐"""
        if not recommendations:
            return "暂无岗位推荐"

        formatted_text = "## 岗位推荐\n\n"
        formatted_text += recommendations
        return formatted_text

    def check_backend_status(self) -> str:
        """检查后端服务状态"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                return "后端服务连接正常"
            else:
                return f"后端服务异常 (状态码: {response.status_code})"
        except Exception as e:
            return f"无法连接后端服务: {str(e)}"

    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="智能简历分析系统") as interface:

            gr.HTML("""
            <div style="text-align: center; padding: 20px;">
                <h1>智能简历分析系统</h1>
                <p>上传您的Word格式简历，获得AI驱动的专业分析和改进建议</p>
            </div>
            """)

            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("### 上传简历")
                    file_input = gr.File(
                        label="选择简历文件 (.docx)",
                        file_types=[".docx"],
                        file_count="single"
                    )

                    analyze_btn = gr.Button("开始分析", variant="primary", size="lg")
                    status_btn = gr.Button("检查服务状态", variant="secondary")
                    status_output = gr.Textbox(label="服务状态", lines=2, interactive=False)

                with gr.Column(scale=2):
                    gr.HTML("### 分析结果")

                    with gr.Tabs():
                        with gr.TabItem("简历解析"):
                            parsed_output = gr.Markdown(
                                label="解析结果",
                                value="请上传简历文件进行分析..."
                            )

                        with gr.TabItem("AI分析建议"):
                            analysis_output = gr.Markdown(
                                label="分析建议",
                                value="等待分析结果..."
                            )

                        with gr.TabItem("岗位推荐"):
                            recommendations_output = gr.Markdown(
                                label="岗位推荐",
                                value="等待推荐结果..."
                            )

            # 事件绑定
            analyze_btn.click(
                fn=self.analyze_resume,
                inputs=[file_input],
                outputs=[parsed_output, analysis_output, recommendations_output]
            )

            status_btn.click(
                fn=self.check_backend_status,
                outputs=[status_output]
            )

        return interface

def main():
    """主函数"""
    print("启动简历分析系统前端...")

    # 创建前端应用
    app = SimpleResumeAnalyzer()

    # 检查后端服务状态
    status = app.check_backend_status()
    print(f"后端服务状态: {status}")

    # 创建并启动界面
    interface = app.create_interface()

    print("启动Gradio界面...")
    print("前端地址: http://127.0.0.1:7860")
    print("按 Ctrl+C 停止服务")

    try:
        interface.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=False,
            show_error=True,
            inbrowser=False  # 不自动打开浏览器
        )
    except Exception as e:
        print(f"启动失败: {str(e)}")

if __name__ == "__main__":
    main()