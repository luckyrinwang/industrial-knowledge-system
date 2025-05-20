#!/bin/bash
# 端口配置测试脚本 test_port_config.sh

echo "=========================================="
echo "   端口配置测试脚本"
echo "=========================================="

# 检查后端端口配置
if [ -f "backend/config.env" ]; then
    BACKEND_PORT=$(grep "PORT=" backend/config.env | cut -d'=' -f2)
    echo "后端配置文件中的端口: $BACKEND_PORT"
else
    echo "警告: 未找到backend/config.env配置文件"
fi

# 检查前端端口配置
if [ -f "frontend/.env" ]; then
    FRONTEND_PORT=$(grep "FRONTEND_PORT=" frontend/.env | cut -d'=' -f2)
    BACKEND_PORT_FE=$(grep "BACKEND_PORT=" frontend/.env | cut -d'=' -f2)
    BACKEND_URL=$(grep "BACKEND_URL=" frontend/.env | cut -d'=' -f2)
    
    echo "前端配置文件中的前端端口: $FRONTEND_PORT"
    echo "前端配置文件中的后端端口: $BACKEND_PORT_FE"
    echo "前端配置文件中的后端URL: $BACKEND_URL"
else
    echo "警告: 未找到frontend/.env配置文件"
fi

# 检查Docker环境变量
if [ -f ".env" ]; then
    DOCKER_FRONTEND_PORT=$(grep "FRONTEND_PORT=" .env | cut -d'=' -f2)
    DOCKER_BACKEND_PORT=$(grep "BACKEND_PORT=" .env | cut -d'=' -f2)
    
    echo "Docker配置文件中的前端端口: $DOCKER_FRONTEND_PORT"
    echo "Docker配置文件中的后端端口: $DOCKER_BACKEND_PORT"
else
    echo "信息: 未找到Docker .env配置文件"
fi

# 检查端口占用情况
echo ""
echo "检查端口占用情况..."

# 检查常用端口是否被占用
check_port() {
    if command -v netstat &> /dev/null; then
        netstat -tuln | grep ":$1 "
        if [ $? -eq 0 ]; then
            echo "警告: 端口 $1 已被占用!"
        else
            echo "信息: 端口 $1 可用。"
        fi
    elif command -v ss &> /dev/null; then
        ss -tuln | grep ":$1 "
        if [ $? -eq 0 ]; then
            echo "警告: 端口 $1 已被占用!"
        else
            echo "信息: 端口 $1 可用。"
        fi
    else
        echo "无法检查端口占用情况，请安装 netstat 或 ss 工具。"
        return
    fi
}

# 检查默认端口和配置端口
check_port 5000
check_port 3000
check_port 80

if [ ! -z "$BACKEND_PORT" ]; then
    check_port $BACKEND_PORT
fi

if [ ! -z "$FRONTEND_PORT" ]; then
    check_port $FRONTEND_PORT
fi

echo ""
echo "端口配置测试完成。"
