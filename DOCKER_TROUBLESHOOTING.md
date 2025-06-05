# Docker 部署常见问题解决指南

## 🚨 常见问题 & 快速解决方案

### 1. 镜像下载速度慢或失败

**问题表现：**
```bash
Error response from daemon: Get https://registry-1.docker.io/v2/: dial tcp: lookup registry-1.docker.io
```

**解决方案：**
```bash
# 方案一：使用项目提供的脚本
./setup_docker_mirrors.sh        # Linux
setup_docker_mirrors.bat         # Windows

# 方案二：手动配置镜像加速
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com", 
    "https://mirror.baidubce.com"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 2. 构建时依赖安装失败

**问题表现：**
```bash
E: Unable to locate package
Could not install packages due to an EnvironmentError
```

**解决方案：**
```bash
# 清理Docker构建缓存
docker system prune -a --volumes

# 重新构建，使用国内镜像源
DOCKER_BUILDKIT=1 docker-compose build --no-cache
```

### 3. 端口被占用

**问题表现：**
```bash
Error starting userland proxy: listen tcp 0.0.0.0:3000: bind: address already in use
```

**解决方案：**
```bash
# 方案一：停止占用端口的服务
sudo lsof -ti:3000 | xargs sudo kill -9

# 方案二：修改docker-compose.yml中的端口映射
services:
  frontend:
    ports:
      - "8080:80"  # 改为8080端口
```

### 4. 权限不足错误

**问题表现：**
```bash
permission denied while trying to connect to the Docker daemon socket
```

**解决方案：**
```bash
# 将当前用户添加到docker组
sudo usermod -aG docker $USER
newgrp docker

# 或使用sudo运行
sudo docker-compose up -d
```

### 5. 容器启动失败

**问题表现：**
```bash
Exited (1) X seconds ago
```

**解决方案：**
```bash
# 查看详细错误日志
docker-compose logs backend
docker-compose logs frontend

# 进入容器调试
docker-compose exec backend bash
```

### 6. 数据库初始化失败

**问题表现：**
```bash
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) unable to open database file
```

**解决方案：**
```bash
# 确保目录权限正确
sudo chown -R $USER:$USER backend/
chmod 755 backend/

# 手动初始化数据库
docker-compose exec backend python init_db.py
```

### 7. 前端无法访问后端API

**问题表现：**
- 前端页面空白或接口调用失败
- Network Error in browser console

**解决方案：**
```bash
# 检查后端服务是否正常运行
curl http://localhost:5000/health

# 检查网络连接
docker network ls
docker-compose exec frontend ping backend

# 检查前端环境变量配置
docker-compose exec frontend env | grep API
```

### 8. 中文字体显示异常

**问题表现：**
- PDF中中文显示为方块或乱码

**解决方案：**
已在Dockerfile中预装中文字体，如果仍有问题：
```bash
# 重新构建后端镜像
docker-compose build backend --no-cache

# 进入容器检查字体
docker-compose exec backend fc-list | grep -i chinese
```

## 🔧 调试技巧

### 查看实时日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 进入容器调试
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 以root用户进入
docker-compose exec --user root backend bash
```

### 检查容器资源使用
```bash
# 查看容器状态
docker-compose ps

# 查看资源使用情况
docker stats

# 查看容器详细信息
docker inspect <container_name>
```

### 网络调试
```bash
# 查看Docker网络
docker network ls

# 检查容器网络连接
docker-compose exec backend ping frontend
docker-compose exec frontend ping backend
```

## 🛡️ 生产环境注意事项

### 1. 安全配置
```bash
# 修改默认密钥
vim backend/config.env
SECRET_KEY=your_production_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

### 2. 数据备份
```bash
# 备份SQLite数据库
cp backend/industrial_knowledge.db backup/

# 备份上传文件
tar -czf backup/uploads.tar.gz backend/uploads/
```

### 3. 使用外部数据库
```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - DATABASE_URI=mysql+pymysql://user:pass@mysql:3306/db
```

### 4. SSL/HTTPS配置
```bash
# 使用Let's Encrypt证书
certbot certonly --webroot -w /var/www/html -d yourdomain.com

# 配置Nginx反向代理
vim nginx.conf
```

## 📞 获取更多帮助

如果问题仍未解决：

1. 查看[完整部署指南](SETUP_GUIDE.md)
2. 查看[项目README](README.md)
3. 提交[GitHub Issue](../../issues)
4. 查看Docker官方文档：https://docs.docker.com/

---

💡 **提示**: 大部分问题都与网络连接和权限相关，确保Docker服务正常运行且用户具有足够权限。
