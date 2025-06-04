@echo off
chcp 65001 >nul
echo === Docker中国镜像源配置脚本 (Windows版) ===
echo 正在配置Docker Desktop使用中国镜像源...
echo.

echo 请按照以下步骤手动配置Docker Desktop：
echo.
echo 1. 打开Docker Desktop
echo 2. 点击右上角的设置图标（齿轮）
echo 3. 选择 "Docker Engine"
echo 4. 在配置文件中添加以下内容：
echo.
echo {
echo   "registry-mirrors": [
echo     "https://registry.cn-hangzhou.aliyuncs.com",
echo     "https://docker.mirrors.ustc.edu.cn",
echo     "https://hub-mirror.c.163.com",
echo     "https://mirror.baidubce.com"
echo   ]
echo }
echo.
echo 5. 点击 "Apply & Restart"
echo.
echo 或者，您也可以复制项目中的 daemon.json 文件到以下位置：
echo Windows: C:\Users\%USERNAME%\.docker\daemon.json
echo.
echo 配置完成后，重新运行：
echo docker compose -p knowledge up -d --build
echo.
pause
