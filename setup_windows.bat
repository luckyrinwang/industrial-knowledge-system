@echo off
SETLOCAL EnableExtensions

echo ===================================================
echo 基于大模型的工业知识库系统 - 环境搭建脚本
echo ===================================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python。请安装Python 3.9或更高版本。
    goto :end
)

:: 检查Python版本
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo 检测到Python版本: %PYTHON_VERSION%

:: 检查pip是否可用
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到pip。请确保pip已安装。
    goto :end
)

:: 检查是否已经存在虚拟环境
if exist venv\ (
    echo 检测到已存在的虚拟环境。
    choice /M "是否重新创建虚拟环境？"
    if errorlevel 2 goto activate_venv
    
    echo 删除现有虚拟环境...
    rmdir /S /Q venv
)

:: 创建虚拟环境
echo 创建新的虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo [错误] 创建虚拟环境失败。
    goto :end
)

:activate_venv
:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [错误] 激活虚拟环境失败。
    goto :end
)

:: 升级pip
echo 升级pip到最新版本...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [警告] 升级pip失败，继续使用当前版本。
)

:: 安装后端依赖
echo 安装后端依赖...
if exist requirements-windows.txt (
    echo 使用Windows专用依赖文件...
    pip install -r requirements-windows.txt 2> pip_error.log
) else (
    echo 使用通用依赖文件...
    pip install -r requirements.txt 2> pip_error.log
)

if %errorlevel% neq 0 (
    echo [警告] 安装依赖时出现错误，请查看pip_error.log文件了解详情。
    echo 尝试单独安装核心依赖...
    pip install flask flask-cors flask-jwt-extended flask-sqlalchemy
    pip install SQLAlchemy PyMySQL python-dotenv Pillow requests bcrypt
    
    if %ERRORLEVEL% neq 0 (
        echo [错误] 核心依赖安装失败，请手动检查环境。
    ) else (
        echo [信息] 核心依赖安装成功。
        if %PROCESSOR_ARCHITECTURE%==AMD64 (
            echo 尝试安装pywin32...
            pip install pywin32
        )
    )
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到Node.js。前端开发需要Node.js 14+。
    goto backend_setup
)

:: 安装前端依赖
echo 安装前端依赖...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo [警告] 安装前端依赖时出现错误，请手动检查。
) else (
    echo 检查并修复前端依赖的安全漏洞...
    npm audit fix
    if %errorlevel% neq 0 (
        echo [警告] 某些安全漏洞无法自动修复，请查看npm audit报告。
    ) else (
        echo [信息] 安全漏洞已修复。
    )
)
cd ..

:backend_setup
:: 检查后端配置
if not exist backend\config.env (
    echo 创建后端配置文件...
    (
        echo SECRET_KEY=dev_secret_key
        echo JWT_SECRET_KEY=jwt_dev_secret_key
        echo DATABASE_URI=sqlite:///industrial_knowledge.db
    ) > backend\config.env
    echo [提示] 已创建默认配置文件。生产环境请修改backend\config.env中的密钥和数据库设置。
)

:: 检查SQLite数据库是否存在
if not exist backend\industrial_knowledge.db (
    echo 初始化数据库...
    cd backend
    python init_db.py
    if %errorlevel% neq 0 (
        echo [错误] 初始化数据库失败。
        cd ..
        goto :end
    )
    cd ..
)

:: 检查Microsoft Office (Word)
reg query "HKEY_CLASSES_ROOT\Word.Application" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 未检测到Microsoft Word。文档转PDF功能可能不可用。
)

echo.
echo ===================================================
echo 环境设置完成！
echo.
echo 运行后端: cd backend && python run.py
echo 运行前端: cd frontend && npm run dev
echo ===================================================

:end
pause
