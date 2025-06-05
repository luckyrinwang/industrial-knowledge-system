# 环境搭建指南

本文档提供了详细的手动搭建步骤，用于"基于大模型的工业知识库系统"的开发和部署。

## 📋 系统要求

### 基础环境
- **Python**: 3.9 或更高版本
- **Node.js**: 14 或更高版本
- **数据库**: SQLite（默认）或 MySQL 5.7+
- **操作系统**: Windows 10+、Ubuntu 18.04+、CentOS 7+ 或 macOS 10.15+

### 可选依赖
- **Docker**: 20.10+ （用于容器化部署）
- **LibreOffice**: 6.0+（Linux环境下文档转换）
- **Microsoft Word**: 2016+（Windows环境下文档转换）

## 🚀 快速开始

### 1. 获取源码

```bash
git clone <项目地址>
cd industrial-knowledge-system
```

## 🐳 方式一：Docker 部署（推荐）

Docker 部署是最简单快捷的部署方式，适合生产环境和快速体验。整个部署过程只需要几个命令即可完成！

### 🚀 一键快速部署

**如果你只想快速体验系统，可以直接运行：**

```bash
# 克隆项目
git clone <项目地址>
cd industrial-knowledge-system

# Linux/macOS 一键启动
chmod +x deploy_china.sh          # 添加执行权限
./deploy_china.sh

# Windows 一键启动（无需额外设置）
deploy_china.bat
```

✨ **一键部署脚本功能：**
- ✅ 自动检查Docker环境
- ✅ 配置中国大陆镜像加速
- ✅ 检查端口占用情况
- ✅ 创建必要的目录结构
- ✅ 复制配置文件模板
- ✅ 构建和启动所有服务
- ✅ 初始化数据库
- ✅ 运行健康检查

**首次部署预计时间：** 5-15分钟（取决于网络速度）

**访问地址：**
- 🌐 前端应用：http://localhost:3000
- 🔗 后端API：http://localhost:5000

**📖 相关文档：**
- [Docker快速上手指南](DOCKER_QUICK_START.md) - 5分钟快速上手
- [Docker故障排除指南](DOCKER_TROUBLESHOOTING.md) - 问题解决方案
- [Docker镜像配置指南](DOCKER_CHINA_MIRRORS.md) - 镜像源配置
- [部署脚本使用说明](DEPLOYMENT_SCRIPTS.md) - 脚本详细说明

**遇到问题？** 查看上述文档或继续阅读详细部署步骤。

---

### 📝 详细部署步骤

### 1.1 环境准备

确保系统已安装 Docker 和 Docker Compose：

**Windows:**
```bash
# 安装 Docker Desktop
# 下载地址：https://www.docker.com/products/docker-desktop

# 验证安装
docker --version
docker-compose --version
```

**Linux (Ubuntu/Debian):**
```bash
# 安装 Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 验证安装
docker --version
docker-compose --version
```

**Linux (CentOS/RHEL):**
```bash
# 安装 Docker
sudo yum install -y docker docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER
newgrp docker
```

### 1.2 中国大陆镜像加速（推荐）

如果在中国大陆，建议配置 Docker 镜像加速：

**自动配置脚本:**
```bash
# Linux
./setup_docker_mirrors.sh

# Windows
setup_docker_mirrors.bat
```

**手动配置:**
```bash
# 创建 daemon.json 配置文件
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

# 重启 Docker 服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 1.3 Docker 部署步骤

#### 方式一：一键部署（推荐）
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 方式二：分步部署
```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 初始化数据库（首次部署需要）
docker-compose exec backend python init_db.py
```

### 1.4 服务访问

部署完成后，可以通过以下地址访问：

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:5000
- **API文档**: http://localhost:5000/docs（如果启用）

### 1.5 Docker 常用管理命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs backend    # 后端日志
docker-compose logs frontend   # 前端日志
docker-compose logs -f         # 实时日志

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 进入容器调试
docker-compose exec backend bash
docker-compose exec frontend sh

# 健康检查（使用项目提供的脚本）
chmod +x docker_health_check.sh    # Linux/macOS
./docker_health_check.sh

# 手动健康检查
curl http://localhost:5000/health  # 检查后端
curl http://localhost:3000         # 检查前端
```
docker-compose logs backend    # 后端日志
docker-compose logs frontend   # 前端日志
docker-compose logs -f         # 实时日志

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 停止并删除容器
docker-compose down

# 重新构建并启动
docker-compose up -d --build

# 进入容器调试
docker-compose exec backend bash
docker-compose exec frontend sh
```

### 1.6 数据持久化

Docker 部署中的重要数据会通过卷挂载保持持久化：

```yaml
# docker-compose.yml 中的卷配置
volumes:
  - ./backend/uploads:/app/uploads          # 文件上传目录
  - ./backend/industrial_knowledge.db:/app/industrial_knowledge.db  # SQLite数据库
```

**备份数据:**
```bash
# 备份数据库
cp backend/industrial_knowledge.db backup/db_$(date +%Y%m%d).db

