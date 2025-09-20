#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API测试脚本
用于检查API连接和可用模型
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 加载配置
load_dotenv('config.env')

def test_deepseek_api():
    """测试DeepSeek API连接"""
    api_key = os.getenv('DEEPSEEK_API_KEY')

    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print("错误: 请在config.env中设置有效的DEEPSEEK_API_KEY")
        return False, None

    print(f"使用API密钥: {api_key[:10]}...")

    try:
        # 初始化客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        print("DeepSeek客户端初始化成功")

        # 测试不同的模型名称
        models_to_test = [
            "deepseek-reasoner",
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-v2",
            "deepseek-v2.5"
        ]

        for model in models_to_test:
            print(f"\n测试模型: {model}")
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "你好，请简单介绍一下你自己。"}
                    ],
                    max_tokens=100,
                    timeout=30
                )

                content = response.choices[0].message.content
                print(f"模型 {model} 可用")
                print(f"响应示例: {content[:100]}...")
                return True, model

            except Exception as e:
                print(f"模型 {model} 不可用: {str(e)}")
                continue

        print("\n所有测试的模型都不可用")
        return False, None

    except Exception as e:
        print(f"API连接失败: {str(e)}")
        return False, None

def test_simple_request():
    """测试简单的API请求"""
    api_key = os.getenv('DEEPSEEK_API_KEY')

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 使用最基本的配置测试
        response = client.chat.completions.create(
            model="deepseek-chat",  # 使用最常见的模型名
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=50
        )

        print("基础API测试成功")
        print(f"响应: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"基础API测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始DeepSeek API测试...")
    print("=" * 50)

    # 测试API连接和模型
    success, working_model = test_deepseek_api()

    if success:
        print(f"\n找到可用模型: {working_model}")
        print(f"建议在代码中使用模型: {working_model}")
    else:
        print("\n尝试基础测试...")
        if test_simple_request():
            print("建议使用模型: deepseek-chat")
        else:
            print("API完全不可用，请检查:")
            print("   1. API密钥是否正确")
            print("   2. 账户是否有余额")
            print("   3. 网络连接是否正常")
            print("   4. API服务是否可用")

    print("\n" + "=" * 50)
    print("测试完成")