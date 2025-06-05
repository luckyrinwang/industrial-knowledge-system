@echo off
setlocal enabledelayedexpansion

REM 工业知识库系统 - 中国大陆一键部署脚本 (Windows)
REM Industrial Knowledge System - China Quick Deploy Script (Windows)

echo 🚀 开始部署工业知识库系统...
echo 📍 针对中国大陆网络环境优化
echo ================================================

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker 环境检查通过

REM 检查端口占用
echo 🔍 检查端口占用情况...

netstat -an | find ":3000 " | find "LISTENING" >nul
if not errorlevel 1 (
    echo ⚠️ 端口 3000 已被占用，请手动停止相关服务或修改 docker-compose.yml 中的端口配置
    set /p choice=是否继续部署？^(y/N^): 
    if /i not "!choice!"=="y" exit /b 1
)

netstat -an | find ":5000 " | find "LISTENING" >nul
if not errorlevel 1 (
    echo ⚠️ 端口 5000 已被占用，请手动停止相关服务或修改 docker-compose.yml 中的端口配置
    set /p choice=是否继续部署？^(y/N^): 
    if /i not "!choice!"=="y" exit /b 1
)

echo ✅ 端口检查完成

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist "backend\uploads\document" mkdir backend\uploads\document
if not exist "backend\uploads\image" mkdir backend\uploads\image
if not exist "backend\uploads\pdf" mkdir backend\uploads\pdf
if not exist "backend\uploads\md" mkdir backend\uploads\md
if not exist "backend\uploads\spreadsheet" mkdir backend\uploads\spreadsheet
if not exist "backend\uploads\video" mkdir backend\uploads\video
if not exist "backend\logs" mkdir backend\logs

REM 复制配置文件模板
if not exist "backend\config.env" (
    echo 📝 创建后端配置文件...
    if exist "backend\config.env.example" (
        copy "backend\config.env.example" "backend\config.env" >nul
        echo ✅ 已复制配置模板，请根据需要修改 backend\config.env
    ) else (
        echo ⚠️ 配置模板文件不存在，使用默认配置
    )
)

REM 提示配置Docker镜像加速
echo 💡 建议配置Docker镜像加速以提高下载速度
echo    请在Docker Desktop设置中添加以下镜像源：
echo    - https://docker.m.daocloud.io
echo    - https://dockerproxy.com
echo    - https://mirror.baidubce.com
echo.
echo    或运行: setup_docker_mirrors.bat 自动配置
echo.
set /p choice=已配置镜像加速？继续部署？^(y/N^): 
if /i not "!choice!"=="y" (
    echo 请先配置Docker镜像加速，然后重新运行此脚本
    pause
    exit /b 1
)

REM 构建并启动服务
echo 🏗️ 构建Docker镜像...
echo 💡 首次构建可能需要较长时间，请耐心等待...

set DOCKER_BUILDKIT=1
docker-compose build --no-cache --progress=plain

if errorlevel 1 (
    echo ❌ 镜像构建失败，请检查网络连接或查看错误信息
    pause
    exit /b 1
)

echo 🚀 启动服务...
docker-compose up -d

if errorlevel 1 (
    echo ❌ 服务启动失败
    pause
    exit /b 1
)

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose ps

REM 初始化数据库
echo 🗄️ 初始化数据库...
docker-compose exec -T backend python init_db.py

echo.
echo 🎉 部署完成！
echo ================================================
echo 📱 访问地址：
echo    前端应用: http://localhost:3000
echo    后端API:  http://localhost:5000
echo.
echo 🔧 管理命令：
echo    查看日志: docker-compose logs -f
echo    停止服务: docker-compose stop
echo    重启服务: docker-compose restart
echo    完全清理: docker-compose down
echo.
echo 📚 更多信息请查看 README.md 和 SETUP_GUIDE.md
echo.

REM 健康检查
echo 🩺 健康检查...
timeout /t 5 /nobreak >nul

REM 使用curl检查服务（如果可用）
curl -f http://localhost:5000/health >nul 2>&1
if not errorlevel 1 (
    echo ✅ 后端服务运行正常
) else (
    echo ⚠️ 后端服务可能存在问题，请查看日志：
    echo    docker-compose logs backend
)

curl -f http://localhost:3000 >nul 2>&1
if not errorlevel 1 (
    echo ✅ 前端服务运行正常
) else (
    echo ⚠️ 前端服务可能存在问题，请查看日志：
    echo    docker-compose logs frontend
)

echo.
echo 🎊 欢迎使用工业知识库系统！
echo 按任意键退出...
pause >nul
