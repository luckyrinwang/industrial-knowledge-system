import os

# Flask应用配置
SECRET_KEY = 'dev_secret_key'
DEBUG = True

# JWT配置
JWT_SECRET_KEY = 'jwt_dev_secret_key'

# 数据库配置
# MySQL配置 - 用户名和密码均为root
DATABASE_URI = 'mysql+pymysql://root:root@localhost/industrial_knowledge'

# SQLite配置(备用)
# DATABASE_URI = 'sqlite:///industrial_knowledge.db'

# 其他配置项
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 