from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_
from models.log import OperationLog
from models.user import User
from models.file import File
from app import db
import json
import csv
import io
import tempfile
import os
from datetime import datetime

# 创建蓝图
log_bp = Blueprint('log', __name__)

@log_bp.route('/', methods=['GET'])
@jwt_required()
def get_logs():
    """获取操作日志列表，支持分页、筛选和搜索"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # 过滤条件
    user_id = request.args.get('user_id', type=int)

    file_id = request.args.get('file_id', type=int)
    operation_type = request.args.get('operation_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search_query = request.args.get('search')
    
    query = OperationLog.query

   
    # 添加过滤条件
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    
    if file_id:
        query = query.filter(OperationLog.file_id == file_id)
    
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
    
    # 日期范围过滤
    date_filters = []
    if start_date:
        date_filters.append(OperationLog.operation_time >= start_date)
    if end_date:
        date_filters.append(OperationLog.operation_time <= end_date)
    
    if date_filters:
        query = query.filter(and_(*date_filters))
    
    # 关键词搜索 - 通过关联表搜索
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.join(User).join(File).filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                File.original_filename.ilike(search_pattern),
                OperationLog.details.ilike(search_pattern)
            )
        )
    
    # 分页查询
    logs = query.order_by(OperationLog.operation_time.desc()).paginate(page=page, per_page=per_page)
    
    # 准备响应数据
    result_logs = []
    for log in logs.items:
        log_dict = log.to_dict()
        
        # 添加用户和文件信息
        if log.user:
            log_dict['user'] = {
                'id': log.user.id,
                'username': log.user.username,
                'email': log.user.email
            }
        
        if log.file:
            log_dict['file'] = {
                'id': log.file.id,
                'original_filename': log.file.original_filename,
                'file_type': log.file.file_type
            }
        
        result_logs.append(log_dict)
    
    return jsonify({
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page,
        'per_page': logs.per_page,
        'items': result_logs
    }), 200

@log_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_log_stats():
    """获取操作日志统计信息"""
    # 按操作类型统计
    operation_stats = db.session.query(
        OperationLog.operation_type,
        db.func.count(OperationLog.id)
    ).group_by(OperationLog.operation_type).all()
    
    # 按用户统计
    user_stats = db.session.query(
        User.username,
        db.func.count(OperationLog.id)
    ).join(User).group_by(User.username).limit(10).all()
    
    # 按文件类型统计
    file_type_stats = db.session.query(
        File.file_type,
        db.func.count(OperationLog.id)
    ).join(File).group_by(File.file_type).all()
    
    return jsonify({
        'operation_stats': {op_type: count for op_type, count in operation_stats},
        'user_stats': {username: count for username, count in user_stats},
        'file_type_stats': {file_type: count for file_type, count in file_type_stats}
    }), 200

@log_bp.route('/export', methods=['GET'])
@jwt_required()
def export_logs():
    """导出操作日志为CSV文件"""
    # 获取查询参数
    user_id = request.args.get('user_id', type=int)
    file_id = request.args.get('file_id', type=int)
    operation_type = request.args.get('operation_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    search_query = request.args.get('search')
    
    query = OperationLog.query
    
    # 添加过滤条件
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    
    if file_id:
        query = query.filter(OperationLog.file_id == file_id)
    
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
    
    # 日期范围过滤
    date_filters = []
    if start_date:
        date_filters.append(OperationLog.operation_time >= start_date)
    if end_date:
        date_filters.append(OperationLog.operation_time <= end_date)
    
    if date_filters:
        query = query.filter(and_(*date_filters))
    
    # 关键词搜索
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.join(User).join(File).filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                File.original_filename.ilike(search_pattern),
                OperationLog.details.ilike(search_pattern)
            )
        )
    
    # 获取所有查询结果
    logs = query.order_by(OperationLog.operation_time.desc()).all()
    
    # 创建临时CSV文件
    fd, path = tempfile.mkstemp(suffix='.csv')
    
    try:
        with os.fdopen(fd, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            # 写入CSV头部
            writer.writerow(['ID', '操作类型', '操作时间', '用户', '文件', '详情', 'IP地址'])
            
            # 写入数据行
            for log in logs:
                user_name = log.user.username if log.user else '未知用户'
                file_name = log.file.original_filename if log.file else '未知文件'
                
                # 格式化详情
                details = log.details
                try:
                    if details:
                        details_obj = json.loads(details)
                        details = details_obj.get('message', details)
                except:
                    pass
                
                writer.writerow([
                    log.id,
                    getOperationTypeLabel(log.operation_type),
                    log.operation_time.strftime('%Y-%m-%d %H:%M:%S'),
                    user_name,
                    file_name,
                    details,
                    log.ip_address or ''
                ])
        
        # 返回CSV文件
        return send_file(
            path, 
            as_attachment=True,
            download_name=f'操作日志_{datetime.now().strftime("%Y%m%d%H%M%S")}.csv',
            mimetype='text/csv'
        )
    
    except Exception as e:
        # 出错时删除临时文件
        os.remove(path)
        return jsonify({'message': f'导出日志失败: {str(e)}'}), 500

def getOperationTypeLabel(type):
    """获取操作类型的中文标签"""
    types = {
        'create': '创建',
        'read': '查看',
        'update': '更新',
        'delete': '删除'
    }
    return types.get(type, type)

# 辅助函数：记录操作日志
def log_operation(operation_type, user_id, file_id, request=None, details=None):
    """
    记录用户操作
    :param operation_type: 操作类型 (create, read, update, delete)
    :param user_id: 用户ID
    :param file_id: 文件ID
    :param request: Flask请求对象，用于获取IP地址
    :param details: 操作详情，可以是字符串或字典
    """
    try:
        ip_address = request.remote_addr if request else None
        
        # 如果details是字典，转换为JSON字符串
        if isinstance(details, dict):
            details = json.dumps(details)
        
        # 获取文件信息
        file_name = None
        file_type = None
        
        # 查询文件信息
        file = File.query.get(file_id) if file_id else None
        if file:
            file_name = file.original_filename
            file_type = file.file_type
        
        # 如果是删除操作且details包含文件信息，优先使用details中的信息
        if operation_type == 'delete' and isinstance(details, str):
            try:
                details_dict = json.loads(details)
                if 'file_info' in details_dict and 'original_filename' in details_dict['file_info']:
                    file_name = details_dict['file_info']['original_filename']
                if 'file_info' in details_dict and 'file_type' in details_dict['file_info']:
                    file_type = details_dict['file_info']['file_type']
            except:
                pass
        
        log = OperationLog(
            operation_type=operation_type,
            user_id=user_id,
            file_id=file_id,
            ip_address=ip_address,
            details=details,
            file_name=file_name,
            file_type=file_type
        )
        
        db.session.add(log)
        db.session.commit()
        
        return True
    except Exception as e:
        db.session.rollback()
        print(f"记录操作日志失败: {str(e)}")
        return False 