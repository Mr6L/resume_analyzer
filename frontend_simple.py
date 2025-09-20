import gradio as gr
import requests
import json

def analyze_resume(file):
    if file is None:
        print("[前端] 没有上传文件")
        return "请先上传简历文件", "", ""

    try:
        # 控制台调试信息
        print(f"[前端] 开始处理文件: {file.name}")
        print(f"[前端] 文件路径: {file.name}")

        # 检查文件是否存在
        import os
        if not os.path.exists(file.name):
            print(f"[前端] 错误: 文件不存在 {file.name}")
            return "文件不存在", "", ""

        file_size = os.path.getsize(file.name)
        print(f"[前端] 文件大小: {file_size} bytes")

        print("[前端] 准备发送HTTP请求...")
        files = {'file': (file.name, open(file.name, 'rb'))}

        # 记录请求开始时间
        import time
        start_time = time.time()

        # 创建session并禁用代理，确保本地请求不走代理
        session = requests.Session()
        session.proxies = {
            'http': None,
            'https': None
        }
        session.trust_env = False  # 忽略环境变量中的代理设置

        print("[前端] 正在调用后端API（绕过代理）...")
        response = session.post("http://127.0.0.1:5000/full_analysis", files=files, timeout=360)  # 增加到6分钟
        files['file'][1].close()

        end_time = time.time()
        duration = end_time - start_time
        print(f"[前端] API调用完成，耗时: {duration:.2f}秒")
        print(f"[前端] HTTP状态码: {response.status_code}")

        if response.status_code == 200:
            print("[前端] 开始解析响应JSON...")
            result = response.json()
            print(f"[前端] 响应字段: {list(result.keys())}")

            if result.get('success'):
                print("[前端] 分析成功，开始格式化结果...")

                # 格式化结果
                parsed_data = result.get('parsed_data', {})
                analysis = result.get('analysis', {})
                recommendations = result.get('recommendations', '')

                print(f"[前端] 解析数据字段: {list(parsed_data.keys()) if parsed_data else '无'}")
                print(f"[前端] 分析结果字段: {list(analysis.keys()) if analysis else '无'}")
                print(f"[前端] 推荐结果长度: {len(recommendations) if recommendations else 0}")

                # 格式化个人信息
                parsed_text = "解析结果:\n\n"
                if parsed_data.get('personal_info'):
                    parsed_text += "个人信息:\n"
                    for k, v in parsed_data['personal_info'].items():
                        parsed_text += f"  {k}: {v}\n"

                if parsed_data.get('education'):
                    parsed_text += "\n教育背景:\n"
                    for edu in parsed_data['education']:
                        parsed_text += f"  - {edu.get('内容', '')}\n"

                if parsed_data.get('work_experience'):
                    parsed_text += "\n工作经历:\n"
                    for work in parsed_data['work_experience']:
                        parsed_text += f"  - {work.get('内容', '')}\n"

                if parsed_data.get('skills'):
                    parsed_text += "\n技能:\n"
                    for skill in parsed_data['skills']:
                        parsed_text += f"  - {skill}\n"

                # 格式化分析结果
                analysis_text = "AI分析建议:\n\n"
                if analysis:
                    for section, content in analysis.items():
                        analysis_text += f"{section}:\n{content}\n\n"
                else:
                    analysis_text = "暂无分析结果"

                # 格式化推荐
                rec_text = f"岗位推荐:\n\n{recommendations}" if recommendations else "暂无岗位推荐"

                print("[前端] 结果格式化完成")
                return parsed_text, analysis_text, rec_text
            else:
                error = result.get('error', '未知错误')
                print(f"[前端] 后端返回错误: {error}")
                return f"分析失败: {error}", "", ""
        else:
            print(f"[前端] HTTP请求失败: {response.status_code}")
            try:
                error_text = response.text[:500]  # 只显示前500字符
                print(f"[前端] 错误详情: {error_text}")
            except:
                pass
            return f"HTTP错误: {response.status_code}", "", ""
    except Exception as e:
        print(f"[前端] 发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"处理异常: {str(e)}", "", ""

def check_backend():
    try:
        # 创建session并禁用代理
        session = requests.Session()
        session.proxies = {
            'http': None,
            'https': None
        }
        session.trust_env = False  # 忽略环境变量中的代理设置

        response = session.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            return "后端服务正常"
        else:
            return f"后端异常: {response.status_code}"
    except:
        return "无法连接后端服务"

# 创建界面
with gr.Blocks(title="简历分析系统") as app:
    gr.Markdown("# 智能简历分析系统")
    gr.Markdown("上传Word格式简历，获得AI分析和建议")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 文件上传")
            file_input = gr.File(
                label="选择简历文件 (.docx)",
                file_types=[".docx"]
            )
            analyze_btn = gr.Button("开始分析", variant="primary", size="lg")

            gr.Markdown("### 服务状态")
            status_btn = gr.Button("检查后端服务")
            status_output = gr.Textbox(label="状态信息", lines=2)

        with gr.Column(scale=2):
            gr.Markdown("### 分析结果")

            with gr.Tabs():
                with gr.TabItem("简历解析"):
                    parsed_output = gr.Textbox(
                        label="解析结果",
                        lines=15,
                        value="等待上传文件..."
                    )

                with gr.TabItem("AI分析建议"):
                    analysis_output = gr.Textbox(
                        label="分析建议",
                        lines=15,
                        value="等待分析结果..."
                    )

                with gr.TabItem("岗位推荐"):
                    recommendations_output = gr.Textbox(
                        label="岗位推荐",
                        lines=15,
                        value="等待推荐结果..."
                    )

    # 绑定事件
    analyze_btn.click(
        fn=analyze_resume,
        inputs=[file_input],
        outputs=[parsed_output, analysis_output, recommendations_output]
    )

    status_btn.click(
        fn=check_backend,
        outputs=[status_output]
    )

if __name__ == "__main__":
    # 设置编码避免Windows控制台问题
    import sys
    import os
    import codecs

    # 设置标准输出编码
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')

    print("=== 简历分析系统前端 ===")
    print("1. 检查后端服务...")
    backend_status = check_backend()
    print(f"   后端状态: {backend_status}")

    if "正常" not in backend_status:
        print("   警告: 后端服务不可用!")
        print("   请确保后端服务已启动: python backend/app.py")

    print("2. 启动前端界面...")
    print("   前端地址: http://127.0.0.1:7864")
    print("   按 Ctrl+C 停止服务")
    print("=" * 40)

    app.launch(
        server_name="127.0.0.1",
        server_port=7864,
        share=False,
        show_error=True,
        inbrowser=False
    )