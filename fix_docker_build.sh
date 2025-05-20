#!/bin/bash
# Docker构建问题一键修复脚本

echo "==========================================="
echo "   Docker构建问题一键修复脚本"
echo "==========================================="
echo ""

# 检查是否有管理员权限
if [ "$EUID" -ne 0 ]; then
  echo "请使用管理员权限运行此脚本:"
  echo "sudo $0"
  exit 1
fi

echo "1. 修复Docker配置..."

# 创建docker配置目录
mkdir -p /etc/docker

# 配置Docker镜像加速
cat > /etc/docker/daemon.json <<EOL
{
  "registry-mirrors": [
    "https://registry.docker-cn.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOL

echo "2. 重启Docker服务..."
systemctl restart docker

echo "3. 拉取基础镜像..."
docker pull python:3.9-slim

echo "4. 创建特殊构建环境..."
mkdir -p docker-build-fix
cd docker-build-fix

# 创建修复版Dockerfile
cat > Dockerfile.backend.fixed <<EOL
# 后端Dockerfile - 修复版本
FROM python:3.9-slim

# 设置国内Debian镜像源
RUN echo 'deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware' > /etc/apt/sources.list && \\
    echo 'deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware' >> /etc/apt/sources.list && \\
    echo 'deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware' >> /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && \\
    apt-get install -y --no-install-recommends \\
        libreoffice \\
        unoconv \\
        ca-certificates \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 设置pip配置
RUN pip config set global.timeout 300 && \\
    pip config set global.retries 10 && \\
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \\
    pip config set global.trusted-host mirrors.aliyun.com

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用程序代码
COPY backend/ .

# 创建上传目录
RUN mkdir -p uploads && chmod 777 uploads

# 设置端口
ENV PORT=5000
EXPOSE \${PORT}

# 运行应用
CMD ["python", "run.py"]
EOL

# 创建修复版Docker Compose文件
cat > docker-compose.fixed.yml <<EOL
version: '3'

services:
  # MySQL数据库
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: industrial_knowledge
      MYSQL_USER: industrial_user
      MYSQL_PASSWORD: industrial_password
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - app_network

  # 后端API服务（使用修改版Dockerfile）
  backend:
    build:
      context: ..
      dockerfile: docker-build-fix/Dockerfile.backend.fixed
    restart: always
    depends_on:
      - db
    environment:
      - SECRET_KEY=production_secret_key
      - JWT_SECRET_KEY=production_jwt_secret_key
      - DATABASE_URI=mysql+pymysql://industrial_user:industrial_password@db/industrial_knowledge
      - PORT=5000
    ports:
      - "5000:5000"
    volumes:
      - uploads_data:/app/uploads
    networks:
      - app_network
    # 增加网络超时
    command: >
      bash -c "
        echo 'Waiting for database to be ready...'
        sleep 10
        python run.py
      "

  # 前端Web服务
  frontend:
    build:
      context: ..
      dockerfile: Dockerfile.frontend
    restart: always
    depends_on:
      - backend
    ports:
      - "80:80"
    networks:
      - app_network

# 持久化卷
volumes:
  db_data:
  uploads_data:

# 网络配置
networks:
  app_network:
    driver: bridge
EOL

echo "5. 设置环境变量..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_CLIENT_TIMEOUT=300
export COMPOSE_HTTP_TIMEOUT=300

echo "6. 启动修复版环境..."
cd ..
docker-compose -f docker-build-fix/docker-compose.fixed.yml up -d

echo "==========================================="
echo "修复完成! 系统应该正在启动中。"
echo "如果仍然遇到问题，请参考以下文档:"
echo " - DOCKER_DEBIAN_TIMEOUT_FIX.md"
echo " - PIP_TIMEOUT_FIX.md"
echo " - DOCKER_GUI_TOOLS.md"
echo "==========================================="
