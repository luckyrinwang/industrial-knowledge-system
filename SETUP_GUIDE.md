# 环境搭建指南

本文档提供了如何为"基于大模型的工业知识库系统"搭建运行环境的详细步骤。

## 系统要求

- Python 3.9+
- MySQL 5.7+ 或 MariaDB 10.5+
- Node.js 14+ (前端开发)
- Windows 或 Linux 服务器

## 通用步骤

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/industrial-knowledge-system.git
cd industrial-knowledge-system
```

### 2. 创建虚拟环境

#### Windows

```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

#### Linux/MacOS

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 3. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

## 特定平台配置

### Windows 平台

Windows平台使用Word COM对象进行文档转换，需要确保：

1. 系统已安装Microsoft Office（Word）
2. 已通过pip安装pywin32库 (包含在requirements.txt中)

### Linux 平台

Linux平台使用LibreOffice和unoconv进行文档转换：

1. 安装LibreOffice
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install libreoffice

   # CentOS/RHEL
   sudo yum install libreoffice
   ```

2. 安装unoconv
   ```bash
   # Ubuntu/Debian
   sudo apt install unoconv

   # CentOS/RHEL
   sudo yum install unoconv
   ```

## 数据库配置

1. 创建MySQL数据库
   ```sql
   CREATE DATABASE industrial_knowledge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'industrial_user'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON industrial_knowledge.* TO 'industrial_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. 配置环境变量
   在项目根目录下创建`backend/config.env`文件，并填入以下内容：
   
   ```
   SECRET_KEY=your_secure_secret_key
   JWT_SECRET_KEY=your_secure_jwt_secret_key
   DATABASE_URI=mysql+pymysql://industrial_user:your_secure_password@localhost/industrial_knowledge
   ```

3. 初始化数据库
   ```bash
   cd backend
   python init_db.py
   ```

## 端口配置

系统支持自定义前后端服务的端口配置：

### 后端端口配置

1. 在`backend/config.env`文件中设置：
   ```
   PORT=5000  # 将5000更改为你希望使用的端口
   ```

2. 启动后端时将使用此端口：
   ```bash
   cd backend
   python run.py  # 将使用config.env中的PORT配置
   ```

### 前端端口配置

1. 在`frontend/.env`文件中设置：
   ```
   FRONTEND_PORT=3000
   BACKEND_PORT=5000
   BACKEND_URL=http://localhost:5000
   ```

2. 启动前端开发服务器：
   ```bash
   cd frontend
   npm run dev  # 将使用.env中的FRONTEND_PORT配置
   ```

### 更多端口配置说明

更详细的端口配置说明，请参考[端口配置使用指南](PORT_CONFIG_GUIDE.md)。

## 运行系统

### 运行后端

```bash
cd backend
python run.py
```

### 运行前端（开发模式）

```bash
cd frontend
npm run dev
```

### 前端构建生产版本

```bash
cd frontend
npm run build
```

## 系统维护

### 备份数据库

```bash
# Windows
mysqldump -u industrial_user -p industrial_knowledge > backup.sql

# Linux
mysqldump -u industrial_user -p industrial_knowledge | gzip > backup_$(date +%Y%m%d).sql.gz
```

### 定期清理临时文件

可以创建定时任务清理不必要的临时文件：

```bash
find /path/to/project/backend/uploads/temp -type f -mtime +7 -delete
```

## 故障排除

### 文档转换问题

- Windows: 确保Microsoft Office正常运行，检查COM对象是否可访问
- Linux: 确保LibreOffice和unoconv已正确安装并可执行

### 文件上传问题

- 检查文件夹权限，确保web服务器用户有权限写入uploads目录
- 检查storage配额，确保有足够的磁盘空间

### API连接问题

- 检查CORS配置
- 确认JWT令牌正确配置

## 更多资源

- Flask文档: https://flask.palletsprojects.com/
- Vue.js文档: https://vuejs.org/guide/introduction.html
- Element Plus UI: https://element-plus.org/
