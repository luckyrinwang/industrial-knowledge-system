import os
import uuid
import re
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from models.file import File
from models.user import User
from app import db
from routes.log import log_operation
from utils.auth_utils import get_current_user_id
from utils.docx2pdf_utils import docx_to_pdf
from utils.ragflow_utils import default_client

# 创建蓝图
file_bp = Blueprint('file', __name__)

def process_single_file(file, file_type, description, current_user_id):
    """处理单个文件上传的共用函数
    
    Args:
        file: 文件对象
        file_type: 文件类型
        description: 文件描述
        current_user_id: 当前用户ID
        
    Returns:
        tuple: (success, result_or_error)
            success: 布尔值，表示处理是否成功
            result_or_error: 成功时返回文件记录对象，失败时返回错误信息
    """
    try:
        # 获取原始文件名（保留中文）
        original_filename = file.filename
        extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        safe_filename = secure_filename(unique_filename)
        
        # 创建年月日目录结构
        today = datetime.now()
        year_dir = str(today.year)
        month_dir = f"{today.month:02d}"
        day_dir = f"{today.day:02d}"
        
        relative_path = os.path.join(file_type, year_dir, month_dir, day_dir)
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], relative_path)
        
        # 确保目录存在
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 保存文件
        file_path = os.path.join(upload_dir, safe_filename)
        file.save(file_path)
        
        pdf_path = None
        md_path = None
        images_dir = None
        ragflow_doc_id = None
        
        # 处理特殊文件类型（doc/docx/pdf）
        if extension in ('doc', 'docx'):
            pdf_filename = f"{uuid.uuid4().hex}.pdf"
            pdf_file_path = os.path.join(upload_dir, pdf_filename)
            pdf_conversion_success = False
            
            try:
                print(f"正在将文档转换为PDF: {original_filename}")
                # 确保文件已经完全写入，并且其他进程不再访问
                import time
                time.sleep(1)  # 等待文件完全写入
                
                # Word文档转PDF处理
                docx_to_pdf(file_path, pdf_file_path)
                
                # 检查PDF是否成功生成
                if os.path.exists(pdf_file_path) and os.path.getsize(pdf_file_path) > 0:
                    pdf_conversion_success = True
                    pdf_path = os.path.join(relative_path, pdf_filename)
                    print(f"成功将 {original_filename} 转换为 PDF: {pdf_file_path}")
                else:
                    raise RuntimeError("PDF文件未能成功生成或文件大小为0")
                    
                # 在处理PDF前，等待文件系统操作完成
                time.sleep(1)
                
                print(f"开始处理PDF转MD和上传到RAGFlow: {pdf_file_path}")
                # 处理PDF转MD和上传到RAGFlow
                md_path, images_dir, ragflow_doc_id = process_pdf_to_md_and_ragflow(pdf_file_path, original_filename)
                print(f"PDF处理完成: {md_path}, {ragflow_doc_id}")
            except Exception as e:
                error_msg = f'doc/docx转pdf或pdf转md失败: {str(e)}'
                print(error_msg)
                
                # 清理已创建的文件
                try:
                    # 先等待文件系统操作完成
                    time.sleep(2)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            print(f"已删除源文件: {file_path}")
                        except Exception as cleanup_error:
                            print(f"清理源文件失败: {cleanup_error}")
                except Exception as cleanup_error:
                    print(f"清理源文件过程出错: {cleanup_error}")
                
                try:
                    if 'pdf_file_path' in locals() and os.path.exists(pdf_file_path):
                        try:
                            os.remove(pdf_file_path)
                            print(f"已删除PDF文件: {pdf_file_path}")
                        except Exception as cleanup_error:
                            print(f"清理PDF文件失败: {cleanup_error}")
                except Exception as cleanup_error:
                    print(f"清理PDF文件过程出错: {cleanup_error}")
                    
                import traceback
                print(f"文档处理异常详情: {traceback.format_exc()}")
                
                # 强制执行垃圾收集和等待
                import gc
                gc.collect()
                time.sleep(2)  # 给系统时间恢复资源
                
                return False, error_msg
        elif extension == 'pdf':
            try:
                # 检查PDF文件是否有效
                if os.path.getsize(file_path) == 0:
                    raise ValueError("PDF文件大小为0，可能已损坏")
                
                print(f"开始处理PDF转MD和上传到RAGFlow: {file_path}")
                # 确保文件已经完全写入，并且其他进程不再访问
                import time
                time.sleep(1)  # 等待文件完全写入
                
                # 处理PDF转MD和上传到RAGFlow
                md_path, images_dir, ragflow_doc_id = process_pdf_to_md_and_ragflow(file_path, original_filename)
                print(f"PDF处理完成: {md_path}, {ragflow_doc_id}")
            except Exception as e:
                error_msg = f'pdf转md失败: {str(e)}'
                print(error_msg)
                
                # 清理已创建的文件
                try:
                    # 先等待文件系统操作完成
                    time.sleep(2)
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            print(f"已删除PDF文件: {file_path}")
                        except Exception as cleanup_error:
                            print(f"清理PDF文件失败: {cleanup_error}")
                except Exception as cleanup_error:
                    print(f"清理过程出错: {cleanup_error}")
                
                import traceback
                print(f"PDF处理异常详情: {traceback.format_exc()}")
                
                # 强制执行垃圾收集和等待
                import gc
                gc.collect()
                time.sleep(1)  # 给系统时间恢复资源
                
                return False, error_msg
        
        # 获取实际的文件大小
        file_size = os.path.getsize(file_path)
        
        # 创建文件记录
        new_file = File(
            filename=safe_filename,
            original_filename=original_filename,
            file_type=file_type,
            file_format=extension,
            file_path=os.path.join(relative_path, safe_filename),
            file_size=file_size,
            user_id=current_user_id,
            description=description,
            pdf_path=pdf_path,
            md_path=md_path,
            images_dir=images_dir,
            ragflow_doc_id=ragflow_doc_id if ragflow_doc_id is not None else None
        )
        
        return True, new_file
    except Exception as e:
        # 清理可能创建的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        return False, str(e)

