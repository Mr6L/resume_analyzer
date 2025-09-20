from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import logging
import traceback
from datetime import datetime
from resume_parser import ResumeParser
from deepseek_analyzer import DeepSeekAnalyzer
from dotenv import load_dotenv

# 加载配置文件
load_dotenv('../config.env')

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('resume_analyzer.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'resume_analyzer_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

logger.info("🚀 启动简历分析系统后端服务...")

# 配置文件上传路径
UPLOAD_FOLDER = '../uploads'
TEMP_FOLDER = '../temp'

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
logger.info(f"📁 上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
logger.info(f"📁 临时目录: {os.path.abspath(TEMP_FOLDER)}")

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'docx'}

# Grok API密钥 - 从环境变量获取
GROK_API_KEY = os.getenv('GROK_API_KEY', 'YOUR_GROK_API_KEY')

if GROK_API_KEY == 'YOUR_GROK_API_KEY':
    logger.warning("⚠️  警告: 请在config.env文件中设置有效的GROK_API_KEY")
    logger.warning("   当前使用的是默认占位符密钥，AI分析功能将不可用")
else:
    logger.info(f"✅ Grok API密钥已加载: {GROK_API_KEY[:10]}...")

# 初始化解析器和分析器
try:
    resume_parser = ResumeParser()
    analyzer = DeepSeekAnalyzer(GROK_API_KEY)  # 传入Grok API密钥，类内部会适配
    logger.info("✅ 简历解析器和AI分析器初始化成功")
except Exception as e:
    logger.error(f"❌ 初始化解析器失败: {str(e)}")
    logger.error(traceback.format_exc())


def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '服务正常运行'})


