import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('config.env')

def test_openrouter_direct():
    """直接测试OpenRouter API"""
    api_key = os.getenv('GROK_API_KEY')
    if not api_key:
        print("错误: 未找到GROK_API_KEY")
        return

    print(f"API密钥: {api_key}")
    print(f"密钥格式检查: {'OpenRouter' if api_key.startswith('sk-or-') else '未知格式'}")

    # 测试简单的API调用
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Resume Analyzer"
    }

    # 尝试不同的模型名称
    models_to_test = [
        "x-ai/grok-beta",
        "anthropic/claude-3.5-sonnet:beta",
        "openai/gpt-3.5-turbo",
        "meta-llama/llama-3.2-3b-instruct:free"
    ]

    for model_name in models_to_test:
        print(f"\n尝试模型: {model_name}")
        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": "Hello, respond with just 'OK'"}
            ],
            "max_tokens": 10
        }

    print(f"请求URL: {url}")
    print("测试多个模型...")

    for model_name in models_to_test:
        print(f"\n尝试模型: {model_name}")
        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": "Hello, respond with just 'OK'"}
            ],
            "max_tokens": 10
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            print(f"  状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 成功! 可用模型: {model_name}")
                break
            else:
                print(f"  ❌ 失败: {response.text[:100]}")
        except Exception as e:
            print(f"  异常: {str(e)}")

    # 也尝试原始的模型名称
    print(f"\n尝试原始模型: x-ai/grok-4-fast:free")
    data = {
        "model": "x-ai/grok-4-fast:free",
        "messages": [
            {"role": "user", "content": "Hello, respond with just 'OK'"}
        ],
        "max_tokens": 10
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.text}")
    except Exception as e:
        print(f"  异常: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("OpenRouter 直接API测试")
    print("=" * 60)
    test_openrouter_direct()