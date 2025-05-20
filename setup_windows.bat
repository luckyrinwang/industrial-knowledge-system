@echo off
SETLOCAL EnableExtensions

echo ===================================================
echo 基于大模型的工业知识库系统 - 安装脚本
echo ===================================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python。请安装Python 3.9或更高版本。
    goto :end
)

:: 读取Python版本
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo 检测到Python版本: %PYTHON_VERSION%

:: 检查pip是否安装
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到pip。请安装pip以便安装依赖包。
    goto :end
)

:: 检查是否已经创建虚拟环境
if exist venv\ (
    echo 检测到已有虚拟环境
    choice /M "是否删除并重新创建虚拟环境？"
    if errorlevel 2 goto activate_venv
    
    echo 删除旧的虚拟环境...
    rmdir /S /Q venv
)

:: 创建虚拟环境
echo 正在创建新的虚拟环境...
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
echo 正在升级pip到最新版本...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [警告] 升级pip失败，继续使用当前版本。
)

:: 安装依赖包
echo 正在安装依赖包...
if exist requirements-windows.txt (
    echo 使用Windows专用依赖文件...
    pip install -r requirements-windows.txt 2> pip_error.log
) else (
    echo 使用通用依赖文件...
    pip install -r requirements.txt 2> pip_error.log
)

if %errorlevel% neq 0 (
    echo [错误] 安装依赖包时发生错误，请查看pip_error.log文件获取详细信息。
    echo 尝试手动安装常用依赖包...
    pip install flask flask-cors flask-jwt-extended flask-sqlalchemy
    pip install SQLAlchemy PyMySQL python-dotenv Pillow requests bcrypt
    
    if %ERRORLEVEL% neq 0 (
        echo [错误] 某些依赖包安装失败，请检查错误信息。
    ) else (
        echo [信息] 常用依赖包安装成功。
        if %PROCESSOR_ARCHITECTURE%==AMD64 (
            echo 检测到64位系统，尝试安装pywin32...
            pip install pywin32
        )
    )
)

:: 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js。请安装Node.js 14或更高版本。
    goto backend_setup
)

:: 安装前端依赖
echo 正在安装前端依赖...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo [错误] 安装前端依赖时发生错误。
) else (
    echo 修复前端依赖中的安全漏洞...
    npm audit fix
    if %errorlevel% neq 0 (
        echo [警告] 某些安全漏洞无法自动修复，请查看npm audit的输出信息。
    ) else (
        echo [信息] 前端依赖安装完成，且安全漏洞已修复。
    )
)
cd ..

:backend_setup
:: 创建配置文件
if not exist backend\config.env (
    echo 创建后端配置文件...
    (
        echo SECRET_KEY=dev_secret_key
        echo JWT_SECRET_KEY=jwt_dev_secret_key
        echo DATABASE_URI=sqlite:///industrial_knowledge.db
        echo PORT=5000
    ) > backend\config.env
    echo [提示] 已创建默认配置文件。生产环境请修改backend\config.env中的密钥和数据库设置。
)

:: 检查前端配置文件
if not exist frontend\.env (
    echo 创建前端环境配置文件...
    (
        echo FRONTEND_PORT=3000
        echo BACKEND_PORT=5000
        echo BACKEND_URL=http://localhost:5000
    ) > frontend\.env
    echo [提示] 已创建前端环境配置文件。可以修改frontend\.env文件自定义端口设置。
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
    echo [警告] 未检测到Microsoft Word，无法转换为PDF格式。
)

echo.
echo ===================================================
echo 安装完成！
echo.
echo 后端启动命令: cd backend && python run.py
echo 前端启动命令: cd frontend && npm run dev
echo ===================================================

:end
pause