def process_pdf_to_md_and_ragflow(pdf_file_path, original_filename):
    """将PDF转换为Markdown并上传到RAGFlow知识库
    
    Args:
        pdf_file_path: PDF文件的完整路径
        original_filename: 原始文件名（用于生成RAGFlow中的显示名称）
        
    Returns:
        tuple: (md_path, images_dir, ragflow_doc_id)
            md_path: Markdown文件的相对路径
            images_dir: 图片目录的相对路径
            ragflow_doc_id: RAGFlow知识库中的文档ID，如果上传失败则为None
    """
    import requests, base64
    
    # 初始化返回值
    md_path = None
    images_dir = None
    ragflow_doc_id = None
    
    # 生成随机目录名
    random_dir = uuid.uuid4().hex
    md_save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'md')
    images_save_dir = os.path.join(md_save_dir, random_dir)
    os.makedirs(images_save_dir, exist_ok=True)
    
    # 调用PDF解析API
    API_URL = current_app.config['PDF_PARSE_SERVICE_URL']
    with open(pdf_file_path, "rb") as f:
        resp = requests.post(API_URL, files={"file": f}, params={
            "parse_method": current_app.config['PDF_PARSE_METHOD'],
            "is_json_md_dump": "false",
            "output_dir": "output",
            "return_layout": "false",
            "return_info": "false",
            "return_content_list": "false",
            "return_images": str(current_app.config['PDF_RETURN_IMAGES']).lower()
        }, timeout=current_app.config['PDF_PARSE_TIMEOUT'])
    
    if resp.status_code == 200:
        result = resp.json()
        md_content = result.get("md_content", "")
        image_dict = result.get("images", {})
        
        # 保存图片
        for filename, data_url in image_dict.items():
            img_data = base64.b64decode(data_url.split(',')[1])
            with open(os.path.join(images_save_dir, filename), 'wb') as imgf:
                imgf.write(img_data)
        
        # 替换md中的图片路径
        for filename in image_dict.keys():
            md_content = md_content.replace(f"images/{filename}", f"{random_dir}/{filename}")
        
        # 保存md文件
        md_filename = f"{random_dir}.md"
        md_path_abs = os.path.join(md_save_dir, md_filename)
        with open(md_path_abs, 'w', encoding='utf-8') as mf:
            mf.write(md_content)
        
        # 相对路径
        md_path = os.path.join('md', md_filename)
        images_dir = os.path.join('md', random_dir)
        
        # 同步上传到RAGFlow知识库
        try:
            # 使用应用配置中的RAGFlow设置
            auto_sync = current_app.config['RAGFLOW_AUTO_SYNC']
            auto_parse = current_app.config['RAGFLOW_AUTO_PARSE']
            chunk_method = current_app.config['RAGFLOW_CHUNK_METHOD']
            parser_config_str = current_app.config['RAGFLOW_PARSER_CONFIG']
            
            try:
                parser_config = json.loads(parser_config_str)
            except Exception as e:
                print(f"解析配置 RAGFLOW_PARSER_CONFIG 错误: {e}")
                parser_config = {"chunk_size": 1000, "chunk_overlap": 100}
                
            if auto_sync:
                # 使用原始文件名作为显示名称
                display_name = f"{os.path.splitext(original_filename)[0]}.md"
                sync_result = default_client.upload_document(
                    md_path_abs, 
                    display_name, 
                    auto_parse=auto_parse,
                    chunk_method=chunk_method,
                    parser_config=parser_config
                )
                
                # 提取并保存RAGFlow文档ID
                if sync_result.get('status') == 'success' and sync_result.get('data'):
                    if isinstance(sync_result['data'], dict) and 'data' in sync_result['data']:
                        doc_data = sync_result['data']['data']
                        if isinstance(doc_data, list) and len(doc_data) > 0:
                            ragflow_doc_id = doc_data[0].get('id')
                            print(f"提取的RAGFlow文档ID: {ragflow_doc_id}")
                
                if sync_result.get('status') != 'success':
                    print(f"RAGFlow同步失败: {sync_result.get('message')}")
        except Exception as e:
            print(f"同步到RAGFlow时出错: {str(e)}")
            # 不影响主流程，仅记录错误日志
    
    return md_path, images_dir, ragflow_doc_id

