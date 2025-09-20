import os
import sys
from dotenv import load_dotenv

# 设置UTF-8编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 加载环境变量
load_dotenv('config.env')

sys.path.append('backend')
from deepseek_analyzer import DeepSeekAnalyzer

def test_openrouter_api():
    """测试OpenRouter API连接"""
    try:
        print("测试OpenRouter Grok API连接...")

        # 获取API密钥
        api_key = os.getenv('GROK_API_KEY')
        if not api_key:
            print("错误: 未找到GROK_API_KEY环境变量")
            return False

        print(f"API密钥已加载: {api_key[:10]}...")

        # 初始化分析器
        print("初始化OpenRouter分析器...")
        analyzer = DeepSeekAnalyzer(api_key, use_grok=True)

        # 测试简单的文本分析
        print("测试简单文本分析...")
        test_resume = {
            'raw_text': """
张三
手机: 13812345678
邮箱: zhangsan@example.com

教育经历:
2018-2022 北京大学 计算机科学与技术 本科

工作经历:
2022-2024 某互联网公司 软件工程师
- 负责后端开发
- 使用Python, Java开发

技能:
Python, Java, MySQL, Git
            """,
            'basic_info': {
                '姓名': '张三',
                '手机': '13812345678',
                '邮箱': 'zhangsan@example.com'
            }
        }

        print("调用OpenRouter API...")
        result = analyzer.analyze_resume(test_resume)

        if result['success']:
            print("API调用成功!")
            print("分析结果预览:")
            print("=" * 50)
            print(result['raw_analysis'][:200] + "...")
            print("=" * 50)
            return True
        else:
            print(f"API调用失败: {result['error']}")
            return False

    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        print("详细错误信息:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("OpenRouter Grok API 测试")
    print("=" * 60)

    success = test_openrouter_api()

    print("\n" + "=" * 60)
    if success:
        print("测试结果: 成功! OpenRouter配置正常")
        print("现在可以启动完整的简历分析系统了:")
        print("1. 启动后端: python backend/app.py")
        print("2. 启动前端: python frontend_simple.py")
    else:
        print("测试结果: 失败! OpenRouter配置有问题，请检查API密钥和网络连接")
    print("=" * 60)