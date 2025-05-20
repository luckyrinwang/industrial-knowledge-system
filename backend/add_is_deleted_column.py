"""
向文件表添加is_deleted字段
"""
from app import app, db
import sys

def add_is_deleted_column():
    """向files表添加is_deleted字段"""
    with app.app_context():
        try:
            # 使用原生SQL添加字段
            db.session.execute("ALTER TABLE files ADD COLUMN is_deleted BOOLEAN DEFAULT 0")
            db.session.commit()
            print("成功添加is_deleted字段到files表")
            return True
        except Exception as e:
            print(f"添加字段失败: {str(e)}")
            # 如果是字段已存在的错误，返回True
            if "Duplicate column name" in str(e) or "already exists" in str(e):
                return True
            return False

if __name__ == "__main__":
    print("开始更新文件表...")
    
    if add_is_deleted_column():
        print("更新文件表成功!")
    else:
        print("更新文件表失败!")
        sys.exit(1) 