# 允许的文件类型
ALLOWED_EXTENSIONS = {
    'document': {'doc', 'docx'},
    'spreadsheet': {'xls', 'xlsx'},
    'pdf': {'pdf'},
    'image': {'jpg', 'jpeg', 'png', 'gif'},
    'video': {'mp4', 'avi', 'mkv'}
}

# 最大文件大小 (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

def allowed_file(filename, file_type=None):
    """检查文件是否允许上传"""
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if file_type:
        return extension in ALLOWED_EXTENSIONS.get(file_type, set())
    else:
        return any(extension in extensions for extensions in ALLOWED_EXTENSIONS.values())

def get_file_type(filename):
    """根据文件扩展名获取文件类型"""
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    return None

@file_bp.route('/', methods=['GET'])
@jwt_required()
def get_files():
    """获取文件列表，支持分页、筛选和搜索"""
    print("开始处理获取文件请求")
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        file_type = request.args.get('file_type')
        search_query = request.args.get('search')
        show_deleted = request.args.get('show_deleted', '0') == '1'  # 是否显示已删除文件
        
        print(f"请求参数: page={page}, per_page={per_page}, file_type={file_type}, search={search_query}, show_deleted={show_deleted}")
        
        query = File.query
        
        # 默认只显示未删除的文件
        if not show_deleted:
            query = query.filter_by(is_deleted=False)
        
        # 如果指定了文件类型，进行筛选
        if file_type:
            query = query.filter_by(file_type=file_type)
        
        # 如果指定了搜索关键词，搜索文件名和描述
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                or_(
                    File.original_filename.ilike(search_pattern),
                    File.description.ilike(search_pattern)
                )
            )
        
        # 计算总数
        total_count = query.count()
        print(f"符合条件的文件总数: {total_count}")
        
        # 分页查询
        files = query.order_by(File.created_at.desc()).paginate(page=page, per_page=per_page)
        
        # 为简化日志记录，仅记录第一个文件的查询操作
        if files.items and len(files.items) > 0:
            log_operation('read', get_current_user_id(), files.items[0].id, request, 
                        {'message': '查询文件列表', 'count': len(files.items)})
        
        # 准备响应数据
        response_data = {
            'total': files.total,
            'pages': files.pages,
            'current_page': files.page,
            'per_page': files.per_page,
            'items': [file.to_dict() for file in files.items]
        }
        
        print(f"返回文件数量: {len(response_data['items'])}")
        return jsonify(response_data), 200
    
    except Exception as e:
        import traceback
        print(f"获取文件列表失败: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'message': f'获取文件列表失败: {str(e)}'}), 500

@file_bp.route('/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """获取单个文件的详细信息"""
    file = File.query.get(file_id)
    
    if not file:
        return jsonify({'message': '文件不存在'}), 404
    
    # 记录查看文件详情的操作
    log_operation('read', get_current_user_id(), file_id, request, {'message': '查看文件详情'})
    
    file_data = file.to_dict()
    
    # 如果文件已删除，在响应中添加提示
    if file.is_deleted:
        file_data['message'] = '此文件已被删除，无法下载或预览'
    
    return jsonify(file_data), 200

@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """上传文件"""
    # 获取当前用户ID
    current_user_id = get_current_user_id()

    
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'message': '没有文件部分'}), 400
    
    file = request.files['file']
    description = request.form.get('description', '')
    file_type = request.form.get('file_type')
    
    # 检查文件是否有名称
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400
    
    # 检查文件类型是否合法
    if not file_type:
        return jsonify({'message': '文件类型不能为空'}), 400
    
    if not allowed_file(file.filename, file_type):
        return jsonify({'message': f'不支持的文件类型，当前仅支持{", ".join(ALLOWED_EXTENSIONS.get(file_type, []))}格式'}), 400
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # 重置文件指针位置
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'message': f'文件大小超出限制（最大{MAX_FILE_SIZE/1024/1024}MB）'}), 400
    
    try:
        # 处理文件上传
        success, result = process_single_file(file, file_type, description, current_user_id)
        
        if not success:
            return jsonify({'message': result}), 500
        
        # 获取处理后的文件对象
        new_file = result
        
        # 保存到数据库
        db.session.add(new_file)
        db.session.commit()
        
        # 记录文件上传操作
        log_operation('create', current_user_id, new_file.id, request, 
                     {'message': '上传文件', 'file_size': new_file.file_size, 'file_type': file_type})
        
        return jsonify({
            'message': '文件上传成功',
            'file': new_file.to_dict()
        }), 201
    
    except Exception as e:
        # 回滚数据库事务
        db.session.rollback()
        return jsonify({'message': f'上传文件失败: {str(e)}'}), 500

