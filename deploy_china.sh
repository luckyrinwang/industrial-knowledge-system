#!/bin/bash

# 工业知识库系统 - 中国大陆一键部署脚本
# Industrial Knowledge System - China Quick Deploy Script

set -e

echo "🚀 开始部署工业知识库系统..."
echo "📍 针对中国大陆网络环境优化"
echo "================================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 配置Docker镜像加速（仅Linux）
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 配置Docker镜像加速..."
    
    # 检查是否已配置镜像加速
    if [ ! -f /etc/docker/daemon.json ]; then
        echo "📝 创建Docker镜像加速配置..."
        sudo mkdir -p /etc/docker
        
        sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://mirror.baidubce.com",
    "https://reg-mirror.qiniu.com"
  ],
  "experimental": false,
  "debug": true,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF
        
        echo "🔄 重启Docker服务..."
        sudo systemctl daemon-reload
        sudo systemctl restart docker
        
        echo "✅ Docker镜像加速配置完成"
    else
        echo "✅ Docker镜像加速已配置"
    fi
fi

# 检查端口占用
echo "🔍 检查端口占用情况..."

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 3000 已被占用，请手动停止相关服务或修改 docker-compose.yml 中的端口配置"
    read -p "是否继续部署？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 5000 已被占用，请手动停止相关服务或修改 docker-compose.yml 中的端口配置"
    read -p "是否继续部署？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ 端口检查完成"

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p backend/uploads/{document,image,pdf,md,spreadsheet,video}
mkdir -p backend/logs

# 复制配置文件模板
if [ ! -f backend/config.env ]; then
    echo "📝 创建后端配置文件..."
    if [ -f backend/config.env.example ]; then
        cp backend/config.env.example backend/config.env
        echo "✅ 已复制配置模板，请根据需要修改 backend/config.env"
    else
        echo "⚠️  配置模板文件不存在，使用默认配置"
    fi
fi

# 构建并启动服务
echo "🏗️  构建Docker镜像..."
echo "💡 首次构建可能需要较长时间，请耐心等待..."

# 使用国内镜像源构建
DOCKER_BUILDKIT=1 docker-compose build --no-cache --progress=plain

if [ $? -ne 0 ]; then
    echo "❌ 镜像构建失败，请检查网络连接或查看错误信息"
    exit 1
fi

echo "🚀 启动服务..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ 服务启动失败"
    exit 1
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 初始化数据库
echo "🗄️  初始化数据库..."
docker-compose exec -T backend python init_db.py

echo ""
echo "🎉 部署完成！"
echo "================================================"
echo "📱 访问地址："
echo "   前端应用: http://localhost:3000"
echo "   后端API:  http://localhost:5000"
echo ""
echo "🔧 管理命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose stop"
echo "   重启服务: docker-compose restart"
echo "   完全清理: docker-compose down"
echo ""
echo "📚 更多信息请查看 README.md 和 SETUP_GUIDE.md"
echo ""

# 检查服务是否正常运行
echo "🩺 健康检查..."
sleep 5

if curl -f http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ 后端服务运行正常"
else
    echo "⚠️  后端服务可能存在问题，请查看日志："
    echo "   docker-compose logs backend"
fi

if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ 前端服务运行正常"
else
    echo "⚠️  前端服务可能存在问题，请查看日志："
    echo "   docker-compose logs frontend"
fi

echo ""
echo "🎊 欢迎使用工业知识库系统！"
