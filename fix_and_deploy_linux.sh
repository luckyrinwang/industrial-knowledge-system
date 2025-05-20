#!/bin/bash
# 修复Nginx变量问题并部署项目

echo "======================================================"
echo "    修复Nginx变量问题并部署项目"
echo "======================================================"
echo

# 检查是否有执行权限
if [ ! -x "$(command -v chmod)" ]; then
  echo "错误: 无法执行chmod命令。请确保您有足够的权限。"
  exit 1
fi

# 首先执行fix_nginx_var.sh脚本
echo "1. 执行Nginx变量修复脚本..."
chmod +x fix_nginx_var.sh
./fix_nginx_var.sh

# 检查脚本执行结果
if [ $? -ne 0 ]; then
  echo "Nginx变量修复失败，退出部署。"
  exit 1
fi

# 设置环境变量
echo "2. 设置环境变量..."
export BACKEND_PORT=${BACKEND_PORT:-5000}
export FRONTEND_PORT=${FRONTEND_PORT:-3000}

# 关闭可能正在运行的容器
echo "3. 停止并删除现有容器（如果有）..."
docker compose -p knowledge down 2>/dev/null || true

# 构建并启动容器
echo "4. 构建并启动Docker容器..."
docker compose -p knowledge up --build -d

# 检查容器是否成功启动
echo "5. 检查容器状态..."
sleep 5
if docker compose -p knowledge ps | grep -q "Exit"; then
  echo "错误: 部分容器未能正常启动。"
  docker compose -p knowledge logs
  exit 1
fi

echo "======================================================"
echo "部署完成！"
echo "前端服务运行在: http://localhost:${FRONTEND_PORT}"
echo "后端API运行在: http://localhost:${BACKEND_PORT}/api"
echo "======================================================"