@file_bp.route('/batch-upload', methods=['POST'])
@jwt_required()
def batch_upload_files():
    """批量上传文件"""
    # 获取当前用户ID
    current_user_id = get_current_user_id()
    
    # 检查是否有文件
    if 'files' not in request.files:
        return jsonify({'message': '没有文件部分'}), 400
    
    files = request.files.getlist('files')
    descriptions = request.form.getlist('descriptions')
    file_type = request.form.get('file_type')
    
    if not files:
        return jsonify({'message': '没有选择文件'}), 400
    
    if not file_type:
        return jsonify({'message': '文件类型不能为空'}), 400
    
    uploaded_files = []
    failed_files = []
    
    try:
        # 控制并发处理，每批次处理的文件数量
        batch_size = 1  # 对于Word文档转换，一次只处理一个文件更安全
        total_files = len(files)
        
        print(f"开始批量处理 {total_files} 个文件，类型：{file_type}")
        
        for i in range(0, total_files, batch_size):
            batch_end = min(i + batch_size, total_files)
            current_batch = files[i:batch_end]
            
            print(f"处理批次 {i//batch_size + 1}/{(total_files + batch_size - 1)//batch_size}，"
                  f"文件 {i+1}-{batch_end} (共 {total_files} 个)")
            
            for file_index, file in enumerate(current_batch, start=i):
                # 检查文件是否有名称
                if file.filename == '':
                    continue
                
                # 检查文件类型是否合法
                if not allowed_file(file.filename, file_type):
                    failed_files.append({
                        'filename': file.filename,
                        'reason': f'不支持的文件类型，当前仅支持{", ".join(ALLOWED_EXTENSIONS.get(file_type, []))}格式'
                    })
                    continue
                
                # 检查文件大小
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)  # 重置文件指针位置
                
                if file_size > MAX_FILE_SIZE:
                    failed_files.append({
                        'filename': file.filename,
                        'reason': f'文件大小超出限制（最大{MAX_FILE_SIZE/1024/1024}MB）'
                    })
                    continue
                
                # 获取文件描述（如果有）
                description_index = file_index if file_index < len(descriptions) else 0
                description = descriptions[description_index] if descriptions and description_index < len(descriptions) else ''
                
                # 处理单个文件
                print(f"处理文件 {file_index+1}/{total_files}: {file.filename}")
                success, result = process_single_file(file, file_type, description, current_user_id)
                
                if not success:
                    failed_files.append({
                        'filename': file.filename,
                        'reason': result
                    })
                    continue
                
                # 获取处理后的文件对象
                new_file = result
                db.session.add(new_file)
                uploaded_files.append(new_file)
                
                # 每批处理完后即提交，避免长时间占用数据库连接
                db.session.flush()
                
                # 如果是Word文档，额外等待一段时间确保系统资源释放
                if file.filename.endswith(('.doc', '.docx')):
                    print(f"Word文档处理完成，等待资源释放...")
                    import time
                    time.sleep(2)  # Word文档需要更长的等待时间
            
            # 每批次提交一次数据库事务
            if uploaded_files:
                db.session.commit()
                print(f"已成功处理并提交 {len(uploaded_files)} 个文件")
            
            # 在批次之间加入短暂暂停，避免资源紧张
            import time
            time.sleep(0.5)
            
            # 强制进行垃圾回收，释放内存
            import gc
            gc.collect()
        
        # 最终提交（确保所有更改都被保存）
        if uploaded_files:
            db.session.commit()
            
            # 记录批量上传操作
            for new_file in uploaded_files:
                log_operation('create', current_user_id, new_file.id, request, 
                            {'message': '批量上传文件', 'file_size': new_file.file_size, 'file_type': new_file.file_type})
        
        return jsonify({
            'message': f'成功上传 {len(uploaded_files)} 个文件，{len(failed_files)} 个文件失败',
            'uploaded_files': [file.to_dict() for file in uploaded_files],
            'failed_files': failed_files
        }), 201
    
    except Exception as e:
        # 回滚数据库事务
        db.session.rollback()
        return jsonify({'message': f'批量上传文件失败: {str(e)}'}), 500

