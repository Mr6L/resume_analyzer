import gradio as gr
import requests
import json
import os
import tempfile
import logging
import traceback
from datetime import datetime
from typing import Optional, Tuple

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('frontend.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class ResumeAnalyzerFrontend:
    """简历分析器前端界面"""

    def __init__(self, backend_url: str = "http://127.0.0.1:5000"):
        self.backend_url = backend_url
        logger.info(f"🚀 初始化前端界面，后端地址: {backend_url}")

    def analyze_resume(self, file) -> Tuple[str, str, str]:
        """分析上传的简历文件"""
        logger.info("📋 开始分析简历文件")

        if file is None:
            logger.warning("⚠️ 没有文件上传")
            return "请先上传简历文件", "", ""

        try:
            logger.info(f"📁 处理文件: {file.name}")
            file_size = os.path.getsize(file.name) if os.path.exists(file.name) else 0
            logger.info(f"📊 文件大小: {file_size} bytes")

            # 准备文件上传
            logger.debug("🔄 准备文件上传...")
            files = {'file': (file.name, open(file.name, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}

            # 调用后端全分析接口
            logger.info(f"🌐 发送请求到: {self.backend_url}/full_analysis")
            start_time = datetime.now()

            response = requests.post(f"{self.backend_url}/full_analysis", files=files, timeout=120)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"⏱️ 请求耗时: {duration:.2f}秒")

            # 关闭文件
            files['file'][1].close()
            logger.debug("✅ 文件句柄已关闭")

            logger.info(f"📡 后端响应状态码: {response.status_code}")

            if response.status_code == 200:
                logger.debug("📥 解析响应JSON...")
                result = response.json()
                logger.debug(f"📋 响应字段: {list(result.keys())}")

                if result.get('success'):
                    logger.info("✅ 分析成功，开始格式化结果")

                    # 格式化解析结果
                    logger.debug("🔄 格式化解析结果...")
                    parsed_info = self._format_parsed_data(result.get('parsed_data'))

                    # 格式化分析结果
                    logger.debug("🔄 格式化分析结果...")
                    analysis_text = self._format_analysis(result.get('analysis'))

                    # 格式化推荐结果
                    logger.debug("🔄 格式化推荐结果...")
                    recommendations_text = self._format_recommendations(result.get('recommendations'))

                    # 检查错误信息
                    errors = result.get('errors', {})
                    if errors.get('analysis_error'):
                        logger.warning(f"⚠️ AI分析有错误: {errors['analysis_error']}")
                    if errors.get('recommendation_error'):
                        logger.warning(f"⚠️ 岗位推荐有错误: {errors['recommendation_error']}")

                    logger.info("🎉 分析完成并返回结果")
                    return parsed_info, analysis_text, recommendations_text

                else:
                    error_msg = result.get('error', '未知错误')
                    logger.error(f"❌ 后端返回错误: {error_msg}")
                    return f"分析失败: {error_msg}", "", ""

            else:
                logger.error(f"❌ HTTP请求失败: {response.status_code}")
                try:
                    error_detail = response.text
                    logger.error(f"❌ 错误详情: {error_detail}")
                except:
                    pass
                return f"请求失败: HTTP {response.status_code}", "", ""

        except requests.exceptions.Timeout:
            logger.error("⏰ 请求超时")
            return "请求超时，请检查网络连接或稍后重试", "", ""
        except requests.exceptions.ConnectionError:
            logger.error("🔌 连接错误")
            return "无法连接到后端服务，请确认后端服务已启动", "", ""
        except Exception as e:
            logger.error(f"💥 分析过程发生异常: {str(e)}")
            logger.error(f"📋 异常详情: {traceback.format_exc()}")
            return f"分析过程出错: {str(e)}", "", ""

    def _format_parsed_data(self, parsed_data: dict) -> str:
        """格式化解析的简历数据"""
        if not parsed_data:
            return "未能解析出有效信息"

        formatted_text = "## 📋 简历信息解析结果\n\n"

        # 个人信息
        if parsed_data.get('personal_info'):
            formatted_text += "### 👤 个人信息\n"
            for key, value in parsed_data['personal_info'].items():
                formatted_text += f"- **{key}**: {value}\n"
            formatted_text += "\n"

        # 教育背景
        if parsed_data.get('education'):
            formatted_text += "### 🎓 教育背景\n"
            for edu in parsed_data['education']:
                formatted_text += f"- {edu.get('内容', '')}\n"
            formatted_text += "\n"

        # 工作经历
        if parsed_data.get('work_experience'):
            formatted_text += "### 💼 工作经历\n"
            for work in parsed_data['work_experience']:
                formatted_text += f"- {work.get('内容', '')}\n"
            formatted_text += "\n"

        # 技能
        if parsed_data.get('skills'):
            formatted_text += "### 🛠️ 技能\n"
            for skill in parsed_data['skills']:
                formatted_text += f"- {skill}\n"
            formatted_text += "\n"

        # 项目经历
        if parsed_data.get('projects'):
            formatted_text += "### 📊 项目经历\n"
            for project in parsed_data['projects']:
                formatted_text += f"- {project.get('内容', '')}\n"
            formatted_text += "\n"

        return formatted_text

    def _format_analysis(self, analysis: dict) -> str:
        """格式化分析结果"""
        if not analysis:
            return "暂无分析结果"

        formatted_text = "## 🔍 AI智能分析建议\n\n"

        for section, content in analysis.items():
            if content.strip():
                formatted_text += f"### {section}\n{content}\n\n"

        return formatted_text

    def _format_recommendations(self, recommendations: str) -> str:
        """格式化岗位推荐"""
        if not recommendations:
            return "暂无岗位推荐"

        formatted_text = "## 💼 岗位推荐\n\n"
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
        with gr.Blocks(
            title="智能简历分析系统",
            theme=gr.themes.Soft(),
            css="""
            .gradio-container {
                max-width: 1200px;
                margin: auto;
            }
            .upload-area {
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                background-color: #fafafa;
            }
            .output-scroll {
                max-height: 420px;
                overflow-y: auto;
                padding-right: 12px;
                background: #f8f9fa;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                padding: 16px;
            }
            """
        ) as interface:

            gr.HTML("""
            <div style="text-align: center; padding: 20px;">
                <h1>🚀 智能简历分析系统</h1>
                <p>上传您的Word格式简历，获得AI驱动的专业分析和改进建议</p>
            </div>
            """)

            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("### 📤 上传简历")
                    file_input = gr.File(
                        label="选择简历文件 (.docx)",
                        file_types=[".docx"],
                        file_count="single"
                    )

                    analyze_btn = gr.Button(
                        "🔍 开始分析",
                        variant="primary",
                        size="lg"
                    )

                    status_btn = gr.Button(
                        "🔧 检查服务状态",
                        variant="secondary"
                    )

                    status_output = gr.Textbox(
                        label="服务状态",
                        lines=2,
                        interactive=False
                    )

                with gr.Column(scale=2):
                    gr.HTML("### 📊 分析结果")

                    with gr.Tabs():
                        with gr.TabItem("📋 简历解析"):
                            parsed_output = gr.Markdown(
                                label="解析结果",
                                value="请上传简历文件进行分析...",
                                elem_classes=["output-scroll"]
                            )

                        with gr.TabItem("🔍 AI分析建议"):
                            analysis_output = gr.Markdown(
                                label="分析建议",
                                value="等待分析结果...",
                                elem_classes=["output-scroll"]
                            )

                        with gr.TabItem("💼 岗位推荐"):
                            recommendations_output = gr.Markdown(
                                label="岗位推荐",
                                value="等待推荐结果...",
                                elem_classes=["output-scroll"]
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

            # 示例和说明
            gr.HTML("""
            <div style="margin-top: 30px; padding: 20px; background-color: #f0f8ff; border-radius: 10px;">
                <h3>📖 使用说明</h3>
                <ol>
                    <li><strong>上传简历</strong>: 选择Word格式(.docx)的简历文件</li>
                    <li><strong>开始分析</strong>: 点击"开始分析"按钮，系统将自动解析简历内容</li>
                    <li><strong>查看结果</strong>: 在右侧三个标签页中查看解析结果、AI分析建议和岗位推荐</li>
                    <li><strong>状态检查</strong>: 如果遇到问题，可以点击"检查服务状态"确认后端服务是否正常</li>
                </ol>

                <h3>⚠️ 注意事项</h3>
                <ul>
                    <li>仅支持Word格式(.docx)文件</li>
                    <li>文件大小不超过16MB</li>
                    <li>请确保简历内容完整且格式规范</li>
                    <li>分析结果仅供参考，请结合实际情况使用</li>
                </ul>
            </div>
            """)

        return interface


def main():
    """主函数"""
    # 创建前端应用
    app = ResumeAnalyzerFrontend()

    # 检查后端服务状态
    print("正在启动前端界面...")
    status = app.check_backend_status()
    print(f"后端服务状态: {status}")

    if "错误" in status or "失败" in status:
        print("警告: 后端服务不可用，请先启动后端服务 (python backend/app.py)")

    # 创建并启动界面
    interface = app.create_interface()

    print("启动Gradio界面...")
    print("界面地址: http://127.0.0.1:7860")
    print("按 Ctrl+C 停止服务")

    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()