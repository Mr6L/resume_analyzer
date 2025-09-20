#!/usr/bin/env python3
"""
测试改进后的简历解析器
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

def test_improved_parser():
    """测试改进后的解析器"""
    print("[测试] 开始测试改进后的简历解析器...")

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
        print("[结果] 解析结果如下:")
        print("="*60)

        print(f"\n[个人信息] ({len(result['personal_info'])}项):")
        for key, value in result['personal_info'].items():
            print(f"  {key}: {value}")

        print(f"\n[教育背景] ({len(result['education'])}项):")
        for i, edu in enumerate(result['education']):
            print(f"  {i+1}. {edu['内容']}")

        print(f"\n[工作经历] ({len(result['work_experience'])}项):")
        for i, work in enumerate(result['work_experience']):
            print(f"  {i+1}. {work['内容']}")

        print(f"\n[技能] ({len(result['skills'])}项):")
        for i, skill in enumerate(result['skills']):
            print(f"  {i+1}. {skill}")

        print(f"\n[项目经历] ({len(result['projects'])}项):")
        for i, project in enumerate(result['projects']):
            print(f"  {i+1}. {project['内容']}")

        print("\n" + "="*60)
        print("[统计] 解析统计:")
        print(f"  个人信息: {len(result['personal_info'])}项")
        print(f"  教育背景: {len(result['education'])}项")
        print(f"  工作经历: {len(result['work_experience'])}项")
        print(f"  技能: {len(result['skills'])}项")
        print(f"  项目经历: {len(result['projects'])}项")
        print(f"  原始文本长度: {len(result['raw_text'])}字符")

        return result

    except Exception as e:
        print(f"[错误] 解析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_improved_parser()