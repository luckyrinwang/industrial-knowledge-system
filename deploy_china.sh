#!/bin/bash
# 执行前请添加执行权限: chmod +x deploy_china.sh

# 工业知识库系统 - 中国地区一键部署脚本

echo "=== 工业知识库系统 - 中国地区一键部署 ==="
echo "正在为中国网络环境优化Docker配置..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "需要管理员权限来配置Docker镜像源"
    echo "正在尝试使用sudo..."
    exec sudo "$0" "$@"
fi

# 运行修复脚本
echo "步骤1: 修复Docker镜像源配置..."
bash docker_fix.sh

if [ $? -ne 0 ]; then
    echo "❌ Docker配置失败，尝试继续部署..."
fi

# 切换回普通用户权限进行Docker操作
USER_HOME=$(eval echo ~${SUDO_USER})
cd "$(dirname "$0")"

echo ""
echo "步骤2: 开始部署工业知识库系统..."

# 清理之前的部署
echo "清理之前的部署..."
docker compose -p knowledge down 2>/dev/null || true
docker system prune -f

# 构建和启动服务
echo "构建和启动服务..."
if docker compose -p knowledge up -d --build; then
    echo ""
    echo "✅ 部署成功！"
    echo ""
    echo "=== 服务信息 ==="
    echo "前端访问地址: http://localhost:3000"
    echo "后端API地址: http://localhost:5000"
    echo ""
    echo "默认登录账户:"
    echo "用户名: admin"
    echo "密码: admin123"
    echo ""
    echo "=== 常用命令 ==="
    echo "查看服务状态: docker compose -p knowledge ps"
    echo "查看日志: docker compose -p knowledge logs -f"
    echo "停止服务: docker compose -p knowledge down"
    echo "重启服务: docker compose -p knowledge restart"
else
    echo ""
    echo "❌ 部署失败！"
    echo ""
    echo "=== 故障排除建议 ==="
    echo "1. 检查网络连接"
    echo "2. 查看详细错误: docker compose -p knowledge logs"
    echo "3. 手动拉取镜像:"
    echo "   docker pull python:3.9-slim"
    echo "   docker pull node:16-alpine"
    echo "   docker pull nginx:stable-alpine"
    echo "4. 参考故障排除指南: cat DOCKER_QUICK_FIX.md"
    echo ""
    exit 1
fi
