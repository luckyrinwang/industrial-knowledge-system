#!/bin/bash
# Nginx变量问题自动修复脚本

echo "======================================================"
echo "    Nginx变量问题自动修复脚本"
echo "======================================================"
echo

# 创建备份
echo "1. 创建备份文件..."
cp -f nginx.conf nginx.conf.bak 2>/dev/null || echo "无法创建nginx.conf备份"
cp -f Dockerfile.frontend Dockerfile.frontend.bak 2>/dev/null || echo "无法创建Dockerfile.frontend备份"

# 修复nginx.conf
echo "2. 修复nginx.conf文件..."
sed -i 's/${BACKEND_PORT}/$backend_port/g' nginx.conf 2>/dev/null || \
  { echo "无法修改nginx.conf，请手动将\${BACKEND_PORT}替换为\$backend_port"; exit 1; }

# 创建启动脚本
echo "3. 创建docker-entrypoint.sh启动脚本..."
cat > docker-entrypoint.sh << 'EOF'
#!/bin/sh
export backend_port=${BACKEND_PORT:-5000}
envsubst "$$backend_port" < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g "daemon off;"
EOF
chmod +x docker-entrypoint.sh || echo "无法设置docker-entrypoint.sh执行权限"

# 修复Dockerfile
echo "4. 修复Dockerfile.frontend..."
cat > Dockerfile.frontend.new << 'EOF'
# 前端Dockerfile
FROM node:16-alpine as build-stage

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY frontend/package*.json ./

# 安装依赖
RUN npm install

# 复制源码
COPY frontend/ .

# 确保node_modules/.bin中的文件有执行权限
RUN chmod +x node_modules/.bin/*

# 构建生产版本
RUN npm run build

# 生产阶段
FROM nginx:stable-alpine as production-stage

# 从构建阶段复制构建结果到nginx静态资源目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制nginx配置为模板
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# 复制启动脚本并设置执行权限
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["/docker-entrypoint.sh"]
EOF

mv Dockerfile.frontend.new Dockerfile.frontend 2>/dev/null || { 
  echo "无法替换Dockerfile.frontend，请手动修改"; 
  echo "新文件已保存为Dockerfile.frontend.new"; 
}

echo "5. 添加.dockerignore文件（如果不存在）..."
if [ ! -f .dockerignore ]; then
  cat > .dockerignore << 'EOF'
.git
.gitignore
README.md
DOCKER_GUIDE.md
NGINX_VAR_FIX.md
*.md
*.log
*.bak
**/__pycache__
venv/
backend/venv/
frontend/node_modules/
EOF
  echo ".dockerignore文件已创建"
else
  echo ".dockerignore文件已存在，跳过"
fi

# 检查docker-compose.yml
echo "6. 检查docker-compose.yml文件..."
if grep -q "BACKEND_PORT" docker-compose.yml; then
  echo "docker-compose.yml中已包含BACKEND_PORT环境变量，无需修改"
else
  echo "提示: 您可能需要在docker-compose.yml的frontend服务中添加环境变量:"
  echo "  environment:"
  echo "    - BACKEND_PORT=5000"
fi

echo
echo "修复完成！请执行以下命令重新构建并启动容器:"
echo "docker-compose down"
echo "docker-compose build frontend"
echo "docker-compose up -d"
echo
echo "如果仍然遇到问题，请查看NGINX_VAR_FIX.md获取更多帮助。"
