from functools import wraps
from flask import jsonify, current_app
from flask_jwt_extended import get_jwt_identity, get_jwt, verify_jwt_in_request
from models.user import User
import os

# 开发模式下禁用严格认证
DEV_MODE = True

def admin_required(fn):
    """检查用户是否具有管理员角色"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 在开发模式下跳过权限检查
        if DEV_MODE:
            return fn(*args, **kwargs)
            
        try:
            # 验证JWT
            verify_jwt_in_request()
            
            # 获取JWT中的角色信息
            claims = get_jwt()
            roles = claims.get('roles', [])
            
            # 检查是否具有管理员角色
            if 'admin' not in roles:
                return jsonify({'message': '需要管理员权限'}), 403
                
        except Exception as e:
            # 在开发模式下，即使JWT验证失败也允许访问
            if DEV_MODE:
                return fn(*args, **kwargs)
            return jsonify({'message': '认证失败'}), 401
        
        return fn(*args, **kwargs)
    return wrapper

def permission_required(permission):
    """检查用户是否具有特定权限"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 在开发模式下跳过权限检查
            if DEV_MODE:
                return fn(*args, **kwargs)
                
            try:
                # 验证JWT
                verify_jwt_in_request()
                
                current_user_id = get_jwt_identity()
                user = User.query.get(current_user_id)
                
                if not user:
                    return jsonify({'message': '用户不存在'}), 404
                
                # 管理员拥有所有权限
                if user.has_role('admin'):
                    return fn(*args, **kwargs)
                
                # 检查是否具有特定权限
                if not user.has_permission(permission):
                    return jsonify({'message': f'需要权限: {permission}'}), 403
                    
            except Exception as e:
                # 在开发模式下，即使JWT验证失败也允许访问
                if DEV_MODE:
                    return fn(*args, **kwargs)
                return jsonify({'message': '认证失败'}), 401
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def self_or_admin(fn):
    """确保用户只能操作自己的资源，除非是管理员"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # 在开发模式下跳过权限检查
        if DEV_MODE:
            return fn(*args, **kwargs)
            
        try:
            # 验证JWT
            verify_jwt_in_request()
            
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            roles = claims.get('roles', [])
            
            # 检查URL中的user_id参数
            user_id = kwargs.get('user_id')
            
            # 非管理员不能操作其他用户资源
            if 'admin' not in roles and user_id != current_user_id:
                return jsonify({'message': '无权操作其他用户资源'}), 403
                
        except Exception as e:
            # 在开发模式下，即使JWT验证失败也允许访问
            if DEV_MODE:
                return fn(*args, **kwargs)
            return jsonify({'message': '认证失败'}), 401
        
        return fn(*args, **kwargs)
    return wrapper 