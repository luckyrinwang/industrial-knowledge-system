from flask import request, g, current_app
from models.user import User
import jwt

def get_current_user_id():
    """
    从请求中获取当前用户ID
    优先从JWT令牌获取，解析失败时尝试其他方式
    """
    # 优先检查请求头中是否有Authorization（JWT）
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            # 解析JWT令牌
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'jwt_dev_secret_key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload.get('sub')  # JWT规范中用户ID存储在sub字段
            if user_id and str(user_id).isdigit():
                return int(user_id)
        except Exception as e:
            # 可选：记录异常日志，便于调试
            current_app.logger.warning(f"JWT解析失败: {e}")
            pass
    
    # 检查全局对象g是否存储了用户ID
    if hasattr(g, 'user_id'):
        return g.user_id
    
    # 检查请求参数
    user_id = request.args.get('user_id')
    if user_id and user_id.isdigit():
        return int(user_id)
    
    # 检查Form数据
    user_id = request.form.get('user_id')
    if user_id and user_id.isdigit():
        return int(user_id)
    
    # 检查Cookie
    user_id = request.cookies.get('user_id')
    if user_id and user_id.isdigit():
        return int(user_id)
    
    # 检查JSON数据
    if request.is_json:
        try:
            data = request.get_json()
            if data and 'user_id' in data and isinstance(data['user_id'], int):
                return data['user_id']
        except Exception as e:
            current_app.logger.warning(f"JSON解析失败: {e}")
            pass
    
    # 如果前端有传入用户名，可以根据用户名查找
    username = request.args.get('username') or request.form.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            return user.id
    
    # 默认返回管理员ID
    return 1  # 默认为ID为1的管理员用户 