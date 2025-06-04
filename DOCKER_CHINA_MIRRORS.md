# Docker中国镜像源配置指南

## 问题描述
在中国部署Docker时，由于网络原因，从Docker Hub拉取镜像可能会超时或失败。

## 解决方案

### 1. 配置Docker镜像源（推荐）

#### Linux系统配置
```bash
# 创建或编辑Docker配置文件
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF

# 重启Docker服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### 或者复制项目中的配置文件
```bash
# 复制项目提供的配置文件
sudo cp daemon.json /etc/docker/daemon.json
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 2. 验证配置
```bash
# 查看Docker配置
docker info | grep -A 5 "Registry Mirrors"
```

### 3. 重新构建项目
```bash
# 清理之前失败的构建
docker compose -p knowledge down
docker system prune -f

# 重新构建和启动
docker compose -p knowledge up -d --build
```

## 镜像源说明

本项目已经配置了以下中国镜像源：

### Docker基础镜像
- 后端：`registry.cn-hangzhou.aliyuncs.com/library/python:3.9-slim`
- 前端：`registry.cn-hangzhou.aliyuncs.com/library/node:16-alpine`
- Nginx：`registry.cn-hangzhou.aliyuncs.com/library/nginx:stable-alpine`

### Python包镜像源
- 阿里云：`https://mirrors.aliyun.com/pypi/simple/`
- 清华大学：`https://pypi.tuna.tsinghua.edu.cn/simple/`
- 腾讯云：`https://mirrors.cloud.tencent.com/pypi/simple/`

### NPM包镜像源
- npmmirror：`https://registry.npmmirror.com`
- 淘宝镜像：`https://registry.npm.taobao.org`
- 腾讯云：`https://mirrors.cloud.tencent.com/npm/`

### APT包镜像源
- 阿里云：`https://mirrors.aliyun.com/debian/`
- 清华大学：`https://mirrors.tuna.tsinghua.edu.cn/debian/`

## 故障排除

如果仍然遇到网络问题，可以尝试：

1. 检查网络连接
2. 尝试不同的镜像源
3. 增加构建超时时间：
   ```bash
   export DOCKER_CLIENT_TIMEOUT=600
   export COMPOSE_HTTP_TIMEOUT=600
   docker compose -p knowledge up -d --build
   ```

4. 使用代理构建（如果有代理服务器）：
   ```bash
   docker compose -p knowledge build --build-arg HTTP_PROXY=http://your-proxy:port --build-arg HTTPS_PROXY=http://your-proxy:port
   ```
