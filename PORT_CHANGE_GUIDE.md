# 修改前端端口指南

如果您的服务器上80端口已被占用，请按照以下步骤将前端端口修改为3000：

## 1. 修改环境配置

创建或编辑项目根目录中的`.env`文件：

```bash
# 在项目根目录执行
echo "FRONTEND_PORT=3000" > .env
echo "BACKEND_PORT=5000" >> .env
```

## 2. 重新启动容器

```bash
# 停止并重新启动容器，应用新的端口配置
docker-compose down
docker-compose up -d
```

## 3. 验证服务是否正常运行

```bash
# 检查容器状态
docker-compose ps

# 检查前端容器日志
docker-compose logs frontend
```

## 4. 访问系统

现在您可以通过以下地址访问系统：
- 前端界面: http://your-server-ip:3000
- 后端API: http://your-server-ip:5000/api

## 故障排除

如果仍然遇到问题，可以尝试以下方法：

1. 检查3000端口是否可用：
   ```bash
   netstat -tuln | grep 3000
   ```

2. 确认防火墙是否允许3000端口：
   ```bash
   # 对于使用UFW的系统
   sudo ufw allow 3000/tcp
   
   # 对于使用iptables的系统
   sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT
   ```

3. 如果需要使用其他端口，可以在`.env`文件中修改：
   ```
   FRONTEND_PORT=其他端口号
   ```
   然后重新启动容器。
