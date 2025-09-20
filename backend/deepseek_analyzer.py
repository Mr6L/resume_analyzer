from openai import OpenAI
import logging
import traceback
from typing import Dict, List
import json

# 配置日志
logger = logging.getLogger(__name__)


class DeepSeekAnalyzer:
    """通用AI分析器（支持DeepSeek和Grok）"""

    def __init__(self, api_key: str, use_grok: bool = True):
        logger.info("🤖 初始化AI分析器...")
        try:
            if use_grok:
                # 使用Grok API
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.x-ai.com/v1"
                )
                self.model_name = "x-ai/grok-4-fast:free"
                logger.info("✅ Grok客户端初始化成功")
            else:
                # 使用DeepSeek API
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com"
                )
                self.model_name = "deepseek-chat"
                logger.info("✅ DeepSeek客户端初始化成功")
        except Exception as e:
            logger.error(f"❌ AI客户端初始化失败: {str(e)}")
            raise
        self.system_prompt = """
你是一个专业的简历分析师，请根据用户提供的简历内容，提供详细的修改建议。

请从以下几个方面进行分析：
1. 个人信息完整性
2. 教育背景描述
3. 工作经历描述
4. 技能展示
5. 项目经历描述
6. 整体格式和结构
7. 语言表达和专业性

对于每个方面，请提供：
- 现状分析
- 具体问题指出
- 改进建议
- 优化后的示例（如适用）

请用中文回答，语言要专业、具体、可操作。
"""

    def analyze_resume(self, resume_data: Dict) -> Dict:
        """分析简历并提供建议"""
        logger.info("🤖 开始AI分析简历...")

        try:
            # 构造用户输入
            logger.debug("📝 格式化简历数据...")
            user_content = self._format_resume_for_analysis(resume_data)
            logger.debug(f"📏 输入内容长度: {len(user_content)} 字符")

            logger.info("🌐 调用AI API...")
            logger.debug(f"🎯 使用模型: {self.model_name}")

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=2000,
                timeout=300  # 增加超时时间到5分钟
            )

            logger.info("✅ API调用成功")

            # 解析响应
            analysis_result = response.choices[0].message.content
            logger.debug(f"📥 响应长度: {len(analysis_result)} 字符")

            # 结构化分析结果
            logger.debug("🔄 结构化分析结果...")
            structured_result = self._structure_analysis(analysis_result)

            logger.info("🎉 简历分析完成")
            return {
                'success': True,
                'analysis': structured_result,
                'raw_analysis': analysis_result
            }

        except Exception as e:
            logger.error(f"❌ AI分析失败: {str(e)}")
            logger.error(f"📋 异常详情: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f"分析失败: {str(e)}",
                'analysis': None,
                'raw_analysis': None
            }

    def _format_resume_for_analysis(self, resume_data: Dict) -> str:
        """格式化简历数据供分析"""
        formatted_content = "以下是简历内容:\n\n"

        # 个人信息
        if resume_data.get('personal_info'):
            formatted_content += "个人信息:\n"
            for key, value in resume_data['personal_info'].items():
                formatted_content += f"{key}: {value}\n"
            formatted_content += "\n"

        # 教育背景
        if resume_data.get('education'):
            formatted_content += "教育背景:\n"
            for edu in resume_data['education']:
                formatted_content += f"- {edu.get('内容', '')}\n"
            formatted_content += "\n"

        # 工作经历
        if resume_data.get('work_experience'):
            formatted_content += "工作经历:\n"
            for work in resume_data['work_experience']:
                formatted_content += f"- {work.get('内容', '')}\n"
            formatted_content += "\n"

        # 技能
        if resume_data.get('skills'):
            formatted_content += "技能:\n"
            for skill in resume_data['skills']:
                formatted_content += f"- {skill}\n"
            formatted_content += "\n"

        # 项目经历
        if resume_data.get('projects'):
            formatted_content += "项目经历:\n"
            for project in resume_data['projects']:
                formatted_content += f"- {project.get('内容', '')}\n"
            formatted_content += "\n"

        return formatted_content

    def _structure_analysis(self, analysis_text: str) -> Dict:
        """结构化分析结果"""
        try:
            # 简单的结构化处理
            sections = {
                '个人信息': '',
                '教育背景': '',
                '工作经历': '',
                '技能展示': '',
                '项目经历': '',
                '整体建议': ''
            }

            lines = analysis_text.split('\n')
            current_section = '整体建议'

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # 检查是否是新的章节标题
                for section in sections.keys():
                    if section in line or any(keyword in line for keyword in ['个人信息', '教育', '工作', '技能', '项目', '整体']):
                        current_section = section
                        break

                sections[current_section] += line + '\n'

            # 清理空的部分
            structured = {k: v.strip() for k, v in sections.items() if v.strip()}

            return structured

        except Exception:
            # 如果结构化失败，返回原始文本
            return {'整体分析': analysis_text}

    def generate_job_recommendations(self, resume_data: Dict) -> Dict:
        """根据简历推荐合适的岗位"""
        try:
            job_prompt = """
基于提供的简历内容，请推荐5个最适合的岗位，并说明推荐理由。

对于每个推荐岗位，请提供：
1. 岗位名称
2. 推荐理由
3. 匹配度（1-10分）
4. 需要加强的技能

请用中文回答，格式要清晰。
"""

            user_content = self._format_resume_for_analysis(resume_data)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": job_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=1500,
                timeout=300  # 增加超时时间到5分钟
            )

            recommendations = response.choices[0].message.content

            return {
                'success': True,
                'recommendations': recommendations
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"岗位推荐失败: {str(e)}",
                'recommendations': None
            }