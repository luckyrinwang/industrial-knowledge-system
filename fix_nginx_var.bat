@echo off
REM Nginx变量问题自动修复脚本 - Windows版本

echo ======================================================
echo     Nginx变量问题自动修复脚本
echo ======================================================
echo.

REM 创建备份
echo 1. 创建备份文件...
copy /Y nginx.conf nginx.conf.bak >nul 2>&1 || echo 无法创建nginx.conf备份
copy /Y Dockerfile.frontend Dockerfile.frontend.bak >nul 2>&1 || echo 无法创建Dockerfile.frontend备份

REM 修复nginx.conf
echo 2. 修复nginx.conf文件...
powershell -Command "(Get-Content nginx.conf) -replace '\${BACKEND_PORT}', '$backend_port' | Set-Content nginx.conf"
if %ERRORLEVEL% NEQ 0 (
  echo 无法修改nginx.conf，请手动将${BACKEND_PORT}替换为$backend_port
  exit /b 1
)

REM 创建启动脚本
echo 3. 创建docker-entrypoint.sh启动脚本...
(
echo #!/bin/sh
echo export backend_port=${BACKEND_PORT:-5000}
echo envsubst "$$backend_port" ^< /etc/nginx/conf.d/default.conf.template ^> /etc/nginx/conf.d/default.conf
echo exec nginx -g "daemon off;"
) > docker-entrypoint.sh

REM 修复Dockerfile
echo 4. 修复Dockerfile.frontend...
(
echo # 前端Dockerfile
echo FROM node:16-alpine as build-stage
echo.
echo # 设置工作目录
echo WORKDIR /app
echo.
echo # 复制package.json和package-lock.json
echo COPY frontend/package*.json ./
echo.
echo # 安装依赖
echo RUN npm install
echo.
echo # 复制源码
echo COPY frontend/ .
echo.
echo # 确保node_modules/.bin中的文件有执行权限
echo RUN chmod +x node_modules/.bin/*
echo.
echo # 构建生产版本
echo RUN npm run build
echo.
echo # 生产阶段
echo FROM nginx:stable-alpine as production-stage
echo.
echo # 从构建阶段复制构建结果到nginx静态资源目录
echo COPY --from=build-stage /app/dist /usr/share/nginx/html
echo.
echo # 复制nginx配置为模板
echo COPY nginx.conf /etc/nginx/conf.d/default.conf.template
echo.
echo # 复制启动脚本并设置执行权限
echo COPY docker-entrypoint.sh /
echo RUN chmod +x /docker-entrypoint.sh
echo.
echo # 暴露端口
echo EXPOSE 80
echo.
echo # 启动nginx
echo CMD ["/docker-entrypoint.sh"]
) > Dockerfile.frontend.new

move /Y Dockerfile.frontend.new Dockerfile.frontend >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo 无法替换Dockerfile.frontend，请手动修改
  echo 新文件已保存为Dockerfile.frontend.new
)

echo 5. 添加.dockerignore文件（如果不存在）...
if not exist .dockerignore (
  (
  echo .git
  echo .gitignore
  echo README.md
  echo DOCKER_GUIDE.md
  echo NGINX_VAR_FIX.md
  echo *.md
  echo *.log
  echo *.bak
  echo **/__pycache__
  echo venv/
  echo backend/venv/
  echo frontend/node_modules/
  ) > .dockerignore
  echo .dockerignore文件已创建
) else (
  echo .dockerignore文件已存在，跳过
)

REM 检查docker-compose.yml
echo 6. 检查docker-compose.yml文件...
findstr /C:"BACKEND_PORT" docker-compose.yml >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  echo docker-compose.yml中已包含BACKEND_PORT环境变量，无需修改
) else (
  echo 提示: 您可能需要在docker-compose.yml的frontend服务中添加环境变量:
  echo   environment:
  echo     - BACKEND_PORT=5000
)

echo.
echo 修复完成！请执行以下命令重新构建并启动容器:
echo docker-compose down
echo docker-compose build frontend
echo docker-compose up -d
echo.
echo 如果仍然遇到问题，请查看NGINX_VAR_FIX.md获取更多帮助。

pause
