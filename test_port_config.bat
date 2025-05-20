@echo off
:: 端口配置测试脚本 test_port_config.bat
setlocal enabledelayedexpansion

echo ==========================================
echo    端口配置测试脚本
echo ==========================================

:: 检查后端端口配置
if exist backend\config.env (
    for /f "tokens=1,* delims==" %%a in ('type backend\config.env ^| findstr "PORT="') do (
        echo 后端配置文件中的端口: %%b
        set BACKEND_PORT=%%b
    )
) else (
    echo 警告: 未找到backend\config.env配置文件
)

:: 检查前端端口配置
if exist frontend\.env (
    for /f "tokens=1,* delims==" %%a in ('type frontend\.env ^| findstr "FRONTEND_PORT="') do (
        echo 前端配置文件中的前端端口: %%b
        set FRONTEND_PORT=%%b
    )
    
    for /f "tokens=1,* delims==" %%a in ('type frontend\.env ^| findstr "BACKEND_PORT="') do (
        echo 前端配置文件中的后端端口: %%b
    )
    
    for /f "tokens=1,* delims==" %%a in ('type frontend\.env ^| findstr "BACKEND_URL="') do (
        echo 前端配置文件中的后端URL: %%b
    )
) else (
    echo 警告: 未找到frontend\.env配置文件
)

:: 检查Docker环境变量
if exist .env (
    for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr "FRONTEND_PORT="') do (
        echo Docker配置文件中的前端端口: %%b
    )
    
    for /f "tokens=1,* delims==" %%a in ('type .env ^| findstr "BACKEND_PORT="') do (
        echo Docker配置文件中的后端端口: %%b
    )
) else (
    echo 信息: 未找到Docker .env配置文件
)

:: 检查端口占用情况
echo.
echo 检查端口占用情况...

:: 检查默认端口
call :check_port 5000
call :check_port 3000
call :check_port 80

if defined BACKEND_PORT (
    call :check_port !BACKEND_PORT!
)

if defined FRONTEND_PORT (
    call :check_port !FRONTEND_PORT!
)

echo.
echo 端口配置测试完成。
goto :eof

:check_port
netstat -ano | findstr ":%1 "
if %errorlevel% equ 0 (
    echo 警告: 端口 %1 已被占用!
) else (
    echo 信息: 端口 %1 可用。
)
goto :eof
