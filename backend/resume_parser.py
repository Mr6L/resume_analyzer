import os
import logging
from docx import Document
import re
from typing import Dict, List, Optional

# 配置日志
logger = logging.getLogger(__name__)

class ResumeParser:
    """简历解析器"""

    def __init__(self):
        self.personal_keywords = ['姓名', '性别', '年龄', '电话', '邮箱', '地址', '联系方式']
        self.education_keywords = ['教育经历', '教育背景', '学历', '毕业院校', '专业']
        self.work_keywords = ['工作经历', '工作经验', '职业经历', '实习经历']
        self.skill_keywords = ['技能', '专业技能', '技术技能', '掌握技能']
        self.project_keywords = ['项目经历', '项目经验', '项目']

    def parse_resume(self, file_path: str) -> Dict:
        """解析简历文件"""
        logger.info(f"📄 开始解析简历文件: {file_path}")

        try:
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")

            logger.debug("📖 读取Word文档...")
            doc = Document(file_path)
            text_content = self._extract_text(doc)

            logger.info(f"📏 提取文本长度: {len(text_content)} 字符")
            logger.debug(f"📝 文本前200字符: {text_content[:200]}...")

            logger.debug("🔍 开始结构化解析...")
            parsed_data = {
                'personal_info': self._extract_personal_info(text_content),
                'education': self._extract_education(text_content),
                'work_experience': self._extract_work_experience(text_content),
                'skills': self._extract_skills(text_content),
                'projects': self._extract_projects(text_content),
                'raw_text': text_content
            }

            logger.info("✅ 简历解析完成")
            logger.debug(f"📊 解析结果统计: 个人信息{len(parsed_data['personal_info'])}项, "
                        f"教育经历{len(parsed_data['education'])}项, "
                        f"工作经历{len(parsed_data['work_experience'])}项, "
                        f"技能{len(parsed_data['skills'])}项, "
                        f"项目{len(parsed_data['projects'])}项")

            return parsed_data

        except Exception as e:
            logger.error(f"❌ 解析简历失败: {str(e)}")
            raise Exception(f"解析简历失败: {str(e)}")

    def _extract_text(self, doc: Document) -> str:
        """提取文档文本"""
        full_text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text.strip())
        return '\n'.join(full_text)

    def _extract_personal_info(self, text: str) -> Dict:
        """提取个人信息"""
        personal_info = {}
        lines = text.split('\n')

        # 提取邮箱
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            personal_info['邮箱'] = email_match.group()

        # 提取电话
        phone_pattern = r'(?:电话|手机|联系方式)[：:]\s*(\d{3}-?\d{4}-?\d{4}|\d{11})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            personal_info['电话'] = phone_match.group(1)

        # 提取姓名（通常在第一行或包含"姓名"的行）
        for line in lines[:5]:  # 检查前5行
            if '姓名' in line:
                name_match = re.search(r'姓名[：:]\s*([^\s]+)', line)
                if name_match:
                    personal_info['姓名'] = name_match.group(1)
                break
        else:
            # 如果没有找到"姓名"关键字，假设第一行是姓名
            if lines and len(lines[0]) < 20:
                personal_info['姓名'] = lines[0].strip()

        return personal_info

    def _extract_education(self, text: str) -> List[Dict]:
        """提取教育经历"""
        education_list = []
        lines = text.split('\n')

        education_section = self._find_section(lines, self.education_keywords)
        if education_section:
            for line in education_section:
                if any(keyword in line for keyword in ['大学', '学院', '学校', '毕业']):
                    education_list.append({'内容': line.strip()})

        return education_list

    def _extract_work_experience(self, text: str) -> List[Dict]:
        """提取工作经历"""
        work_list = []
        lines = text.split('\n')

        work_section = self._find_section(lines, self.work_keywords)
        if work_section:
            for line in work_section:
                if any(keyword in line for keyword in ['公司', '职位', '负责', '工作']):
                    work_list.append({'内容': line.strip()})

        return work_list

    def _extract_skills(self, text: str) -> List[str]:
        """提取技能"""
        skills = []
        lines = text.split('\n')

        skill_section = self._find_section(lines, self.skill_keywords)
        if skill_section:
            for line in skill_section:
                if line.strip() and not any(keyword in line for keyword in self.skill_keywords):
                    skills.append(line.strip())

        return skills

    def _extract_projects(self, text: str) -> List[Dict]:
        """提取项目经历"""
        projects = []
        lines = text.split('\n')

        project_section = self._find_section(lines, self.project_keywords)
        if project_section:
            for line in project_section:
                if line.strip() and not any(keyword in line for keyword in self.project_keywords):
                    projects.append({'内容': line.strip()})

        return projects

    def _find_section(self, lines: List[str], keywords: List[str]) -> Optional[List[str]]:
        """查找特定关键字对应的段落"""
        start_idx = None

        # 找到关键字开始的位置
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in keywords):
                start_idx = i + 1
                break

        if start_idx is None:
            return None

        # 找到下一个段落的开始位置
        end_idx = len(lines)
        all_keywords = (self.personal_keywords + self.education_keywords +
                       self.work_keywords + self.skill_keywords + self.project_keywords)

        for i in range(start_idx, len(lines)):
            if any(keyword in lines[i] for keyword in all_keywords):
                end_idx = i
                break

        return lines[start_idx:end_idx]