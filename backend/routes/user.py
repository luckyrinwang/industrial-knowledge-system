from flask import Blueprint, request, jsonify
from models.user import User, Role
from utils.auth import admin_required
from app import db

# 创建蓝图
user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
def get_users():
    """获取所有用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    users = User.query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'total': users.total,
        'pages': users.pages,
        'current_page': users.page,
        'per_page': users.per_page,
        'items': [user.to_dict() for user in users.items]
    }), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户详情"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    return jsonify(user.to_dict()), 200

@user_bp.route('/', methods=['POST'])
def create_user():
    """创建新用户"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': '无效的数据'}), 400
    
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'缺少必填字段: {field}'}), 400
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': '邮箱已存在'}), 400
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        full_name=data.get('full_name')
    )
    
    # 添加角色
    if 'roles' in data and isinstance(data['roles'], list):
        for role_name in data['roles']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                new_user.roles.append(role)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': '用户创建成功',
        'user': new_user.to_dict()
    }), 201

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'message': '无效的数据'}), 400
    
    # 更新基本信息
    if 'email' in data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'message': '邮箱已被占用'}), 400
        user.email = data['email']
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    # 更新密码
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    # 更新角色
    if 'roles' in data and isinstance(data['roles'], list):
        # 清除现有角色
        user.roles = []
        
        # 添加新角色
        for role_name in data['roles']:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
    
    db.session.commit()
    
    return jsonify({
        'message': '用户信息更新成功',
        'user': user.to_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': '用户不存在'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': '用户删除成功'}), 200

@user_bp.route('/roles', methods=['GET'])
def get_roles():
    """获取所有角色列表"""
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles]), 200 