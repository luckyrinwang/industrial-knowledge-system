#!/bin/bash
# 执行前请添加执行权限: chmod +x docker_fix.sh

# Docker中国网络环境一键修复脚本
# 解决Docker镜像拉取失败问题

echo "=== Docker中国网络环境一键修复脚本 ==="
echo "正在诊断和修复Docker网络问题..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root权限运行此脚本"
    echo "使用方式: sudo bash docker_fix.sh"
    exit 1
fi

# 函数：测试镜像源连通性
test_mirror() {
    local mirror=$1
    echo -n "测试镜像源 $mirror ... "
    if curl -s --connect-timeout 5 "$mirror/v2/" > /dev/null 2>&1; then
        echo "✅ 可用"
        return 0
    else
        echo "❌ 不可用"
        return 1
    fi
}

# 测试各个镜像源
echo "正在测试镜像源连通性..."
mirrors=(
    "https://docker.mirrors.ustc.edu.cn"
    "https://hub-mirror.c.163.com"
    "https://mirror.baidubce.com"
    "https://dockerproxy.com"
)

working_mirrors=()
for mirror in "${mirrors[@]}"; do
    if test_mirror "$mirror"; then
        working_mirrors+=("$mirror")
    fi
done

if [ ${#working_mirrors[@]} -eq 0 ]; then
    echo "❌ 所有镜像源都不可用，请检查网络连接"
    echo "尝试手动拉取镜像..."
    docker pull python:3.9-slim || echo "拉取python镜像失败"
    docker pull node:16-alpine || echo "拉取node镜像失败"
    docker pull nginx:stable-alpine || echo "拉取nginx镜像失败"
    exit 1
fi

echo "✅ 找到 ${#working_mirrors[@]} 个可用镜像源"

# 备份原配置
if [ -f /etc/docker/daemon.json ]; then
    echo "备份原Docker配置..."
    cp /etc/docker/daemon.json "/etc/docker/daemon.json.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 创建docker目录
mkdir -p /etc/docker

# 生成新的配置文件
echo "生成新的Docker配置..."
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
$(printf '    "%s",\n' "${working_mirrors[@]}" | sed '$ s/,$//')
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

# 等待Docker启动
sleep 5

# 验证Docker服务
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker服务启动失败，恢复原配置"
    if [ -f /etc/docker/daemon.json.backup.* ]; then
        cp /etc/docker/daemon.json.backup.* /etc/docker/daemon.json
        systemctl restart docker
    fi
    exit 1
fi

echo "✅ Docker服务启动成功"

# 测试镜像拉取
echo "测试镜像拉取..."
if docker pull hello-world > /dev/null 2>&1; then
    echo "✅ 镜像拉取测试成功"
    docker rmi hello-world > /dev/null 2>&1
else
    echo "⚠️ 镜像拉取测试失败，但Docker配置已更新"
fi

# 显示当前配置
echo ""
echo "=== 当前Docker镜像源配置 ==="
docker info | grep -A 10 "Registry Mirrors" || echo "镜像源配置已生效"

echo ""
echo "=== 修复完成 ==="
echo "现在可以运行以下命令部署项目："
echo "cd /path/to/industrial-knowledge-system"
echo "docker compose -p knowledge up -d --build"
echo ""
echo "如果仍然遇到问题，请尝试："
echo "1. 检查防火墙设置"
echo "2. 使用代理网络"
echo "3. 手动拉取镜像"
