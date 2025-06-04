# 基于大模型的工业知识库系统

基于 Vue + Flask + MySQL 开发的工业知识库管理系统，提供多种类型文件管理、用户管理、角色权限管理及操作日志记录等功能。

## 功能特点

- 用户认证与授权（登录/登出）
- 基于角色的权限控制
- 完整的用户管理（用户组、权限、用户创建查询修改删除）
- 支持多种类型文件的知识库（文档、表格、PDF、图片、视频）
- 文档自动转换（Word转PDF，PDF转Markdown）
- 文件预览、下载、批量上传
- 与RAGFlow知识库集成，支持文档自动同步与语义检索
- 详细的操作日志记录
- 可自定义前后端端口配置

## 技术栈

### 后端
- Flask 2.0.1
- Flask-SQLAlchemy 2.5.1
- Flask-JWT-Extended 4.3.1
- MySQL/SQLite

### 前端
- Vue 3
- Vue Router
- Pinia 状态管理
- Axios
- Element Plus UI

## 运行环境

系统提供多种运行环境配置方式，选择其一即可：

### 1. 使用自动化脚本

#### Windows
```bash
setup_windows.bat
```

#### Linux
```bash
chmod +x setup_linux.sh
./setup_linux.sh
```

### 2. Docker 部署

使用Docker Compose一键部署整个系统：

```bash
docker-compose up -d
```

#### 中国地区部署说明

由于网络原因，在中国地区部署时可能会遇到镜像下载超时问题。本项目已针对中国网络环境进行优化：

**自动配置镜像源（推荐）:**
```bash
# Linux系统
sudo bash setup_docker_mirrors.sh

# Windows系统
setup_docker_mirrors.bat
```

**手动配置Docker镜像源:**
```bash
# Linux系统
sudo cp daemon.json /etc/docker/daemon.json
sudo systemctl daemon-reload
sudo systemctl restart docker
```

然后重新部署：
```bash
docker compose -p knowledge up -d --build
```

详细的中国部署指南请参考：[Docker中国镜像源配置指南](DOCKER_CHINA_MIRRORS.md)

#### 普通部署
详细说明请参考 [Docker环境使用指南](DOCKER_GUIDE.md)。

### 3. 手动配置

详细的手动配置步骤请参考 [环境搭建指南](SETUP_GUIDE.md)。

## 端口配置

系统支持自定义前后端服务端口：

- **后端默认端口**: 5000
- **前端开发服务端口**: 3000
- **Docker部署前端端口**: 80

可以通过环境变量或配置文件自定义这些端口，详细配置方法请参考：
- [端口配置使用指南](PORT_CONFIG_GUIDE.md)
- [Docker环境端口配置](DOCKER_GUIDE.md#端口配置)
- [开发环境端口配置](SETUP_GUIDE.md#端口配置)

## 默认账户

系统初始化后会创建一个默认的管理员账户：

- 用户名：admin
- 密码：admin123

## 角色与权限

系统支持灵活的角色和权限管理：

1. **超级管理员**：拥有所有权限，可以管理其他用户、角色和权限
2. **自定义角色**：可以根据业务需求自定义不同角色并分配特定权限
3. **权限控制**：文件上传、下载、预览、删除等操作都受权限控制

## 支持的文件类型

- **文档**：doc, docx (自动转换为PDF和Markdown，同步到RAGFlow知识库)
- **表格**：xls, xlsx
- **PDF**：pdf (自动转换为Markdown，同步到RAGFlow知识库)
- **图片**：jpg, jpeg, png, gif
- **视频**：mp4, avi, mkv

## 系统架构

```
industrial-knowledge-system/
├── backend/                # 后端Flask应用
│   ├── models/             # 数据模型
│   ├── routes/             # API路由
│   ├── utils/              # 工具函数
│   └── uploads/            # 文件上传目录
├── frontend/               # 前端Vue应用
│   ├── src/
│   │   ├── api/            # API接口
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   └── store/          # 状态管理
│   └── public/             # 静态资源
├── SETUP_GUIDE.md          # 环境搭建指南
├── DOCKER_GUIDE.md         # Docker部署指南
├── setup_windows.bat       # Windows环境配置脚本
├── setup_linux.sh          # Linux环境配置脚本
└── docker-compose.yml      # Docker组合配置
```
- `POST /api/auth/change-password` - 修改密码

### 用户管理

- `GET /api/users/` - 获取用户列表
- `GET /api/users/<id>` - 获取单个用户
- `POST /api/users/` - 创建新用户
- `PUT /api/users/<id>` - 更新用户
- `DELETE /api/users/<id>` - 删除用户
- `GET /api/users/roles` - 获取角色列表