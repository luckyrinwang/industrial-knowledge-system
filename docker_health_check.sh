#!/bin/bash

# Docker 服务健康检查脚本
# Industrial Knowledge System Health Check

echo "🩺 工业知识库系统健康检查"
echo "================================"

# 检查Docker是否运行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker 服务未运行"
    exit 1
fi

echo "✅ Docker 服务正常"

# 检查容器状态
echo ""
echo "📋 容器状态："
docker-compose ps

# 检查服务健康状态
echo ""
echo "🔍 服务健康检查："

# 检查后端服务
echo -n "后端服务 (port 5000): "
if curl -f -s http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ 正常"
else
    echo "❌ 异常"
    echo "   检查命令: docker-compose logs backend"
fi

# 检查前端服务
echo -n "前端服务 (port 3000): "
if curl -f -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ 正常"
else
    echo "❌ 异常"
    echo "   检查命令: docker-compose logs frontend"
fi

# 检查数据库
echo -n "数据库连接: "
if docker-compose exec -T backend python -c "
import sys
sys.path.append('/app')
try:
    from backend.config import Config
    from sqlalchemy import create_engine
    engine = create_engine(Config.DATABASE_URI)
    connection = engine.connect()
    connection.close()
    print('OK')
except Exception as e:
    print('ERROR')
    sys.exit(1)
" 2>/dev/null | grep -q "OK"; then
    echo "✅ 正常"
else
    echo "❌ 异常"
    echo "   可能需要初始化: docker-compose exec backend python init_db.py"
fi

# 检查磁盘空间
echo -n "磁盘空间: "
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠️  磁盘空间不足 (${DISK_USAGE}%)"
else
    echo "✅ 充足 (${DISK_USAGE}% 已使用)"
fi

# 检查内存使用
echo -n "内存使用: "
if command -v free >/dev/null; then
    MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    if [ $MEM_USAGE -gt 90 ]; then
        echo "⚠️  内存使用率过高 (${MEM_USAGE}%)"
    else
        echo "✅ 正常 (${MEM_USAGE}% 已使用)"
    fi
else
    echo "✅ 无法检测"
fi

echo ""
echo "📊 资源使用统计："
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""
echo "🔗 访问地址："
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:5000"

echo ""
echo "💡 常用管理命令："
echo "   查看日志: docker-compose logs -f"
echo "   重启服务: docker-compose restart"
echo "   停止服务: docker-compose stop"
echo "   清理环境: docker-compose down"
