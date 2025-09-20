#!/usr/bin/env python3
"""
测试简化后的简历解析器
"""
import sys
import os
import codecs

# 设置编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from resume_parser import ResumeParser

def test_simplified_parser():
    """测试简化后的解析器"""
    print("[测试] 开始测试简化后的简历解析器...")

    resume_file = r"C:\Users\lyp\Desktop\戴小菲求职意向.docx"

    if not os.path.exists(resume_file):
        print(f"[错误] 文件不存在: {resume_file}")
        return

    try:
        # 初始化解析器
        parser = ResumeParser()

        # 解析简历
        print(f"[解析] 正在解析文件: {resume_file}")
        result = parser.parse_resume(resume_file)

        # 打印结果
        print("\n" + "="*60)
        print("[结果] 简化解析器结果:")
        print("="*60)

        print(f"\n[统计信息]:")
        print(f"  文本长度: {result['text_length']} 字符")
        print(f"  段落数量: {len(result['paragraphs'])} 个")
        print(f"  基本信息: {len(result['basic_info'])} 项")

        print(f"\n[基本信息]:")
        for key, value in result['basic_info'].items():
            print(f"  {key}: {value}")

        print(f"\n[原始文本]:")
        print("-" * 40)
        print(result['raw_text'])
        print("-" * 40)

        print(f"\n[段落列表] (前10个):")
        for i, para in enumerate(result['paragraphs'][:10]):
            print(f"  {i+1:2d}. {para}")

        return result

    except Exception as e:
        print(f"[错误] 解析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_simplified_parser()