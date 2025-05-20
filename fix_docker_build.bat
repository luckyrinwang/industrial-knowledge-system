@echo off
REM Docker构建问题一键修复脚本 (Windows版)

echo ===========================================
echo    Docker构建问题一键修复脚本 (Windows版)
echo ===========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo 请使用管理员权限运行此脚本
    echo 右键点击脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo 1. 创建修复环境...
mkdir docker-build-fix
cd docker-build-fix

REM 创建修复版Dockerfile
echo # 后端Dockerfile - 修复版本 > Dockerfile.backend.fixed
echo FROM python:3.9-slim >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 设置国内Debian镜像源 >> Dockerfile.backend.fixed
echo RUN echo 'deb https://mirrors.ustc.edu.cn/debian/ bookworm main contrib non-free non-free-firmware' ^> /etc/apt/sources.list ^&^& ^\ >> Dockerfile.backend.fixed
echo     echo 'deb https://mirrors.ustc.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware' ^>^> /etc/apt/sources.list ^&^& ^\ >> Dockerfile.backend.fixed
echo     echo 'deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware' ^>^> /etc/apt/sources.list >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 安装系统依赖 >> Dockerfile.backend.fixed
echo RUN apt-get update ^&^& ^\ >> Dockerfile.backend.fixed
echo     apt-get install -y --no-install-recommends ^\ >> Dockerfile.backend.fixed
echo         libreoffice ^\ >> Dockerfile.backend.fixed
echo         unoconv ^\ >> Dockerfile.backend.fixed
echo         ca-certificates ^\ >> Dockerfile.backend.fixed
echo     ^&^& apt-get clean ^\ >> Dockerfile.backend.fixed
echo     ^&^& rm -rf /var/lib/apt/lists/* >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 设置工作目录 >> Dockerfile.backend.fixed
echo WORKDIR /app >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 复制依赖文件 >> Dockerfile.backend.fixed
echo COPY requirements.txt . >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 设置pip配置 >> Dockerfile.backend.fixed
echo RUN pip config set global.timeout 300 ^&^& ^\ >> Dockerfile.backend.fixed
echo     pip config set global.retries 10 ^&^& ^\ >> Dockerfile.backend.fixed
echo     pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ ^&^& ^\ >> Dockerfile.backend.fixed
echo     pip config set global.trusted-host mirrors.aliyun.com >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 安装Python依赖 >> Dockerfile.backend.fixed
echo RUN pip install --no-cache-dir -r requirements.txt >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 复制应用程序代码 >> Dockerfile.backend.fixed
echo COPY backend/ . >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 创建上传目录 >> Dockerfile.backend.fixed
echo RUN mkdir -p uploads ^&^& chmod 777 uploads >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 设置端口 >> Dockerfile.backend.fixed
echo ENV PORT=5000 >> Dockerfile.backend.fixed
echo EXPOSE ${PORT} >> Dockerfile.backend.fixed
echo. >> Dockerfile.backend.fixed
echo # 运行应用 >> Dockerfile.backend.fixed
echo CMD ["python", "run.py"] >> Dockerfile.backend.fixed

REM 创建修复版Docker Compose文件
echo version: '3' > docker-compose.fixed.yml
echo. >> docker-compose.fixed.yml
echo services: >> docker-compose.fixed.yml
echo   # MySQL数据库 >> docker-compose.fixed.yml
echo   db: >> docker-compose.fixed.yml
echo     image: mysql:8.0 >> docker-compose.fixed.yml
echo     restart: always >> docker-compose.fixed.yml
echo     environment: >> docker-compose.fixed.yml
echo       MYSQL_ROOT_PASSWORD: rootpassword >> docker-compose.fixed.yml
echo       MYSQL_DATABASE: industrial_knowledge >> docker-compose.fixed.yml
echo       MYSQL_USER: industrial_user >> docker-compose.fixed.yml
echo       MYSQL_PASSWORD: industrial_password >> docker-compose.fixed.yml
echo     volumes: >> docker-compose.fixed.yml
echo       - db_data:/var/lib/mysql >> docker-compose.fixed.yml
echo     networks: >> docker-compose.fixed.yml
echo       - app_network >> docker-compose.fixed.yml
echo. >> docker-compose.fixed.yml
echo   # 后端API服务（使用修改版Dockerfile） >> docker-compose.fixed.yml
echo   backend: >> docker-compose.fixed.yml
echo     build: >> docker-compose.fixed.yml
echo       context: .. >> docker-compose.fixed.yml
echo       dockerfile: docker-build-fix/Dockerfile.backend.fixed >> docker-compose.fixed.yml
echo     restart: always >> docker-compose.fixed.yml
echo     depends_on: >> docker-compose.fixed.yml
echo       - db >> docker-compose.fixed.yml
echo     environment: >> docker-compose.fixed.yml
echo       - SECRET_KEY=production_secret_key >> docker-compose.fixed.yml
echo       - JWT_SECRET_KEY=production_jwt_secret_key >> docker-compose.fixed.yml
echo       - DATABASE_URI=mysql+pymysql://industrial_user:industrial_password@db/industrial_knowledge >> docker-compose.fixed.yml
echo       - PORT=5000 >> docker-compose.fixed.yml
echo     ports: >> docker-compose.fixed.yml
echo       - "5000:5000" >> docker-compose.fixed.yml
echo     volumes: >> docker-compose.fixed.yml
echo       - uploads_data:/app/uploads >> docker-compose.fixed.yml
echo     networks: >> docker-compose.fixed.yml
echo       - app_network >> docker-compose.fixed.yml
echo. >> docker-compose.fixed.yml
echo   # 前端Web服务 >> docker-compose.fixed.yml
echo   frontend: >> docker-compose.fixed.yml
echo     build: >> docker-compose.fixed.yml
echo       context: .. >> docker-compose.fixed.yml
echo       dockerfile: Dockerfile.frontend >> docker-compose.fixed.yml
echo     restart: always >> docker-compose.fixed.yml
echo     depends_on: >> docker-compose.fixed.yml
echo       - backend >> docker-compose.fixed.yml
echo     ports: >> docker-compose.fixed.yml
echo       - "80:80" >> docker-compose.fixed.yml
echo     networks: >> docker-compose.fixed.yml
echo       - app_network >> docker-compose.fixed.yml
echo. >> docker-compose.fixed.yml
echo # 持久化卷 >> docker-compose.fixed.yml
echo volumes: >> docker-compose.fixed.yml
echo   db_data: >> docker-compose.fixed.yml
echo   uploads_data: >> docker-compose.fixed.yml
echo. >> docker-compose.fixed.yml
echo # 网络配置 >> docker-compose.fixed.yml
echo networks: >> docker-compose.fixed.yml
echo   app_network: >> docker-compose.fixed.yml
echo     driver: bridge >> docker-compose.fixed.yml

echo 2. 设置环境变量...
set DOCKER_BUILDKIT=1
set COMPOSE_DOCKER_CLI_BUILD=1
set DOCKER_CLIENT_TIMEOUT=300
set COMPOSE_HTTP_TIMEOUT=300

echo 3. 尝试拉取基础镜像...
docker pull python:3.9-slim

echo 4. 启动修复版环境...
cd ..
docker-compose -f docker-build-fix/docker-compose.fixed.yml up -d

echo ===========================================
echo 修复完成! 系统应该正在启动中。
echo 如果仍然遇到问题，请参考以下文档:
echo  - DOCKER_DEBIAN_TIMEOUT_FIX.md
echo  - PIP_TIMEOUT_FIX.md
echo  - DOCKER_GUI_TOOLS.md
echo ===========================================

pause