@file_bp.route('/download/<int:file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """下载文件"""
    file = File.query.get(file_id)
    
    if not file:
        return jsonify({'message': '文件不存在'}), 404
    
    # 检查文件是否已被删除
    if file.is_deleted:
        return jsonify({'message': '文件已被删除'}), 404
    
    # 获取当前用户ID
    current_user_id = get_current_user_id()
    
    # 记录文件下载操作
    log_operation('read', get_current_user_id(), file_id, request, {'message': '下载文件'})
    
    # 构建文件路径
    file_dir = os.path.dirname(os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path))
    filename = os.path.basename(file.file_path)
    
    # 检查文件是否存在
    full_path = os.path.join(file_dir, filename)
    if not os.path.exists(full_path):
        return jsonify({'message': '文件不存在或已被删除'}), 404
    
    try:
        return send_from_directory(
            file_dir, 
            filename, 
            as_attachment=True,
            download_name=file.original_filename
        )
    except Exception as e:
        return jsonify({'message': f'下载文件失败: {str(e)}'}), 500

@file_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """删除文件"""
    file = File.query.get(file_id)
    
    if not file:
        return jsonify({'message': '文件不存在'}), 404
    
    # 获取当前用户ID
    current_user_id = get_current_user_id()
    
    try:
        # 从RAGFlow知识库中删除文档
        ragflow_result = None
        if file.file_format in ('doc', 'docx', 'pdf') and file.ragflow_doc_id:
            # 如果文件已经同步到RAGFlow并且有文档ID，则从RAGFlow中删除
            ragflow_result = default_client.delete_documents([file.ragflow_doc_id])
            print(f"从RAGFlow删除文档结果: {ragflow_result}")
            
            # 记录RAGFlow删除操作
            log_operation('delete', get_current_user_id(), file_id, request, 
                         {'message': '从RAGFlow删除文档', 'ragflow_result': ragflow_result})
        
        # 删除物理文件
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 如果是doc/docx并且有pdf_path，删除pdf文件
        if file.file_format in ('doc', 'docx') and file.pdf_path:
            pdf_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.pdf_path)
            if os.path.exists(pdf_file_path):
                os.remove(pdf_file_path)
            # 同时删除md文件和图片目录
            if file.md_path:
                md_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.md_path)
                if os.path.exists(md_file_path):
                    os.remove(md_file_path)
            if file.images_dir:
                images_dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.images_dir)
                import shutil
                if os.path.exists(images_dir_path):
                    shutil.rmtree(images_dir_path)
        # 如果是pdf，删除md文件和图片目录
        if file.file_format == 'pdf':
            if file.md_path:
                md_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.md_path)
                if os.path.exists(md_file_path):
                    os.remove(md_file_path)
            if file.images_dir:
                images_dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.images_dir)
                import shutil
                if os.path.exists(images_dir_path):
                    shutil.rmtree(images_dir_path)
        
        # 记录文件删除操作
        log_operation('delete', get_current_user_id(), file_id, request, 
                    {'message': '删除文件'})
        
        # 标记文件为已删除（软删除）
        file.is_deleted = True
        # 清除RAGFlow文档ID
        file.ragflow_doc_id = None
        db.session.commit()
        
        return jsonify({
            'message': '文件删除成功',
            'ragflow_result': ragflow_result
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除文件失败: {str(e)}'}), 500

@file_bp.route('/preview/<int:file_id>', methods=['GET'])
@jwt_required()
def preview_file(file_id):
    """预览文件"""
    file = File.query.get(file_id)
    
    if not file:
        return jsonify({'message': '文件不存在'}), 404
    
    # 检查文件是否已被删除
    if file.is_deleted:
        return jsonify({'message': '文件已被删除'}), 404
    
    # 获取当前用户ID
    current_user_id = get_current_user_id()
    
    # 记录文件预览操作
    log_operation('read', get_current_user_id(), file_id, request, {'message': '预览文件'})
    
    # 构建文件路径
    file_dir = os.path.dirname(os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path))
    filename = os.path.basename(file.file_path)
    
    # 检查文件是否存在
    full_path = os.path.join(file_dir, filename)
    if not os.path.exists(full_path):
        return jsonify({'message': '文件不存在或已被删除'}), 404
    
    # 根据文件类型设置适当的Content-Type
    content_type = None
    if file.file_type == 'image':
        content_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif'
        }
        content_type = content_type_map.get(file.file_format)
    elif file.file_type == 'video':
        content_type_map = {
            'mp4': 'video/mp4',
            'avi': 'video/x-msvideo',
            'mkv': 'video/x-matroska'
        }
        content_type = content_type_map.get(file.file_format)
    elif file.file_type == 'pdf':
        content_type = 'application/pdf'
    
    # 对于图片、视频等可直接预览的文件，直接返回
    if file.file_type in ['image', 'video', 'pdf']:
        try:
            return send_from_directory(
                file_dir, 
                filename,
                mimetype=content_type
            )
        except Exception as e:
            return jsonify({'message': f'文件预览失败: {str(e)}'}), 500
    
    # 对于文档、表格等不能直接预览的文件，返回一个预览URL
    return jsonify({
        'message': '该文件类型不支持在线预览，请下载后查看',
        'download_url': f'/api/files/download/{file.id}'
    }), 200

