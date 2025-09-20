import os
import logging
from docx import Document
import re
from typing import Dict, List, Optional

# 配置日志
logger = logging.getLogger(__name__)

class ResumeParser:
    """简历解析器 - 简化版（只做文本提取）"""

    def __init__(self):
        # 简化后不需要复杂的关键词定义
        pass

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

            logger.debug("📝 简单提取文本内容...")
            parsed_data = {
                'raw_text': text_content,  # 主要内容
                'text_length': len(text_content),  # 文本长度
                'paragraphs': self._split_paragraphs(text_content),  # 段落列表
                'basic_info': self._extract_basic_info(text_content)  # 基本信息（简单提取）
            }

            logger.info("✅ 简历解析完成")
            logger.debug(f"📊 解析结果统计: 文本长度{parsed_data['text_length']}字符, "
                        f"段落数{len(parsed_data['paragraphs'])}个, "
                        f"基本信息{len(parsed_data['basic_info'])}项")

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

    def _split_paragraphs(self, text: str) -> List[str]:
        """分割段落"""
        paragraphs = []
        for line in text.split('\n'):
            line = line.strip()
            if line:  # 只保留非空行
                paragraphs.append(line)
        return paragraphs

    def _extract_basic_info(self, text: str) -> Dict:
        """提取基本信息（简化版）"""
        basic_info = {}

        # 只做最基本的提取，不做复杂匹配
        import re

        # 提取邮箱
        email_match = re.search(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b', text)
        if email_match:
            basic_info['邮箱'] = email_match.group(1)

        # 提取电话号码（包括各种格式）
        phone_patterns = [
            r'1[3-9]\d{9}',  # 手机号
            r'\d{3,4}[-\s]?\d{3,4}[-\s]?\d{4}',  # 固定电话
            r'\d{3}\*{4}\d{4}'  # 掩码电话
        ]
        for pattern in phone_patterns:
            phone_match = re.search(pattern, text)
            if phone_match:
                basic_info['电话'] = phone_match.group()
                break

        # 提取可能的姓名（取第一行中的中文名字）
        first_line = text.split('\n')[0] if text.split('\n') else ''
        name_match = re.search(r'([\u4e00-\u9fa5]{2,4})', first_line)
        if name_match:
            basic_info['可能的姓名'] = name_match.group(1)

        return basic_info