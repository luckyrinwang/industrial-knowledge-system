#!/bin/bash

# 修复vite权限问题脚本 - Linux版本

echo "====================================================="
echo "    修复前端构建vite权限问题"
echo "====================================================="
echo

echo "1. 创建临时Dockerfile.frontend.fix文件..."
cp Dockerfile.frontend Dockerfile.frontend.fix

echo "2. 修改Dockerfile添加权限修复..."
cat > Dockerfile.frontend.fix << 'EOF'
# 前端Dockerfile - 权限修复版
FROM node:16-alpine as build-stage

# 设置工作目录
WORKDIR /app

# 复制package.json和package-lock.json
COPY frontend/package*.json ./

# 配置npm使用国内镜像
RUN npm config set registry https://registry.npmmirror.com/

# 安装依赖
RUN npm install

# 复制源码
COPY frontend/ .

# 确保node_modules中的文件有执行权限
RUN chmod -R 777 node_modules
RUN chmod +x node_modules/.bin/*
RUN ls -la node_modules/.bin/

# 构建生产版本
RUN npm run build

# 生产阶段
FROM nginx:stable-alpine as production-stage

# 从构建阶段复制构建结果到nginx静态资源目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
EOF

echo "3. 使用修复后的Dockerfile构建前端..."
docker build -t industrial-knowledge-system-frontend:latest -f Dockerfile.frontend.fix .

if [ $? -eq 0 ]; then
    echo "构建成功！替换原始Dockerfile..."
    mv Dockerfile.frontend.fix Dockerfile.frontend
    echo "修复完成！"
else
    echo "构建失败，尝试另一种方式..."
    
    echo "4. 创建更简化的Dockerfile..."
    cat > Dockerfile.frontend.simple << 'EOF'
# 前端Dockerfile - 强制权限修复版
FROM node:16-alpine as build-stage
WORKDIR /app
COPY frontend/ .
RUN npm config set registry https://registry.npmmirror.com/
RUN mkdir -p node_modules && chmod -R 777 node_modules
RUN npm install
RUN find node_modules/.bin -type f -exec chmod +x {} \;
RUN npm run build
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF
    
    echo "5. 尝试使用简化版Dockerfile构建..."
    docker build -t industrial-knowledge-system-frontend:latest -f Dockerfile.frontend.simple .
    
    if [ $? -eq 0 ]; then
        echo "构建成功！替换原始Dockerfile..."
        mv Dockerfile.frontend.simple Dockerfile.frontend
        echo "修复完成！"
    else
        echo "修复失败，尝试本地构建方式..."
        
        echo "6. 尝试在本地环境直接构建前端..."
        cd frontend
        npm install
        chmod -R 777 node_modules
        chmod +x node_modules/.bin/*
        npm run build
        
        if [ $? -eq 0 ]; then
            echo "本地构建成功！现在可以修改Dockerfile直接复制构建结果..."
            
            cd ..
            cat > Dockerfile.frontend.prebuilt << 'EOF'
# 前端Dockerfile - 使用预构建文件
FROM nginx:stable-alpine

# 复制已构建的前端文件
COPY frontend/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
EOF
            echo "创建了使用预构建文件的Dockerfile.frontend.prebuilt"
            echo "您可以使用: docker build -t industrial-knowledge-system-frontend:latest -f Dockerfile.frontend.prebuilt ."
        else
            echo "本地构建也失败，请检查项目配置。"
            rm -f Dockerfile.frontend.fix
            rm -f Dockerfile.frontend.simple
        fi
    fi
fi

echo
echo "处理完成！"
