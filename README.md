# 基于大模型的工业知识库系统

一个现代化的工业知识管理平台，结合人工智能技术提供智能文档处理、知识检索和管理功能。

## 🚀 功能特色

- **智能文档处理**: 支持多种格式文档上传与自动转换
- **知识检索**: 基于大模型的智能问答系统
- **用户管理**: 完整的用户认证和权限控制
- **操作日志**: 详细的系统操作记录
- **文件管理**: 支持批量上传、下载、删除等操作
- **RAGFlow集成**: 支持文档自动同步与语义检索

## 🛠 技术栈

### 后端
- **Python 3.9+**
- **Flask 2.0.1** - Web框架
- **SQLAlchemy 2.5.1** - ORM数据库操作
- **Flask-JWT-Extended** - 用户认证
- **SQLite/MySQL** - 数据库支持

### 前端
- **Vue.js 3** - 前端框架
- **Element Plus** - UI组件库
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Axios** - HTTP客户端

## 📦 快速开始

### 方式一：Docker 部署（推荐）

**🚀 一键部署（最简单）**
```bash
# 克隆项目
git clone <项目地址>
cd industrial-knowledge-system

# Linux/macOS 一键部署
chmod +x deploy_china.sh && ./deploy_china.sh

# Windows 一键部署
deploy_china.bat
```

**📋 标准Docker部署**
```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 初始化数据库（首次部署）
docker-compose exec backend python init_db.py
```

**📖 详细指南**
- [Docker快速上手](DOCKER_QUICK_START.md) - 5分钟快速上手
- [完整部署指南](SETUP_GUIDE.md) - 详细配置说明
- [故障排除](DOCKER_TROUBLESHOOTING.md) - 常见问题解决

访问地址：
- 前端: http://localhost:3000
- 后端API: http://localhost:5000

### 方式二：一键脚本部署

#### Windows 环境
```bash
setup_windows.bat
```

#### Linux 环境
```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

### 方式三：手动部署

详细的手动配置步骤请参考 [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 🌍 中国大陆部署优化

本项目已针对中国大陆网络环境进行全面优化，确保快速、稳定的部署体验：

### 🎯 一键优化脚本
```bash
# 中国大陆优化一键部署
./deploy_china.sh        # Linux/macOS
deploy_china.bat         # Windows
```

### 🚀 优化内容
- **Docker 镜像加速**: 预配置多个可靠的国内镜像源
- **Python 依赖**: 使用阿里云、清华大学等国内镜像源
- **Node.js 依赖**: 使用淘宝 NPM 镜像
- **系统包管理**: APT/YUM 使用国内镜像源
- **中文字体**: 预装完整中文字体，解决PDF乱码问题

### 📋 手动配置（可选）
```bash
# Docker 镜像加速
./setup_docker_mirrors.sh     # Linux
setup_docker_mirrors.bat      # Windows

# Linux 字体和环境配置
./setup_linux.sh
```

### 📚 相关文档
- [Docker中国镜像配置](DOCKER_CHINA_MIRRORS.md) - 镜像源详细配置
- [Docker故障排除](DOCKER_TROUBLESHOOTING.md) - 网络问题解决方案

## 📋 环境要求

- **Python**: 3.9+
- **Node.js**: 14+
- **Docker**: 20.10+ (可选)
- **Docker Compose**: 1.29+ (可选)

## 🔧 配置说明

### 后端配置 (`backend/config.env`)
```env
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URI=sqlite:///industrial_knowledge.db
PORT=5000
```

### 前端配置 (`frontend/.env`)
```env
FRONTEND_PORT=3000
BACKEND_PORT=5000
BACKEND_URL=http://localhost:5000
```



## 📚 文档转换支持

系统支持多种文档格式自动转换：

### 支持的文件类型
- **文档**: doc, docx → PDF + Markdown
- **表格**: xls, xlsx
- **PDF**: pdf → Markdown
- **图片**: jpg, jpeg, png, gif
- **视频**: mp4, avi, mkv

### 转换引擎
- **Windows**: Microsoft Word（原生支持）
- **Linux**: LibreOffice + 中文字体支持

## 🔑 角色与权限

系统支持灵活的角色和权限管理：

1. **超级管理员**: 拥有所有权限，可以管理其他用户、角色和权限
2. **自定义角色**: 可根据业务需求自定义不同角色并分配特定权限
3. **权限控制**: 文件上传、下载、预览、删除等操作都受权限控制

## 📖 API 文档

### 认证相关
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/change-password` - 修改密码

### 文件管理
- `GET /api/files` - 获取文件列表
- `POST /api/files/upload` - 文件上传
- `DELETE /api/files/<id>` - 删除文件
- `GET /api/files/download/<id>` - 下载文件

### 用户管理
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `PUT /api/users/<id>` - 更新用户
- `DELETE /api/users/<id>` - 删除用户

### 操作日志
- `GET /api/logs` - 获取操作日志

## 🚀 部署脚本

项目提供了多个便捷的部署脚本：

- `setup_linux.sh` - Linux 环境一键设置
- `setup_windows.bat` - Windows 环境一键设置
- `setup_docker_mirrors.sh` - Linux Docker 镜像配置
- `setup_docker_mirrors.bat` - Windows Docker 镜像配置

## 📁 项目结构

```
industrial-knowledge-system/
├── backend/                    # 后端Flask应用
│   ├── models/                 # 数据模型
│   │   ├── user.py            # 用户模型
│   │   ├── file.py            # 文件模型
│   │   └── log.py             # 日志模型
│   ├── routes/                 # API路由
│   │   ├── auth.py            # 认证路由
│   │   ├── file.py            # 文件路由
│   │   ├── user.py            # 用户路由
│   │   └── log.py             # 日志路由
│   ├── utils/                  # 工具函数
│   │   ├── auth_utils.py      # 认证工具
│   │   └── docx2pdf_utils.py  # 文档转换工具
│   ├── uploads/                # 文件上传目录
│   ├── config.py              # 配置文件
│   ├── app.py                 # Flask应用
│   └── run.py                 # 启动脚本
├── frontend/                   # 前端Vue应用
│   ├── src/
│   │   ├── api/               # API接口
│   │   ├── components/        # Vue组件
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   └── store/             # 状态管理
│   └── public/                # 静态资源
├── SETUP_GUIDE.md             # 环境搭建指南
├── DOCKER_CHINA_MIRRORS.md    # Docker镜像配置指南
├── docker-compose.yml         # Docker组合配置
├── Dockerfile.backend         # 后端Docker配置
├── Dockerfile.frontend        # 前端Docker配置
└── requirements.txt           # Python依赖列表
```

## 🆘 常见问题

### Q: Docker 构建失败怎么办？
A: 请参考 [DOCKER_QUICK_FIX.md](DOCKER_QUICK_FIX.md) 进行故障排除。

### Q: PDF 转换出现中文乱码？
A: Linux 环境请运行 `setup_linux.sh` 自动安装中文字体。

### Q: 前端页面无法访问后端？
A: 检查后端服务是否启动，端口配置是否正确。

### Q: 文件上传失败？
A: 检查上传目录权限，确保应用有写入权限。

### Q: 数据库连接失败？
A: 检查数据库配置，确保数据库服务正常运行。

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 📞 支持与反馈

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](../../issues)
- 发起 [Pull Request](../../pulls)
- 联系开发团队

---

**⚠️ 重要提醒**: 
- 生产环境部署前请修改默认密钥和数据库配置
- 定期备份重要数据
- 及时更新系统补丁和依赖包