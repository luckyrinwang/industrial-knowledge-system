@echo off
echo 安装工业知识库系统所需的依赖...

:: 安装基本依赖
pip install -r requirements.txt

:: 安装RAGFlow所需的额外依赖
pip install requests

:: 安装文档转换所需的依赖
pip install pywin32

echo 依赖安装完成！
