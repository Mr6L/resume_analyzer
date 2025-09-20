(base) PS C:\Users\lyp\Desktop\项目\resume_analyzer> python .\test_grok.py
🧪 测试Grok API连接...
✅ API密钥已加载: sk-or-v1-1...
🤖 初始化Grok分析器...
📝 测试简单文本分析...
🚀 调用Grok API...
❌ AI分析失败: Error code: 401 - {'error': {'message': 'User not found.', 'code': 401}}
📋 异常详情: Traceback (most recent call last):
  File "C:\Users\lyp\Desktop\项目\resume_analyzer\backend\deepseek_analyzer.py", line 70, in analyze_resume
    response = self.client.chat.completions.create(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\anaconda\Lib\site-packages\openai\_utils\_utils.py", line 286, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "E:\anaconda\Lib\site-packages\openai\resources\chat\completions\completions.py", line 1147, in create
    return self._post(
           ^^^^^^^^^^^
  File "E:\anaconda\Lib\site-packages\openai\_base_client.py", line 1259, in post
    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\anaconda\Lib\site-packages\openai\_base_client.py", line 1047, in request
    raise self._make_status_error_from_response(err.response) from None
openai.AuthenticationError: Error code: 401 - {'error': {'message': 'User not found.', 'code': 401}}

❌ API调用失败: 分析失败: Error code: 401 - {'error': {'message': 'User not found.', 'code': 401}}

💥 Grok API配置有问题，请检查API密钥和网络连接