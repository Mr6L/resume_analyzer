# 简历分析系统

这是一个基于AI的智能简历分析系统，可以解析Word格式的简历，提供专业的修改建议和岗位推荐。

## 功能特点

- 📄 **简历解析**: 自动解析Word格式简历，提取个人信息、教育背景、工作经历等
- 🤖 **AI分析**: 集成DeepSeek API，提供专业的简历修改建议
- 💼 **岗位推荐**: 根据简历内容智能推荐合适的岗位
- 🎨 **友好界面**: 基于Gradio的直观Web界面

## 技术栈

- **前端**: Gradio
- **后端**: Python + Flask
- **文件解析**: python-docx
- **AI分析**: DeepSeek API

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `backend/app.py` 文件，将 `DEEPSEEK_API_KEY` 替换为你的实际API密钥：

```python
DEEPSEEK_API_KEY = "your_actual_api_key_here"
```

### 3. 启动后端服务

```bash
cd backend
python app.py
```

后端服务将在 `http://127.0.0.1:5000` 启动

### 4. 启动前端界面

```bash
cd frontend
python gradio_app.py
```

前端界面将在 `http://127.0.0.1:7860` 启动

## API接口

### 健康检查
- **URL**: `/health`
- **方法**: GET
- **功能**: 检查服务状态

### 完整分析
- **URL**: `/full_analysis`
- **方法**: POST
- **功能**: 上传简历文件并进行完整分析
- **参数**:
  - `file`: Word格式的简历文件

### 其他接口
- `/upload`: 单独上传文件
- `/parse`: 解析简历
- `/analyze`: AI分析
- `/recommend_jobs`: 岗位推荐

## 使用方法

1. 访问前端界面 `http://127.0.0.1:7860`
2. 上传Word格式(.docx)的简历文件
3. 点击"开始分析"按钮
4. 在三个标签页中查看：
   - 简历解析结果
   - AI分析建议
   - 岗位推荐

## 注意事项

- 仅支持Word格式(.docx)文件
- 文件大小限制为16MB
- 需要有效的DeepSeek API密钥
- 请确保简历格式规范以获得更好的解析效果

## 目录结构

```
resume_analyzer/
├── backend/                # 后端代码
│   ├── app.py             # Flask主应用
│   ├── resume_parser.py   # 简历解析器
│   └── deepseek_analyzer.py # DeepSeek API分析器
├── frontend/              # 前端代码
│   └── gradio_app.py     # Gradio界面
├── uploads/               # 上传文件目录
├── temp/                  # 临时文件目录
├── requirements.txt       # 依赖包列表
└── README.md             # 说明文档
```

## 故障排除

### 1. 后端服务无法启动
- 检查是否安装了所有依赖包
- 确认Python版本是否兼容
- 检查端口5000是否被占用

### 2. 前端无法连接后端
- 确认后端服务正在运行
- 检查防火墙设置
- 确认URL配置正确

### 3. 分析失败
- 检查DeepSeek API密钥是否有效
- 确认网络连接正常
- 检查简历文件格式是否正确

## 开发说明

如需扩展功能或修改代码，请参考以下文件：

- `backend/resume_parser.py`: 修改简历解析逻辑
- `backend/deepseek_analyzer.py`: 修改AI分析提示词
- `frontend/gradio_app.py`: 修改界面布局和交互