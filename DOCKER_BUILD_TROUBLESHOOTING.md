# Docker 构建问题解决指南

## 常见问题

在使用 Docker 部署本项目时，可能会遇到以下常见问题：

### 1. Debian 软件源连接超时

**错误信息示例：**
```
Connection timed out [IP: 151.101.66.132 80]
```

**原因：**
- 网络环境限制，无法连接到官方 Debian 源
- 防火墙或网络策略阻止了容器与外部网络的通信
- Docker 构建过程中网络不稳定

**解决方案：**
- 使用国内 Debian 镜像源（已在 Dockerfile.backend 中配置）
- 增加 apt-get 超时设置和重试次数
- 使用代理服务器（如有）

### 2. Vite 权限问题

**错误信息示例：**
```
sh: vite: Permission denied
```

**原因：**
- Docker 容器内的 node_modules/.bin 目录中的可执行文件没有执行权限
- Linux 与 Windows 文件权限处理方式不同导致的问题

**解决方案：**
- 在 Dockerfile.frontend 中添加 chmod 命令授予执行权限
- 使用 `fix_frontend_build.sh` (Linux) 或 `fix_frontend_build.bat` (Windows) 脚本修复
- 在本地构建前端，然后使用预构建文件的 Dockerfile

## 快速修复步骤

### 在 Linux 上：

1. 修复前端构建问题：
   ```bash
   chmod +x fix_frontend_build.sh
   ./fix_frontend_build.sh
   ```

2. 使用简化配置构建：
   ```bash
   docker-compose -f docker-compose.simple.yml build
   docker-compose -f docker-compose.simple.yml up -d
   ```

### 在 Windows 上：

1. 修复前端构建问题：
   ```cmd
   fix_frontend_build.bat
   ```

2. 使用简化配置构建：
   ```cmd
   docker-compose -f docker-compose.simple.yml build
   docker-compose -f docker-compose.simple.yml up -d
   ```

## 高级解决方案

如果上述方法无法解决问题，可以尝试以下高级方法：

### 预构建前端

1. 在本地环境构建前端：
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. 使用预构建文件创建容器：
   ```bash
   docker build -t industrial-knowledge-system-frontend:latest -f Dockerfile.frontend.prebuilt .
   ```

### 使用本地离线依赖

1. 下载所有依赖到本地：
   ```bash
   pip download -r requirements.txt -d ./pip_cache
   ```

2. 修改 Dockerfile 使用本地依赖：
   ```dockerfile
   COPY pip_cache /app/pip_cache
   RUN pip install --no-index --find-links=/app/pip_cache -r requirements.txt
   ```

## 其他常见 Docker 问题

### 容器间通信问题

如果 frontend 无法连接到 backend，请检查：

1. Docker 网络配置是否正确
2. backend 服务是否正常运行
3. 端口映射是否配置正确

### 数据持久化问题

如果数据未正确持久化，请检查：

1. Docker 卷配置是否正确
2. 权限问题是否阻止了写入操作

### 资源限制问题

如果构建过程中出现内存不足或 CPU 限制问题：

1. 增加 Docker 可用资源（在 Docker Desktop 设置中）
2. 拆分构建步骤，分别构建前端和后端

## 更多帮助

如果以上方法无法解决问题，请：

1. 检查 Docker 日志：`docker-compose logs`
2. 进入容器内部调试：`docker-compose exec backend /bin/bash`
3. 联系支持团队获取更多帮助
