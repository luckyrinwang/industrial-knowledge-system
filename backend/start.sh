#!/bin/bash
# 等待数据库启动
echo "等待数据库服务准备就绪..."
sleep 10

# 初始化数据库
echo "初始化数据库..."
python init_db.py

# 启动应用
echo "启动应用程序..."
exec python run.py