# 备份上传文件
tar -czf backup/uploads_$(date +%Y%m%d).tar.gz backend/uploads/
```

### 1.7 自定义配置

#### 修改端口
编辑 `docker-compose.yml` 文件：
```yaml
services:
  frontend:
    ports:
      - "8080:80"    # 修改前端端口为8080
  backend:
    ports:
      - "8000:5000"  # 修改后端端口为8000
```

#### 环境变量配置
创建 `.env` 文件在项目根目录：
```env
# 服务端口
FRONTEND_PORT=3000
BACKEND_PORT=5000

# 数据库配置
DATABASE_URI=sqlite:///industrial_knowledge.db

# 生产环境配置
SECRET_KEY=your_production_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
```

### 1.8 生产环境优化

#### 使用外部数据库
```yaml
# docker-compose.prod.yml
services:
  backend:
    environment:
      - DATABASE_URI=mysql+pymysql://user:password@mysql:3306/industrial_knowledge
  
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: industrial_knowledge
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql
```

#### SSL/HTTPS 配置
```yaml
# 使用 Nginx 反向代理
nginx:
  image: nginx:alpine
  ports:
    - "443:443"
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/ssl/certs
```

### 1.9 故障排除

Docker部署中遇到问题？查看详细的[Docker故障排除指南](DOCKER_TROUBLESHOOTING.md)。

#### 常见问题快速解决

**镜像下载失败：**
```bash
# 配置镜像加速
./setup_docker_mirrors.sh
```

**端口被占用：**
```bash
# 检查占用进程
sudo lsof -ti:3000 | xargs sudo kill -9
sudo lsof -ti:5000 | xargs sudo kill -9
```

**权限不足：**
```bash
# 添加用户到docker组
sudo usermod -aG docker $USER
newgrp docker
```

**容器启动失败：**
```bash
# 查看详细错误信息
docker-compose logs backend
docker-compose logs frontend

# 进入容器调试
docker-compose exec backend bash
```

**数据库连接失败：**
```bash
# 进入后端容器检查
docker-compose exec backend python -c "
from backend.config import Config
print('Database URI:', Config.DATABASE_URI)
"
```

📚 **更多问题和解决方案请查看完整的 [Docker故障排除指南](DOCKER_TROUBLESHOOTING.md)**

## 🛠 方式二：手动环境搭建

如果需要自定义开发环境或不使用Docker，可以按照以下步骤手动搭建：

#### 2.1 创建Python虚拟环境

**Windows:**
```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 验证激活状态
where python
```

**Linux/macOS:**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证激活状态
which python
```

#### 2.2 安装Python依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt
```

#### 2.3 配置后端环境变量

复制配置模板并编辑：
```bash
cp backend/config.env.example backend/config.env
```

编辑 `backend/config.env` 文件：
```env
# 密钥配置（生产环境必须修改）
SECRET_KEY=your_production_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# 数据库配置
DATABASE_URI=sqlite:///industrial_knowledge.db
# 或使用MySQL：
# DATABASE_URI=mysql+pymysql://username:password@localhost/industrial_knowledge

# 服务配置
PORT=5000
DEBUG=False

# 文件上传配置
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# RAGFlow集成配置（可选）
RAGFLOW_API_URL=http://localhost:9380
RAGFLOW_API_KEY=your_ragflow_api_key
```

#### 2.4 初始化数据库

```bash
cd backend
python init_db.py
cd ..
```

### 3. 前端环境搭建

#### 3.1 安装Node.js依赖

```bash
cd frontend
npm install
```

如果下载速度慢，可以使用国内镜像：
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

#### 3.2 配置前端环境变量

创建前端环境配置文件：
```bash
# 开发环境配置
cat > .env.development << EOF
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_TITLE=工业知识库系统
EOF

# 生产环境配置
cat > .env.production << EOF
VITE_API_BASE_URL=http://your-domain.com
VITE_APP_TITLE=工业知识库系统
EOF
```

### 4. 文档转换环境配置

#### 4.1 Windows环境（推荐使用Word）

确保系统已安装Microsoft Word：
```cmd
# 验证Word是否可用
powershell -Command "New-Object -ComObject Word.Application | Select-Object Version"
```

#### 4.2 Linux环境（使用LibreOffice）

**Ubuntu/Debian:**
```bash
# 安装LibreOffice和中文字体
sudo apt update
sudo apt install -y libreoffice \
    fonts-noto-cjk \
    fonts-arphic-ukai \
    fonts-arphic-uming \
    fonts-wqy-zenhei \
    fonts-wqy-microhei

# 更新字体缓存
sudo fc-cache -f -v
```

**CentOS/RHEL:**
```bash
# 安装LibreOffice和中文字体
sudo yum install -y libreoffice \
    google-noto-cjk-fonts \
    wqy-microhei-fonts \
    wqy-zenhei-fonts

# 更新字体缓存
sudo fc-cache -f -v
```

### 5. 启动服务

#### 5.1 启动后端服务

```bash
# 激活虚拟环境（如果尚未激活）
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 启动后端
cd backend
python run.py
```

后端服务将在 http://localhost:5000 启动

#### 5.2 启动前端服务

打开新的终端窗口：
```bash
cd frontend

