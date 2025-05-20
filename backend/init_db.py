from app import app, db
from models.user import User, Role, Permission
from models.file import File
from models.log import OperationLog
import bcrypt
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String

def init_db():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否需要进行日志表迁移
        migrate_operation_logs()
        
        # 如果没有任何角色，则创建默认角色
        if Role.query.count() == 0:
            create_default_roles()
        
        # 如果没有任何用户，则创建默认用户
        if User.query.count() == 0:
            create_default_users()
        
        # 提交所有更改
        db.session.commit()
        
        print("数据库初始化完成！")

        # 新增：为files表添加md_path和images_dir字段
        engine = db.engine
        meta = MetaData()
        meta.reflect(bind=engine)
        files = Table('files', meta, autoload_with=engine)
        if not hasattr(files.c, 'md_path'):
            with engine.connect() as conn:
                conn.execute('ALTER TABLE files ADD COLUMN md_path VARCHAR(255)')
        if not hasattr(files.c, 'images_dir'):
            with engine.connect() as conn:
                conn.execute('ALTER TABLE files ADD COLUMN images_dir VARCHAR(255)')

def migrate_operation_logs():
    """迁移操作日志表结构，为已有记录填充文件名和类型"""
    try:
        # 检查是否已经有file_name字段
        has_file_name = False
        try:
            # 检查一个日志记录中是否有file_name属性
            log = OperationLog.query.first()
            if log:
                _ = log.file_name
                has_file_name = True
        except Exception:
            # 捕获异常，说明字段不存在
            pass
        
        # 如果已经有file_name字段，说明已经迁移过，直接返回
        if has_file_name:
            print("日志表已经迁移，无需再次迁移")
            return
        
        # 添加新字段
        # 注意：这里使用SQLAlchemy实际上不会添加新字段，需要使用原生SQL
        # 但我们可以先创建模型，然后更新已有数据
        print("正在迁移操作日志表...")
        
        # 获取所有日志记录
        logs = OperationLog.query.all()
        
        # 记录已处理的日志数量
        processed = 0
        
        # 更新每个日志记录
        for log in logs:
            file_name = None
            file_type = None
            
            # 尝试从关联的文件中获取信息
            if log.file:
                file_name = log.file.original_filename
                file_type = log.file.file_type
            
            # 如果没有关联文件但是是删除操作，尝试从details中提取信息
            elif log.operation_type == 'delete' and log.details:
                try:
                    details = json.loads(log.details)
                    if 'file_info' in details:
                        file_info = details['file_info']
                        file_name = file_info.get('original_filename')
                        file_type = file_info.get('file_type')
                except:
                    pass
            
            # 更新日志记录
            log.file_name = file_name
            log.file_type = file_type
            processed += 1
        
        # 提交更改
        db.session.commit()
        print(f"成功迁移 {processed} 条操作日志记录")
    
    except Exception as e:
        db.session.rollback()
        print(f"迁移操作日志表失败: {str(e)}")

def create_default_roles():
    """创建默认角色和权限"""
    # 创建权限
    view_permission = Permission(name='view_content', description='查看内容')
    edit_permission = Permission(name='edit_content', description='编辑内容')
    delete_permission = Permission(name='delete_content', description='删除内容')
    manage_users = Permission(name='manage_users', description='管理用户')
    
    db.session.add_all([view_permission, edit_permission, delete_permission, manage_users])
    
    # 创建角色
    admin_role = Role(name='admin', description='管理员')
    editor_role = Role(name='editor', description='编辑')
    user_role = Role(name='user', description='普通用户')
    
    # 设置权限
    admin_role.permissions = [view_permission, edit_permission, delete_permission, manage_users]
    editor_role.permissions = [view_permission, edit_permission]
    user_role.permissions = [view_permission]
    
    db.session.add_all([admin_role, editor_role, user_role])
    
    print("默认角色和权限创建成功！")

def create_default_users():
    """创建默认用户"""
    # 创建管理员用户
    admin = User(
        username='admin',
        email='admin@example.com',
        password='admin123',
        full_name='系统管理员'
    )
    
    # 添加管理员角色
    admin_role = Role.query.filter_by(name='admin').first()
    admin.roles.append(admin_role)
    
    db.session.add(admin)
    
    print("默认用户创建成功！")

if __name__ == '__main__':
    init_db() 