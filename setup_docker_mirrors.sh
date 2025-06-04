#!/bin/bash
# 执行前请添加执行权限: chmod +x setup_docker_mirrors.sh

# Docker中国镜像源快速配置脚本
# 适用于Linux系统

echo "=== Docker中国镜像源配置脚本 ==="
echo "正在配置Docker使用中国镜像源..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行此脚本"
    echo "使用方式: sudo bash setup_docker_mirrors.sh"
    exit 1
fi

# 备份原配置文件（如果存在）
if [ -f /etc/docker/daemon.json ]; then
    echo "备份原配置文件..."
    cp /etc/docker/daemon.json /etc/docker/daemon.json.backup.$(date +%Y%m%d_%H%M%S)
fi

# 创建docker目录
mkdir -p /etc/docker

# 写入镜像源配置
echo "写入Docker镜像源配置..."
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com",
    "https://dockerproxy.com"
  ],
  "insecure-registries": [],
  "debug": false,
  "experimental": false,
  "features": {
    "buildkit": true
  },
  "dns": ["8.8.8.8", "114.114.114.114"],
  "max-concurrent-downloads": 3,
  "max-concurrent-uploads": 5
}
EOF

# 重启Docker服务
echo "重启Docker服务..."
systemctl daemon-reload
systemctl restart docker

# 验证配置
echo "验证Docker配置..."
sleep 3
if docker info > /dev/null 2>&1; then
    echo "✅ Docker服务启动成功"
    echo "已配置的镜像源："
    docker info | grep -A 10 "Registry Mirrors" || echo "镜像源配置成功，但显示可能需要重启Docker"
else
    echo "❌ Docker服务启动失败，请检查配置"
    exit 1
fi

echo ""
echo "=== 配置完成 ==="
echo "现在可以运行以下命令部署项目："
echo "docker compose -p knowledge up -d --build"
echo ""
echo "如果仍然遇到问题，请检查："
echo "1. 网络连接是否正常"
echo "2. 防火墙设置"
echo "3. 尝试重启Docker服务: sudo systemctl restart docker"