@app.route('/upload', methods=['POST'])
def upload_resume():
    """上传简历文件接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件上传'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': '只支持.docx格式文件'}), 400

        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        # 保存文件
        file.save(file_path)

        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'file_id': unique_filename,
            'original_name': filename
        })

    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@app.route('/parse', methods=['POST'])
def parse_resume():
    """解析简历接口"""
    try:
        data = request.get_json()
        if not data or 'file_id' not in data:
            return jsonify({'error': '缺少file_id参数'}), 400

        file_id = data['file_id']
        file_path = os.path.join(UPLOAD_FOLDER, file_id)

        if not os.path.exists(file_path):
            return jsonify({'error': '文件不存在'}), 404

        # 解析简历
        parsed_data = resume_parser.parse_resume(file_path)

        return jsonify({
            'success': True,
            'data': parsed_data
        })

    except Exception as e:
        return jsonify({'error': f'解析失败: {str(e)}'}), 500


@app.route('/analyze', methods=['POST'])
def analyze_resume():
    """分析简历并提供建议"""
    try:
        data = request.get_json()
        if not data or 'resume_data' not in data:
            return jsonify({'error': '缺少resume_data参数'}), 400

        resume_data = data['resume_data']

        # 使用DeepSeek分析简历
        analysis_result = analyzer.analyze_resume(resume_data)

        if not analysis_result['success']:
            return jsonify({'error': analysis_result['error']}), 500

        return jsonify({
            'success': True,
            'analysis': analysis_result['analysis'],
            'raw_analysis': analysis_result['raw_analysis']
        })

    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@app.route('/recommend_jobs', methods=['POST'])
def recommend_jobs():
    """推荐岗位接口"""
    try:
        data = request.get_json()
        if not data or 'resume_data' not in data:
            return jsonify({'error': '缺少resume_data参数'}), 400

        resume_data = data['resume_data']

        # 生成岗位推荐
        recommendation_result = analyzer.generate_job_recommendations(resume_data)

        if not recommendation_result['success']:
            return jsonify({'error': recommendation_result['error']}), 500

        return jsonify({
            'success': True,
            'recommendations': recommendation_result['recommendations']
        })

    except Exception as e:
        return jsonify({'error': f'推荐失败: {str(e)}'}), 500


@app.route('/full_analysis', methods=['POST'])
def full_analysis():
    """完整分析流程：上传->解析->分析->推荐"""
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"🔍 [{request_id}] 开始完整分析流程")

    try:
        # 1. 检查文件上传
        logger.debug(f"[{request_id}] 检查文件上传...")
        if 'file' not in request.files:
            logger.error(f"[{request_id}] 没有文件上传")
            return jsonify({'error': '没有文件上传'}), 400

        file = request.files['file']
        logger.info(f"[{request_id}] 接收到文件: {file.filename}")

        if file.filename == '':
            logger.error(f"[{request_id}] 没有选择文件")
            return jsonify({'error': '没有选择文件'}), 400

        if not allowed_file(file.filename):
            logger.error(f"[{request_id}] 文件格式不支持: {file.filename}")
            return jsonify({'error': '只支持.docx格式文件'}), 400

        # 2. 保存临时文件
        logger.debug(f"[{request_id}] 保存临时文件...")
        filename = secure_filename(file.filename)
        temp_filename = f"{uuid.uuid4()}_{filename}"
        temp_file_path = os.path.join(TEMP_FOLDER, temp_filename)
        logger.info(f"[{request_id}] 临时文件路径: {temp_file_path}")

        file.save(temp_file_path)
        file_size = os.path.getsize(temp_file_path)
        logger.info(f"[{request_id}] 文件保存成功，大小: {file_size} bytes")

        try:
            # 3. 解析简历
            logger.info(f"[{request_id}] 开始解析简历...")
            parsed_data = resume_parser.parse_resume(temp_file_path)
            logger.info(f"[{request_id}] 简历解析成功")
            logger.debug(f"[{request_id}] 解析结果: {list(parsed_data.keys())}")

            # 4. AI分析
            logger.info(f"[{request_id}] 开始AI分析...")
            analysis_result = analyzer.analyze_resume(parsed_data)
            if analysis_result['success']:
                logger.info(f"[{request_id}] AI分析成功")
            else:
                logger.error(f"[{request_id}] AI分析失败: {analysis_result['error']}")

            # 5. 岗位推荐
            logger.info(f"[{request_id}] 开始岗位推荐...")
            recommendation_result = analyzer.generate_job_recommendations(parsed_data)
            if recommendation_result['success']:
                logger.info(f"[{request_id}] 岗位推荐成功")
            else:
                logger.error(f"[{request_id}] 岗位推荐失败: {recommendation_result['error']}")

            # 6. 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug(f"[{request_id}] 临时文件已删除")

            logger.info(f"[{request_id}] 完整分析流程完成")
            return jsonify({
                'success': True,
                'original_filename': filename,
                'parsed_data': parsed_data,
                'analysis': analysis_result['analysis'] if analysis_result['success'] else None,
                'recommendations': recommendation_result['recommendations'] if recommendation_result['success'] else None,
                'errors': {
                    'analysis_error': None if analysis_result['success'] else analysis_result['error'],
                    'recommendation_error': None if recommendation_result['success'] else recommendation_result['error']
                }
            })

        except Exception as e:
            # 确保删除临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.debug(f"[{request_id}] 异常时清理临时文件")
            raise e

    except Exception as e:
        logger.error(f"[{request_id}] 分析过程发生异常: {str(e)}")
        logger.error(f"[{request_id}] 异常详情: {traceback.format_exc()}")
        return jsonify({'error': f'分析失败: {str(e)}'}), 500


@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件过大，请上传小于16MB的文件'}), 413


@app.errorhandler(500)
def internal_error(e):
    """服务器内部错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500


if __name__ == '__main__':
    print("启动简历分析后端服务...")
    print(f"上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"临时目录: {os.path.abspath(TEMP_FOLDER)}")
    print("请确保已设置DeepSeek API密钥")
    app.run(host='127.0.0.1', port=5000, debug=True)