# 端口配置使用指南

本文档介绍如何在不同环境下配置"基于大模型的工业知识库系统"的前后端端口。

## 开发环境配置

### 后端端口配置

1. **通过环境变量配置文件**
   
   在`backend/config.env`文件中设置端口：
   ```
   PORT=5000  # 更改为你希望使用的端口
   ```

2. **直接在代码中修改**
   
   如果你不想使用环境变量，可以直接在`backend/run.py`中修改默认端口：
   ```python
   app.run(debug=True, host='0.0.0.0', port=5000)  # 更改这里的5000
   ```

### 前端端口配置

1. **通过环境变量配置**
   
   创建或编辑`frontend/.env`文件：
   ```
   FRONTEND_PORT=3000  # 前端服务端口
   BACKEND_PORT=5000   # 后端服务端口
   BACKEND_URL=http://localhost:5000  # 后端服务地址
   ```

2. **直接修改Vite配置**
   
   可以直接在`frontend/vite.config.js`中修改端口配置。

## Docker环境配置

为Docker环境配置端口，你有两种方法：

### 1. 使用`.env`文件（推荐）

在项目根目录创建`.env`文件：
```
FRONTEND_PORT=80
BACKEND_PORT=5000
```

然后正常启动Docker：
```bash
docker-compose up -d
```

### 2. 通过命令行设置环境变量

```bash
FRONTEND_PORT=8080 BACKEND_PORT=5001 docker-compose up -d
```

### 3. 直接编辑docker-compose.yml

修改`docker-compose.yml`中的端口映射：
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

## 生产环境部署

对于生产环境，建议使用以下设置：

1. **使用标准的HTTP/HTTPS端口**
   - 前端: 80 (HTTP) 或 443 (HTTPS)
   - 后端: 使用一个非标准端口，如5000、8000或8080

2. **配置HTTPS**
   - 在生产环境中，强烈建议配置HTTPS
   - 可以使用Nginx作为前端的反向代理，并配置SSL证书

## 注意事项

1. 确保防火墙允许所选端口的访问
2. 如果使用云服务，需要在云控制台配置安全组或网络ACL
3. 不要使用已被其他服务占用的端口
4. 避免使用低于1024的端口（除非有root权限）

## 端口配置测试

系统提供了端口配置测试脚本，用于验证当前的端口配置和占用情况：

### Linux环境

```bash
chmod +x test_port_config.sh
./test_port_config.sh
```

### Windows环境

```batch
test_port_config.bat
```

测试脚本会检查：
1. 各配置文件中设置的端口
2. 系统中是否有程序占用这些端口
3. 输出配置状态摘要

建议在启动系统前先运行此测试脚本，确保端口没有冲突。
