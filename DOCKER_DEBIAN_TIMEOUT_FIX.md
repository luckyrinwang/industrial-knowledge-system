# Docker构建中的Debian仓库连接超时解决方案

## 问题描述

在使用Docker构建"基于大模型的工业知识库系统"时，遇到了以下错误：

```
Err:4 http://deb.debian.org/debian bookworm/main amd64 Packages
Connection timed out [IP: 151.101.66.132 80]
```

这是因为在构建Docker镜像过程中，安装系统依赖`libreoffice`和`unoconv`时无法连接到默认的Debian软件源(deb.debian.org)。

## 解决方案

### 方案1：使用国内Debian镜像源（推荐）

已经提供了修改版的`Dockerfile.backend`，它使用了清华大学TUNA镜像源来替代默认的Debian软件源。

使用方法与标准部署相同：
```bash
docker-compose up -d
```

### 方案2：使用最小依赖版本

如果仍然遇到网络问题，可以使用`Dockerfile.backend.minimal`，它：

1. 减少了对外部依赖的需求
2. 使用多阶段构建减小镜像大小
3. 提供了一个纯Python的替代方案来替代LibreOffice

使用方法：
```bash
# 修改docker-compose.yml中的backend服务使用Dockerfile.backend.minimal
docker-compose up -d
```

### 方案3：完全离线构建

如果网络环境非常受限，可以考虑以下步骤：

1. 在网络良好的环境中预先拉取基础镜像：
```bash
docker pull python:3.9-slim
docker save -o python-slim.tar python:3.9-slim
```

2. 将镜像文件和源代码传输到目标环境：
```bash
# 在目标环境加载镜像
docker load -i python-slim.tar
```

3. 使用本地构建方式：
```bash
docker build -t industrial-knowledge-backend -f Dockerfile.backend.minimal .
```

## 适配本地环境的其他建议

1. **使用VPN或代理**：
   ```bash
   export http_proxy=http://your-proxy:port
   export https_proxy=http://your-proxy:port
   docker-compose up -d
   ```

2. **修改Docker镜像源**：
   在`/etc/docker/daemon.json`中添加：
   ```json
   {
     "registry-mirrors": [
       "https://registry.docker-cn.com",
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ]
   }
   ```
   然后重启Docker服务：
   ```bash
   sudo systemctl restart docker
   ```

3. **增加构建超时**：
   ```bash
   DOCKER_BUILDKIT=1 DOCKER_TIMEOUT=600 docker-compose up -d
   ```

## 替代方案：不使用Docker

如果Docker环境问题无法解决，可以考虑使用传统方式部署：

1. 按照`SETUP_GUIDE.md`中的指南直接在服务器上设置环境
2. 使用`setup_linux.sh`脚本自动配置环境
3. 手动启动前后端服务
