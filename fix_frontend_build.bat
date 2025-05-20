@echo off
REM 修复vite权限问题脚本

echo =====================================================
echo    修复前端构建vite权限问题
echo =====================================================
echo.

echo 1. 创建临时Dockerfile.frontend.fix文件...
copy Dockerfile.frontend Dockerfile.frontend.fix

echo 2. 修改Dockerfile添加权限修复...
(
echo # 前端Dockerfile - 权限修复版
echo FROM node:16-alpine as build-stage
echo.
echo # 设置工作目录
echo WORKDIR /app
echo.
echo # 复制package.json和package-lock.json
echo COPY frontend/package*.json ./
echo.
echo # 配置npm使用国内镜像
echo RUN npm config set registry https://registry.npmmirror.com/
echo.
echo # 安装依赖
echo RUN npm install
echo.
echo # 复制源码
echo COPY frontend/ .
echo.
echo # 确保node_modules中的文件有执行权限
echo RUN chmod -R 777 node_modules
echo RUN chmod +x node_modules/.bin/*
echo RUN ls -la node_modules/.bin/
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
echo # 复制nginx配置
echo COPY nginx.conf /etc/nginx/conf.d/default.conf
echo.
echo # 暴露端口
echo EXPOSE 80
echo.
echo # 启动nginx
echo CMD ["nginx", "-g", "daemon off;"]
) > Dockerfile.frontend.fix

echo 3. 使用修复后的Dockerfile构建前端...
docker build -t industrial-knowledge-system-frontend:latest -f Dockerfile.frontend.fix .

if %ERRORLEVEL% EQU 0 (
    echo 构建成功！替换原始Dockerfile...
    move /y Dockerfile.frontend.fix Dockerfile.frontend
    echo 修复完成！
) else (
    echo 构建失败，尝试另一种方式...
    
    echo 4. 创建更简化的Dockerfile...
    (
    echo # 前端Dockerfile - 强制权限修复版
    echo FROM node:16-alpine as build-stage
    echo WORKDIR /app
    echo COPY frontend/ .
    echo RUN npm config set registry https://registry.npmmirror.com/
    echo RUN mkdir -p node_modules && chmod -R 777 node_modules
    echo RUN npm install
    echo RUN find node_modules/.bin -type f -exec chmod +x {} \;
    echo RUN npm run build
    echo FROM nginx:stable-alpine as production-stage
    echo COPY --from=build-stage /app/dist /usr/share/nginx/html
    echo COPY nginx.conf /etc/nginx/conf.d/default.conf
    echo EXPOSE 80
    echo CMD ["nginx", "-g", "daemon off;"]
    ) > Dockerfile.frontend.simple
    
    echo 5. 尝试使用简化版Dockerfile构建...
    docker build -t industrial-knowledge-system-frontend:latest -f Dockerfile.frontend.simple .
    
    if %ERRORLEVEL% EQU 0 (
        echo 构建成功！替换原始Dockerfile...
        move /y Dockerfile.frontend.simple Dockerfile.frontend
        echo 修复完成！
    ) else (
        echo 修复失败，请手动检查问题。
        echo 可能的解决方案：
        echo 1. 在Linux环境下直接构建前端：cd frontend && npm install && npm run build
        echo 2. 尝试在package.json中修改build命令以明确指定vite路径
        del Dockerfile.frontend.fix
        del Dockerfile.frontend.simple
    )
)

echo.
echo 处理完成！
pause
