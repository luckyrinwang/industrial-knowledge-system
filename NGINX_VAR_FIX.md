# Nginx变量问题解决方案

## 问题描述

在Linux系统中部署项目时，前端容器出现以下错误：

```
frontend-1  | 2025/05/20 08:27:37 [emerg] 1#1: unknown "backend_port" variable
frontend-1  | nginx: [emerg] unknown "backend_port" variable
```

这是因为Nginx配置文件中使用了`$backend_port`变量，但在Nginx启动前没有正确地设置这个变量或使用envsubst命令进行变量替换。

## 修复方法

1. **自动修复**：使用提供的`fix_and_deploy_linux.sh`脚本一键修复并部署项目

```bash
chmod +x fix_and_deploy_linux.sh
./fix_and_deploy_linux.sh
```

2. **手动修复**：如果自动脚本不起作用，可按照以下步骤手动修复

   a. 修改`Dockerfile.frontend`文件中的entrypoint脚本，确保正确处理变量：
   
   ```dockerfile
   # 创建启动脚本
   RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
       echo 'export backend_port=${BACKEND_PORT:-5000}' >> /docker-entrypoint.sh && \
       echo 'envsubst "\$backend_port" < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
       echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
       chmod +x /docker-entrypoint.sh
   ```
   
   b. 确保`nginx.conf`文件使用正确的变量名：
   
   ```
   proxy_pass http://backend:$backend_port;
   ```
   
   c. 重新构建并启动容器：
   
   ```bash
   docker-compose down
   docker-compose up --build -d
   ```

## 技术说明

该问题是由Nginx处理环境变量的方式引起的。在Dockerfile.frontend中，我们需要：

1. 将`nginx.conf`作为模板复制到容器中
2. 在容器启动时，使用envsubst命令将环境变量替换到模板中
3. 生成最终的Nginx配置文件
4. 启动Nginx服务

在上述修复中，关键是正确转义`$`符号，并使用`exec`确保nginx进程接收到正确的信号（比如SIGTERM），这有助于容器的优雅关闭。

## 防止问题再次发生

为了避免在不同环境中再次出现此问题，请确保：

1. 在部署前先运行`fix_nginx_var.sh`脚本
2. 使用`fix_and_deploy_linux.sh`脚本进行部署
3. 检查前端容器日志，确认没有Nginx配置错误
