from flask import Flask, send_from_directory, current_app, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.env')
load_dotenv(config_path)

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///industrial_knowledge.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt_dev_secret_key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 默认1天
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # 指定token位置
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['PROPAGATE_EXCEPTIONS'] = True  # 确保JWT异常被正确传播

# 端口配置
app.config['PORT'] = int(os.getenv('PORT', 5000))

# 文件上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # 默认100MB

# PDF解析服务配置
app.config['PDF_PARSE_SERVICE_URL'] = os.getenv('PDF_PARSE_SERVICE_URL', 'http://52.183.67.209:6004/file_parse')
app.config['PDF_PARSE_TIMEOUT'] = int(os.getenv('PDF_PARSE_TIMEOUT', 600))
app.config['PDF_PARSE_METHOD'] = os.getenv('PDF_PARSE_METHOD', 'auto')
app.config['PDF_RETURN_IMAGES'] = os.getenv('PDF_RETURN_IMAGES', 'True').lower() in ('true', '1', 'yes')

# RAGFlow配置
app.config['RAGFLOW_AUTO_SYNC'] = os.getenv('RAGFLOW_AUTO_SYNC', 'True').lower() in ('true', '1', 'yes')
app.config['RAGFLOW_AUTO_PARSE'] = os.getenv('RAGFLOW_AUTO_PARSE', 'True').lower() in ('true', '1', 'yes')
app.config['RAGFLOW_CHUNK_METHOD'] = os.getenv('RAGFLOW_CHUNK_METHOD', 'naive')
app.config['RAGFLOW_PARSER_CONFIG'] = os.getenv('RAGFLOW_PARSER_CONFIG', '{"chunk_size": 1000, "chunk_overlap": 100}')
app.config['RAGFLOW_API_URL'] = os.getenv('RAGFLOW_API_URL', 'http://52.183.67.209:6002')
app.config['RAGFLOW_API_KEY'] = os.getenv('RAGFLOW_API_KEY', 'ragflow-k3YjY5Y2IwMWMxZjExZjA4ZDUwMmVjOT')
app.config['RAGFLOW_DATASET_ID'] = os.getenv('RAGFLOW_DATASET_ID', 'ddd4765c32ab11f0a1620ac4a9677486')

# 初始化扩展
db = SQLAlchemy(app)
jwt = JWTManager(app)

# 配置CORS，允许所有跨域请求，支持凭证
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# JWT错误处理
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "令牌已过期，请重新登录"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "无效的访问令牌"}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({"message": "未提供访问令牌"}), 401

@jwt.token_in_blocklist_loader
def token_in_blocklist_callback(jwt_header, jwt_payload):
    return False  # 暂时不检查黑名单

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "需要新的令牌"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"message": "令牌已被撤销"}), 401

# 导入模型
from models.user import User, Role, Permission, user_roles
from models.file import File
from models.log import OperationLog

# 导入路由
from routes.auth import auth_bp
from routes.user import user_bp
from routes.file import file_bp
from routes.log import log_bp
from routes.file_batch_delete import file_batch_delete_bp
from routes.public_files import public_files_bp

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(file_bp, url_prefix='/files')
app.register_blueprint(file_batch_delete_bp, url_prefix='/files')
app.register_blueprint(log_bp, url_prefix='/api/logs')
app.register_blueprint(public_files_bp, url_prefix='/public')

@app.route('/')
def index():
    return {'message': '工业知识库系统API服务运行正常'}

# 处理上传文件的静态资源访问
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 用于调试 - 显示当前配置的上传目录路径
@app.route('/debug/paths')
def debug_paths():
    upload_folder = app.config['UPLOAD_FOLDER']
    md_folder = os.path.join(upload_folder, 'md')
    
    example_paths = {
        'UPLOAD_FOLDER': upload_folder,
        'MD_FOLDER': md_folder,
        'UPLOAD_FOLDER_EXISTS': os.path.exists(upload_folder),
        'MD_FOLDER_EXISTS': os.path.exists(md_folder)
    }
    
    # 列出md目录下的所有目录
    if os.path.exists(md_folder):
        example_paths['MD_SUBDIRS'] = [d for d in os.listdir(md_folder) 
                                     if os.path.isdir(os.path.join(md_folder, d))]
    
    return jsonify(example_paths)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)