# 开发环境启动
npm run dev

# 或构建生产版本
npm run build
npm run preview
```

前端服务将在 http://localhost:3000 启动

## 🔧 高级配置

### 数据库配置

#### SQLite（默认）
无需额外配置，数据库文件会自动创建在 `backend/` 目录下。

#### MySQL配置
1. 创建数据库：
```sql
CREATE DATABASE industrial_knowledge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON industrial_knowledge.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

2. 更新配置文件中的数据库连接字符串。

### 端口配置

#### 自定义后端端口
编辑 `backend/config.env`：
```env
PORT=8080
```

#### 自定义前端端口
编辑 `frontend/vite.config.js`：
```javascript
export default defineConfig({
  server: {
    port: 8081,
    host: '0.0.0.0'
  }
})
```

### SSL/HTTPS配置

#### 开发环境HTTPS
```bash
# 前端启用HTTPS
cd frontend
npm run dev -- --https

# 后端SSL配置需要在config.env中添加证书路径
```

#### 生产环境推荐使用Nginx反向代理

## 🐛 故障排除

### 常见问题及解决方案

#### 1. Python依赖安装失败
```bash
# 升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 如果某个包安装失败，可以尝试
pip install package_name --no-cache-dir
```

#### 2. Node.js依赖安装失败
```bash
# 清除npm缓存
npm cache clean --force

# 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install
```

#### 3. 数据库连接失败
- 检查数据库服务是否运行
- 验证连接字符串格式
- 确认用户权限和密码

#### 4. 文档转换失败
**Windows:**
- 确认Word已正确安装
- 检查COM权限设置

**Linux:**
- 确认LibreOffice已安装：`libreoffice --version`
- 检查中文字体：`fc-list | grep -i chinese`

#### 5. 前端无法访问后端
- 检查后端服务是否启动
- 验证CORS配置
- 确认防火墙设置

### 日志查看

#### 后端日志
```bash
# 查看Flask日志
tail -f backend/logs/app.log
```

#### 前端构建日志
```bash
# 查看Vite构建日志
cd frontend
npm run build -- --debug
```

## 🔒 安全配置

### 生产环境安全检查清单

- [ ] 修改默认管理员密码
- [ ] 更新所有密钥（SECRET_KEY, JWT_SECRET_KEY）
- [ ] 配置HTTPS
- [ ] 设置防火墙规则
- [ ] 配置文件权限限制
- [ ] 定期备份数据库
- [ ] 启用操作日志审计

### 文件权限设置

```bash
# 设置适当的文件权限
chmod 755 backend/
chmod 755 frontend/
chmod 777 backend/uploads/
chmod 600 backend/config.env
```

## 📦 生产部署建议

### 1. 使用Gunicorn部署后端
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### 2. 使用Nginx部署前端
```bash
# 构建生产版本
cd frontend
npm run build

# 配置Nginx指向dist目录
```

### 3. 使用Supervisor管理进程
```ini
[program:industrial-knowledge-backend]
command=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 backend.app:app
directory=/path/to/industrial-knowledge-system
user=www-data
autostart=true
autorestart=true
```

## 📞 获取帮助

如果在环境搭建过程中遇到问题：

1. 查看本文档的故障排除部分
2. 检查项目的 [常见问题文档](FAQ.md)
3. 在GitHub提交 [Issue](../../issues)
4. 联系开发团队

---

**提示**: 建议在生产环境部署前先在测试环境完整验证所有功能。

---

## 📚 附录

### A. 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vue 3 前端    │────│   Flask 后端    │────│   SQLite/MySQL  │
│                 │    │                 │    │      数据库     │
│  - 文件管理     │    │  - API接口      │    │                 │
│  - 知识检索     │    │  - 文件转换     │    │  - 用户数据     │
│  - 用户管理     │    │  - 用户认证     │    │  - 文件元数据   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│   文件存储系统   │──────────────┘
                        │                 │
                        │  - 文档文件     │
                        │  - 图片文件     │
                        │  - 转换缓存     │
                        └─────────────────┘
```

### B. 开发规范

#### 代码提交规范
```bash
# 提交信息格式
feat: 新增功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建或辅助工具的变动
```

#### 分支管理规范
```bash
main        # 主分支（生产环境）
develop     # 开发分支
feature/*   # 功能分支
hotfix/*    # 热修复分支
release/*   # 发布分支
```

### C. 性能优化建议

#### 前端优化
- 启用路由懒加载
- 组件按需加载
- 图片压缩和懒加载
- 开启Gzip压缩

#### 后端优化
- 数据库连接池配置
- 接口响应缓存
- 文件上传分片处理
- 异步任务队列

#### 部署优化
- 使用CDN加速静态资源
- 配置Redis缓存
- 数据库读写分离
- 负载均衡配置

---

**📞 获取支持**
- 📖 查看 [README.md](README.md) 了解项目概述
- 🐛 报告问题: [GitHub Issues](issues)
- 💬 技术讨论: [Discussions](discussions)
- 📧 联系邮箱: support@example.com

---

⚡ **快速提示**: 推荐使用 Docker 部署方式，可以避免大部分环境配置问题！
