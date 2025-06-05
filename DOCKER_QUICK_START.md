# Docker 快速使用指南

## 🚀 5分钟快速上手

### 第一步：获取代码
```bash
git clone <项目地址>
cd industrial-knowledge-system
```

### 第二步：一键部署
```bash
# Linux/macOS
chmod +x deploy_china.sh && ./deploy_china.sh

# Windows
deploy_china.bat
```

### 第三步：开始使用
- 打开浏览器访问：http://localhost:3000
- 默认管理员账号（首次运行会自动创建）

## 📋 常用命令速查

### 服务管理
```bash
# 启动服务
docker-compose up -d

# 停止服务  
docker-compose stop

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps
```

### 日志查看
```bash
# 查看所有日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend
```

### 数据管理
```bash
# 备份数据库
cp backend/industrial_knowledge.db backup/

# 备份上传文件
tar -czf uploads_backup.tar.gz backend/uploads/

# 清理数据（慎用）
docker-compose down -v
```

### 开发调试
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 查看后端日志
docker-compose logs backend | tail -50
```

## 🔧 常见操作

### 修改端口
编辑 `docker-compose.yml`:
```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 前端改为8080端口
  backend:
    ports:
      - "8000:5000"  # 后端改为8000端口
```

### 更新代码
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 重置环境
```bash
# 完全清理（会删除数据）
docker-compose down -v
docker system prune -a

# 重新部署
./deploy_china.sh
```

## 🩺 健康检查

### 自动检查
```bash
# 使用项目提供的健康检查脚本
chmod +x docker_health_check.sh
./docker_health_check.sh
```

### 手动检查
```bash
# 检查服务状态
curl http://localhost:5000/health
curl http://localhost:3000

# 检查容器资源使用
docker stats
```

## 🛠 故障排除

### 服务无法启动
```bash
# 查看错误日志
docker-compose logs

# 检查端口占用
netstat -tlnp | grep :3000
netstat -tlnp | grep :5000
```

### 构建失败
```bash
# 清理构建缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

### 访问异常
```bash
# 检查防火墙
sudo ufw status

# 检查网络连接
docker-compose exec frontend ping backend
```

## 🔗 相关文档

- [完整部署指南](SETUP_GUIDE.md)
- [Docker故障排除](DOCKER_TROUBLESHOOTING.md)  
- [Docker镜像配置](DOCKER_CHINA_MIRRORS.md)
- [项目README](README.md)

---

💡 **小贴士**: 遇到问题时，90%的情况下重新构建可以解决：`docker-compose up -d --build`
