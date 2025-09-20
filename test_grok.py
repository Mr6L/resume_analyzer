#!/usr/bin/env python3
"""
测试Grok API连接性
"""
from backend.deepseek_analyzer import DeepSeekAnalyzer
from dotenv import load_dotenv
import os

# 加载配置
load_dotenv('config.env')

def test_grok_api():
    """测试Grok API"""
    print("🧪 测试Grok API连接...")

    # 获取API密钥
    api_key = os.getenv('GROK_API_KEY')
    if not api_key:
        print("❌ 错误: 未找到GROK_API_KEY环境变量")
        return False

    print(f"✅ API密钥已加载: {api_key[:10]}...")

    try:
        # 初始化分析器（使用Grok）
        print("🤖 初始化Grok分析器...")
        analyzer = DeepSeekAnalyzer(api_key, use_grok=True)

        # 测试简单的分析
        print("📝 测试简单文本分析...")
        test_data = {
            'personal_info': {'姓名': '测试用户', '邮箱': 'test@example.com'},
            'work_experience': [{'内容': '软件开发工程师，3年Python经验'}],
            'skills': ['Python', 'Flask', 'MySQL']
        }

        print("🚀 调用Grok API...")
        result = analyzer.analyze_resume(test_data)

        if result.get('success'):
            print("✅ Grok API测试成功！")
            print(f"📊 分析结果长度: {len(result.get('raw_analysis', ''))}")
            print("🎯 结果预览:")
            preview = result.get('raw_analysis', '')[:200]
            print(f"   {preview}...")
            return True
        else:
            print(f"❌ API调用失败: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_grok_api()
    if success:
        print("\n🎉 Grok API配置正确，可以开始使用系统了！")
    else:
        print("\n💥 Grok API配置有问题，请检查API密钥和网络连接")