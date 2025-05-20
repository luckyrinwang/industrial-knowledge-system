"""
数据库迁移脚本，用于在files表中添加ragflow_doc_id字段
"""
import sqlite3
import os
import sys

# 获取当前文件目录
current_dir = os.path.dirname(os.path.abspath(__file__))
db_file = os.path.join(current_dir, 'industrial_knowledge.db')

def add_ragflow_doc_id_column():
    print(f"正在连接数据库: {db_file}")
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_file):
        print(f"错误: 数据库文件 {db_file} 不存在!")
        return False
    
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 检查是否已经存在ragflow_doc_id列
        cursor.execute("PRAGMA table_info(files)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'ragflow_doc_id' in column_names:
            print("ragflow_doc_id列已存在，无需添加")
            conn.close()
            return True
        
        # 添加新列
        print("正在添加ragflow_doc_id列...")
        cursor.execute("ALTER TABLE files ADD COLUMN ragflow_doc_id TEXT;")
        
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
        
        print("成功添加ragflow_doc_id列!")
        return True
    except Exception as e:
        print(f"错误: {str(e)}")
        return False

if __name__ == "__main__":
    add_ragflow_doc_id_column()
