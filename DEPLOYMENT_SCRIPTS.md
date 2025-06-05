# 部署脚本使用说明

## 📋 可用脚本

### 一键部署脚本
- `deploy_china.sh` - Linux/macOS 一键部署（针对中国大陆优化）
- `deploy_china.bat` - Windows 一键部署（针对中国大陆优化）

### 环境配置脚本
- `setup_docker_mirrors.sh` - Linux Docker镜像加速配置
- `setup_docker_mirrors.bat` - Windows Docker镜像加速配置
- `setup_linux.sh` - Linux环境自动配置（LibreOffice、字体、locale）
- `setup_windows.bat` - Windows环境配置（原有脚本）

### 运维管理脚本
- `docker_health_check.sh` - Docker服务健康检查

## 🚀 推荐使用方式

### 首次部署
```bash
# 新用户推荐：一键部署
./deploy_china.sh       # Linux/macOS
deploy_china.bat        # Windows
```

### 环境配置
```bash
# 仅配置Docker镜像加速
./setup_docker_mirrors.sh

# 仅配置Linux环境（字体、LibreOffice等）
./setup_linux.sh
```

### 日常运维
```bash
# 健康检查
./docker_health_check.sh

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 📝 脚本功能说明

### deploy_china.sh / deploy_china.bat
**功能**：全自动化部署工业知识库系统
**适用场景**：新环境首次部署、快速体验

**包含功能**：
- Docker环境检查
- 镜像加速配置（Linux）
- 端口占用检查  
- 目录结构创建
- 配置文件准备
- 镜像构建和服务启动
- 数据库初始化
- 健康状态检查

### setup_docker_mirrors.sh / setup_docker_mirrors.bat
**功能**：配置Docker国内镜像加速
**适用场景**：Docker下载速度慢、无法访问官方镜像仓库

**镜像源列表**：
- DaoCloud (docker.m.daocloud.io)
- Docker Proxy (dockerproxy.com)
- 百度云 (mirror.baidubce.com)
- 七牛云 (reg-mirror.qiniu.com)

### setup_linux.sh
**功能**：Linux环境自动化配置
**适用场景**：解决PDF中文乱码、LibreOffice环境配置

**包含功能**：
- LibreOffice自动安装
- 中文字体包安装
- 系统locale配置
- 字体缓存更新

### docker_health_check.sh
**功能**：Docker服务健康检查
**适用场景**：定期检查、故障诊断

**检查项目**：
- Docker服务状态
- 容器运行状态
- 服务端口连通性
- 数据库连接状态
- 系统资源使用

## ⚙️ 脚本参数

大部分脚本支持无参数运行，会使用默认配置。

### 高级用法示例
```bash
# 指定不同的端口
export FRONTEND_PORT=8080
export BACKEND_PORT=8000
./deploy_china.sh

# 跳过端口检查
export SKIP_PORT_CHECK=1
./deploy_china.sh

# 仅构建不启动
export BUILD_ONLY=1
./deploy_china.sh
```

## 🐛 故障排除

### 脚本执行权限问题
```bash
# Linux/macOS
chmod +x deploy_china.sh
chmod +x setup_docker_mirrors.sh
chmod +x setup_linux.sh
chmod +x docker_health_check.sh

# Windows（以管理员身份运行PowerShell）
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 常见错误

**"Docker not found"**
```bash
# 检查Docker是否安装
docker --version
docker-compose --version
```

**"Permission denied"**
```bash
# 将用户添加到docker组
sudo usermod -aG docker $USER
newgrp docker
```

**"Port already in use"**
```bash
# 查看端口占用
sudo lsof -ti:3000 | xargs sudo kill -9
sudo lsof -ti:5000 | xargs sudo kill -9
```

## 📞 获取帮助

如果脚本执行遇到问题：

1. 检查脚本执行权限
2. 查看详细错误输出
3. 参考 [Docker故障排除指南](DOCKER_TROUBLESHOOTING.md)
4. 提交 [GitHub Issue](issues)

---

💡 **提示**: 建议首次使用时使用一键部署脚本，后续根据需要使用具体的功能脚本。
