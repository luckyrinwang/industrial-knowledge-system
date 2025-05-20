from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    get_jwt_identity, 
    jwt_required,
    get_jwt
)
from models.user import User
from app import db, jwt
import logging

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': '用户名和密码不能为空'}), 400
    
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': '用户名或密码错误'}), 401
    
    if not user.is_active:
        return jsonify({'message': '该账户已被禁用，请联系管理员'}), 403
    
    # 创建访问令牌
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'username': user.username,
            'email': user.email,
            'roles': [role.name for role in user.roles]
        }
    )
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'message': '原密码和新密码不能为空'}), 400
    
    if not user.check_password(data.get('old_password')):
        return jsonify({'message': '原密码错误'}), 401
    
    user.set_password(data.get('new_password'))
    db.session.commit()
    
    return jsonify({'message': '密码修改成功'}), 200

# JWT错误处理
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'message': '令牌已过期，请重新登录'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    logging.error(f"JWT invalid_token_loader triggered. Error: {str(error)}")
    return jsonify({'message': '无效的令牌，请查看后端日志了解详情'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'message': '未提供访问令牌'}), 401 