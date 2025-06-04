# 中国Docker镜像源快速修复指南

## 问题描述
在中国使用Docker时，经常遇到镜像拉取失败的问题，主要原因是：
1. Docker Hub访问缓慢或超时
2. 某些镜像源不可用或需要认证

## 推荐解决方案

### 方案1：使用可靠的Docker镜像源（推荐）

执行以下命令配置Docker镜像源：

```bash
# Linux系统
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "dns": ["8.8.8.8", "114.114.114.114"]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 方案2：使用Docker代理服务

如果上述镜像源仍然不可用，可以使用以下代理服务：

```bash
# 临时使用代理构建
docker build --build-arg HTTP_PROXY=http://127.0.0.1:7890 \
             --build-arg HTTPS_PROXY=http://127.0.0.1:7890 \
             -f Dockerfile.backend .
```

### 方案3：手动拉取镜像

```bash
# 手动拉取所需镜像
docker pull python:3.9-slim
docker pull node:16-alpine  
docker pull nginx:stable-alpine

# 然后构建项目
docker compose -p knowledge up -d --build
```

### 方案4：使用离线镜像

如果网络环境较差，可以：

1. 在网络环境较好的机器上导出镜像：
```bash
docker save python:3.9-slim node:16-alpine nginx:stable-alpine | gzip > base-images.tar.gz
```

2. 在目标机器上导入镜像：
```bash
gunzip -c base-images.tar.gz | docker load
```

## 验证和部署

配置完成后，验证Docker配置：
```bash
docker info | grep -A 5 "Registry Mirrors"
```

然后重新部署项目：
```bash
# 清理之前的构建缓存
docker system prune -f

# 重新构建和部署
docker compose -p knowledge up -d --build
```

## 常见问题解决

### 1. 镜像源不可用
如果某个镜像源不可用，Docker会自动尝试下一个镜像源。

### 2. DNS解析问题
添加可靠的DNS服务器：
```bash
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
echo "nameserver 114.114.114.114" | sudo tee -a /etc/resolv.conf
```

### 3. 防火墙问题
确保Docker相关端口没有被防火墙阻止：
```bash
sudo ufw allow 2375
sudo ufw allow 2376
```

### 4. 权限问题
确保当前用户在docker组中：
```bash
sudo usermod -aG docker $USER
newgrp docker
```