@file_bp.route('/download-pdf/<int:file_id>', methods=['GET'])
def download_pdf_file(file_id):
    """下载或预览文档类文件生成的PDF"""
    file = File.query.get(file_id)
    if not file:
        return jsonify({'message': '文件不存在'}), 404
    if not file.pdf_path:
        return jsonify({'message': '该文件没有生成PDF'}), 404
    pdf_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.pdf_path)
    if not os.path.exists(pdf_full_path):
        return jsonify({'message': 'PDF文件不存在'}), 404
    try:
        pdf_dir = os.path.dirname(pdf_full_path)
        pdf_filename = os.path.basename(pdf_full_path)
        # 判断是否为预览模式
        as_attachment = not (request.args.get('preview') == '1')
        return send_from_directory(
            pdf_dir,
            pdf_filename,
            as_attachment=as_attachment,
            download_name=os.path.splitext(file.original_filename)[0] + '.pdf',
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'message': f'下载PDF失败: {str(e)}'}), 500

@file_bp.route('/batch-delete', methods=['POST'])
@jwt_required()
def batch_delete_files():
    """批量删除文件"""
    data = request.get_json()
    if not data or 'file_ids' not in data:
        return jsonify({'message': '请提供要删除的文件ID列表'}), 400
        
    file_ids = data['file_ids']
    delete_strategy = data.get('delete_strategy', 'type')  # 默认按类型删除
    
    if not isinstance(file_ids, list) or not file_ids:
        return jsonify({'message': '文件ID列表必须是非空数组'}), 400
    
    # 获取当前用户ID
    current_user_id = get_current_user_id()
    
    results = {
        'success': [],
        'failed': []
    }
    
    # 收集需要删除的RAGFlow文档ID
    ragflow_doc_ids = []
    file_id_to_doc_id = {}  # 用于记录文件ID与RAGFlow文档ID的映射关系
    
    # 第一阶段：收集所有有效的文件和对应的RAGFlow文档ID
    valid_files = []
    for file_id in file_ids:
        try:
            file = File.query.get(file_id)
            
            if not file:
                results['failed'].append({
                    'file_id': file_id,
                    'error': '文件不存在'
                })
                continue
            
            valid_files.append(file)
            
            # 收集RAGFlow文档ID (只有在需要处理RAGFlow的策略下才收集)
            if delete_strategy in ['type', 'hard'] and file.file_format in ('doc', 'docx', 'pdf') and file.ragflow_doc_id:
                ragflow_doc_ids.append(file.ragflow_doc_id)
                file_id_to_doc_id[file_id] = file.ragflow_doc_id
            
        except Exception as e:
            results['failed'].append({
                'file_id': file_id,
                'error': str(e)
            })
    
    # 第二阶段：批量删除RAGFlow文档（如果有）
    ragflow_result = None
    if ragflow_doc_ids:
        try:
            # 一次性删除所有RAGFlow文档
            ragflow_result = default_client.delete_documents(ragflow_doc_ids)
            print(f"批量从RAGFlow删除文档结果: {ragflow_result}")
            
            # 记录RAGFlow批量删除操作
            log_operation('delete', get_current_user_id(), None, request, 
                         {'message': f'从RAGFlow批量删除{len(ragflow_doc_ids)}个文档', 
                          'ragflow_result': ragflow_result,
                          'document_ids': ragflow_doc_ids})
        except Exception as e:
            print(f"批量删除RAGFlow文档时出错: {str(e)}")
            # 记录错误但继续处理文件删除
    
    # 第三阶段：处理文件删除，按照不同策略处理
    for file in valid_files:
        try:
            file_id = file.id
            file_type = file.file_type
            file_format = file.file_format
            
            # 根据策略选择删除方式
            if delete_strategy == 'soft':
                # 软删除：只标记为已删除，不删除物理文件
                # 记录文件删除操作
                log_operation('delete', get_current_user_id(), file_id, request, 
                            {'message': f'批量软删除文件', 'strategy': 'soft'})
                
                # 标记文件为已删除（软删除）
                file.is_deleted = True
                # 仅清除RAGFlow文档ID
                if file_format in ('doc', 'docx', 'pdf'):
                    file.ragflow_doc_id = None
            
            elif delete_strategy == 'hard':
                # 硬删除：删除所有相关的物理文件和数据库记录
                # 删除物理文件
                _delete_physical_file(file)
                
                # 记录文件删除操作
                log_operation('delete', get_current_user_id(), file_id, request, 
                            {'message': f'批量硬删除文件', 'strategy': 'hard'})
                
                # 从数据库中删除记录
                db.session.delete(file)
            
            else:  # delete_strategy == 'type' 或其他未知策略使用默认的类型策略
                # 按文件类型删除：为不同类型的文件使用不同的删除策略
                
                # 对于文档和PDF类型，需要删除转换的文件和服务器资源
                if file_type in ['document', 'pdf']:
                    _delete_physical_file(file)
                    
                    # 记录文件删除操作
                    log_operation('delete', get_current_user_id(), file_id, request, 
                                {'message': f'批量删除文件(文档/PDF类型)', 'strategy': 'type'})
                    
                    # 标记为已删除
                    file.is_deleted = True
                    file.ragflow_doc_id = None
                
                # 对于图片和表格，这些文件通常较小，直接删除物理文件
                elif file_type in ['image', 'spreadsheet']:
                    # 删除物理文件
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # 记录文件删除操作
                    log_operation('delete', get_current_user_id(), file_id, request, 
                                {'message': f'批量删除文件(图片/表格类型)', 'strategy': 'type'})
                    
                    # 标记为已删除
                    file.is_deleted = True
                
                # 对于视频文件，根据文件大小决定是否删除物理文件
                elif file_type == 'video':
                    # 大于50MB的视频文件，考虑到存储压力，直接删除物理文件
                    if file.file_size > 50 * 1024 * 1024:  # 50MB
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        
                        log_operation('delete', get_current_user_id(), file_id, request, 
                                    {'message': f'批量删除文件(大型视频)', 'strategy': 'type'})
                    else:
                        # 小视频只做软删除
                        log_operation('delete', get_current_user_id(), file_id, request, 
                                    {'message': f'批量删除文件(小型视频-软删除)', 'strategy': 'type'})
                    
                    # 标记为已删除
                    file.is_deleted = True
                
                # 对于其他未知类型，采用软删除策略
                else:
                    log_operation('delete', get_current_user_id(), file_id, request, 
                                {'message': f'批量删除文件(其他类型-软删除)', 'strategy': 'type'})
                    file.is_deleted = True
            
            # 添加到成功列表
            results['success'].append({
                'file_id': file_id,
                'original_filename': file.original_filename,
                'file_type': file.file_type,
                'strategy': delete_strategy,
                'ragflow_doc_id': file_id_to_doc_id.get(file_id)
            })
            
        except Exception as e:
            # 添加到失败列表
            results['failed'].append({
                'file_id': file.id,
                'error': str(e)
            })
    
    # 提交数据库事务
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'message': f'批量删除文件失败: {str(e)}',
            'results': results
        }), 500
    
    # 返回处理结果
    return jsonify({
        'message': f'批量删除完成: {len(results["success"])}个成功, {len(results["failed"])}个失败',
        'results': results,
        'ragflow_result': ragflow_result
    }), 200

def _delete_physical_file(file):
    """删除文件相关的所有物理文件
    
    Args:
        file: 文件对象
        
    Returns:
        None
    """
    # 删除原始物理文件
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 如果是doc/docx并且有pdf_path，删除pdf文件
    if file.file_format in ('doc', 'docx') and file.pdf_path:
        pdf_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.pdf_path)
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
        # 同时删除md文件和图片目录
        if file.md_path:
            md_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.md_path)
            if os.path.exists(md_file_path):
                os.remove(md_file_path)
        if file.images_dir:
            images_dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.images_dir)
            import shutil
            if os.path.exists(images_dir_path):
                shutil.rmtree(images_dir_path)
    # 如果是pdf，删除md文件和图片目录
    if file.file_format == 'pdf':
        if file.md_path:
            md_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.md_path)
            if os.path.exists(md_file_path):
                os.remove(md_file_path)
        if file.images_dir:
            images_dir_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.images_dir)
            import shutil
            if os.path.exists(images_dir_path):
                shutil.rmtree(images_dir_path)