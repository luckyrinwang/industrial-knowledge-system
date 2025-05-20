@echo off
REM 用于预下载Python依赖，解决pip安装超时问题
REM 在构建Docker镜像前运行此脚本

echo ===== 开始预下载Python依赖 =====

REM 创建缓存目录
if not exist docker_pip_cache mkdir docker_pip_cache

REM 下载依赖包到本地目录
echo 下载依赖到本地目录...
pip download -r requirements.txt -d ./docker_pip_cache

REM 检查结果
if %ERRORLEVEL% equ 0 (
    echo 下载完成! 
    echo 现在可以使用以下命令构建Docker镜像：
    echo docker build -t industrial-knowledge-backend -f Dockerfile.backend.offline .
) else (
    echo 下载过程中出现错误，请检查网络连接或尝试设置不同的PyPI镜像源。
)
