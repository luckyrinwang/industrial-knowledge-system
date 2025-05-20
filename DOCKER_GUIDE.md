# Docker环境使用指南

本文档提供了如何使用Docker快速部署"基于大模型的工业知识库系统"的指南。

## 前提条件

- 安装Docker和Docker Compose
- 对于Windows: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- 对于Linux: Docker Engine和Docker Compose

## 快速开始

1. 克隆代码库：
```bash
git clone https://github.com/yourusername/industrial-knowledge-system.git
cd industrial-knowledge-system
```

2. 使用Docker Compose启动系统：
```bash
docker-compose up -d
```

3. 访问系统：
   - 前端界面: http://localhost
   - 后端API: http://localhost/api

## 自定义配置

### 端口配置

1. **使用.env文件配置端口**（推荐方式）

   在项目根目录创建`.env`文件：
   ```
   FRONTEND_PORT=80    # 前端服务端口
   BACKEND_PORT=5000   # 后端服务端口
   ```
   
   然后正常启动Docker：
   ```bash
   docker-compose up -d
   ```

2. **通过命令行设置端口**

   ```bash
   FRONTEND_PORT=8080 BACKEND_PORT=5001 docker-compose up -d
   ```

3. **修改docker-compose.yml**

   可以直接在`docker-compose.yml`中修改端口映射：
   ```yaml
   frontend:
     ports:
       - "8080:80"  # 将8080改为你希望的端口
   
   backend:
     ports:
       - "5001:5001"  # 将5001改为你希望的端口
     environment:
       - PORT=5001    # 确保这里也改为同样的端口
   ```

### 修改环境变量

编辑`docker-compose.yml`文件中的环境变量：

```yaml
backend:
  environment:
    - SECRET_KEY=your_custom_secret_key
    - JWT_SECRET_KEY=your_custom_jwt_secret_key
    - DATABASE_URI=mysql+pymysql://industrial_user:your_custom_password@db/industrial_knowledge
```

### 修改数据库配置

```yaml
db:
  environment:
    MYSQL_ROOT_PASSWORD: your_root_password
    MYSQL_DATABASE: industrial_knowledge
    MYSQL_USER: industrial_user
    MYSQL_PASSWORD: your_custom_password
```

### 暴露不同端口

如果80端口被占用，可以修改端口映射：

```yaml
frontend:
  ports:
    - "8080:80"  # 将前端服务映射到8080端口
```

## 数据持久化

系统使用Docker卷来持久化数据：
- `db_data`: 存储MySQL数据库文件
- `uploads_data`: 存储上传的文件

这些卷保证了即使容器被删除，数据也不会丢失。

## 日常管理命令

### 查看容器状态
```bash
docker-compose ps
```

### 查看容器日志
```bash
# 查看所有容器日志
docker-compose logs

# 查看特定服务的日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### 停止系统
```bash
docker-compose down
```

### 重新构建并启动
```bash
docker-compose up -d --build
```

### 备份数据库
```bash
docker exec industrial-knowledge-system_db_1 sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" industrial_knowledge' > backup.sql
```

## 生产环境部署

对于生产环境部署，建议：

1. 修改所有默认密码
2. 配置HTTPS (在nginx.conf中添加SSL配置)
3. 配置定期备份
4. 使用外部数据库服务(可选)

## 故障排除

### 容器无法启动
检查日志：
```bash
docker-compose logs
```

### 无法连接数据库
确保数据库容器正常运行：
```bash
docker-compose ps db
```

### 文件上传问题
检查上传文件夹权限：
```bash
docker exec -it industrial-knowledge-system_backend_1 ls -la /app/uploads
```
