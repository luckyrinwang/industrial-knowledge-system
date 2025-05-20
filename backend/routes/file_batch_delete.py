import os
import shutil
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from models.file import File
from app import db
from routes.log import log_operation
from utils.auth_utils import get_current_user_id
from utils.ragflow_utils import default_client

# 创建蓝图
file_batch_delete_bp = Blueprint('file_batch_delete', __name__)

@file_batch_delete_bp.route('/batch-delete', methods=['POST'])
@jwt_required()
def batch_delete_files():
    """批量删除文件"""
    data = request.get_json()
    if not data or 'file_ids' not in data:
        return jsonify({'message': '请提供要删除的文件ID列表'}), 400
        
    file_ids = data['file_ids']
    if not isinstance(file_ids, list) or not file_ids:
        return jsonify({'message': '文件ID列表必须是非空数组'}), 400
    
    # 获取当前用户ID
    current_user_id = get_current_user_id()
    
    results = {
        'success': [],
        'failed': []
    }
    
    for file_id in file_ids:
        try:
            file = File.query.get(file_id)
            
            if not file:
                results['failed'].append({
                    'file_id': file_id,
                    'error': '文件不存在'
                })
                continue
                
            # 从RAGFlow知识库中删除文档
            ragflow_result = None
            if file.file_format in ('doc', 'docx', 'pdf') and file.ragflow_doc_id:                # 如果文件已经同步到RAGFlow并且有文档ID，则从RAGFlow中删除
                ragflow_result = default_client.delete_documents([file.ragflow_doc_id])
                print(f"从RAGFlow删除文档结果 (文件ID: {file_id}): {ragflow_result}")
                
                # 记录RAGFlow删除操作
                log_operation('delete', get_current_user_id(), file_id, request, 
                             {'message': '从RAGFlow批量删除文档', 'ragflow_result': ragflow_result})
            
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
                        {'message': '批量删除文件'})
            
            # 标记文件为已删除（软删除）
            file.is_deleted = True
            # 清除RAGFlow文档ID
            file.ragflow_doc_id = None
            
            # 添加到成功列表
            results['success'].append({
                'file_id': file_id,
                'original_filename': file.original_filename,
                'ragflow_result': ragflow_result
            })
            
        except Exception as e:
            # 添加到失败列表
            results['failed'].append({
                'file_id': file_id,
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
        'results': results
    }), 200
