# Nginx变量问题修复指南

如果您在Linux上使用Docker部署时遇到以下错误：

```
frontend-1  | 2025/05/20 07:54:28 [emerg] 1#1: unknown "backend_port" variable
frontend-1  | nginx: [emerg] unknown "backend_port" variable
```

请按照以下步骤修复问题：

## 方法1: 使用已修复的代码重新构建

1. 拉取最新代码（如果您的代码仓库中已包含修复）
   ```bash
   git pull
   ```

2. 重新构建并启动容器
   ```bash
   docker-compose down
   docker-compose build frontend
   docker-compose up -d
   ```

## 方法2: 手动修复（如果您没有最新代码）

1. 修改nginx.conf文件
   ```bash
   # 备份原始文件
   cp nginx.conf nginx.conf.bak
   
   # 修改文件 - 将${BACKEND_PORT}替换为$backend_port
   sed -i 's/${BACKEND_PORT}/$backend_port/g' nginx.conf
   ```

2. 创建一个docker-entrypoint.sh脚本
   ```bash
   cat > docker-entrypoint.sh << 'EOF'
   #!/bin/sh
   export backend_port=${BACKEND_PORT:-5000}
   envsubst '$backend_port' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf
   nginx -g "daemon off;"
   EOF
   
   chmod +x docker-entrypoint.sh
   ```

3. 修改Dockerfile.frontend
   ```bash
   # 备份原始文件
   cp Dockerfile.frontend Dockerfile.frontend.bak
   
   # 修改文件 - 更改nginx配置文件的处理方式
   sed -i 's|COPY nginx.conf /etc/nginx/conf.d/default.conf|COPY nginx.conf /etc/nginx/conf.d/default.conf.template|' Dockerfile.frontend
   
   # 修改启动命令
   sed -i 's|CMD \["nginx", "-g", "daemon off;"\]|COPY docker-entrypoint.sh /\nCMD ["/docker-entrypoint.sh"]|' Dockerfile.frontend
   ```

4. 重新构建并启动容器
   ```bash
   docker-compose down
   docker-compose build frontend
   docker-compose up -d
   ```

## 方法3: 快速修复（无需修改文件）

如果您不想修改任何文件，可以直接在运行时指定一个固定的后端端口：

1. 修改docker-compose.yml
   ```bash
   # 备份原始文件
   cp docker-compose.yml docker-compose.yml.bak
   
   # 在frontend服务中添加环境变量
   # 找到frontend部分，添加下面的环境变量配置
   sed -i '/frontend:/,/}/s/}/  environment:\n    - BACKEND_PORT=5000\n}/' docker-compose.yml
   ```

2. 重新启动容器
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## 检查修复是否成功

修复后，您可以检查容器日志，确认问题是否解决：

```bash
docker-compose logs frontend
```

如果没有看到之前的错误，说明修复成功。

## 进一步帮助

如果上述方法都不起作用，您也可以直接进入容器内部手动修复：

```bash
# 进入前端容器
docker-compose exec frontend sh

# 在容器内修改nginx配置
sed -i 's/${BACKEND_PORT}/5000/g' /etc/nginx/conf.d/default.conf

# 重新加载nginx配置
nginx -s reload
```

如需更多帮助，请参考项目的DOCKER_GUIDE.md文档或联系支持团队。
