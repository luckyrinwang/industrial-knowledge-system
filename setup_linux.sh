#!/bin/bash

echo "==================================================="
echo "基于大模型的工业知识库系统 - Linux环境搭建脚本"
echo "==================================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3。请安装Python 3.9或更高版本。"
    exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "检测到Python版本: $PYTHON_VERSION"

# 检查pip是否可用
if ! command -v pip3 &> /dev/null; then
    echo "[错误] 未检测到pip3。请确保pip已安装。"
    exit 1
fi

# 检查是否已经存在虚拟环境
if [ -d "venv" ]; then
    echo "检测到已存在的虚拟环境。"
    read -p "是否重新创建虚拟环境？(y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除现有虚拟环境..."
        rm -rf venv
    else
        echo "使用现有虚拟环境..."
    fi
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建新的虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 创建虚拟环境失败。"
        exit 1
    fi
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[错误] 激活虚拟环境失败。"
    exit 1
fi

# 安装后端依赖
echo "安装后端依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[警告] 安装依赖时出现错误，请手动检查。"
fi

# 检查LibreOffice是否安装
if ! command -v libreoffice &> /dev/null; then
    echo "[警告] 未检测到LibreOffice。文档转换功能需要LibreOffice。"
    read -p "是否安装LibreOffice? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 检测Linux发行版
        if [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            echo "检测到Debian/Ubuntu系统，使用apt安装..."
            sudo apt update
            sudo apt install -y libreoffice
        elif [ -f /etc/redhat-release ]; then
            # CentOS/RHEL
            echo "检测到CentOS/RHEL系统，使用yum安装..."
            sudo yum install -y libreoffice
        else
            echo "[错误] 无法确定Linux发行版，请手动安装LibreOffice。"
        fi
    fi
fi

# 检查unoconv是否安装
if ! command -v unoconv &> /dev/null; then
    echo "[警告] 未检测到unoconv。文档转换功能需要unoconv。"
    read -p "是否安装unoconv? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 检测Linux发行版
        if [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            sudo apt install -y unoconv
        elif [ -f /etc/redhat-release ]; then
            # CentOS/RHEL
            sudo yum install -y unoconv
        else
            echo "[错误] 无法确定Linux发行版，请手动安装unoconv。"
        fi
    fi
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "[警告] 未检测到Node.js。前端开发需要Node.js 14+。"
else
    # 安装前端依赖
    echo "安装前端依赖..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        echo "[警告] 安装前端依赖时出现错误，请手动检查。"
    fi
    cd ..
fi

# 检查后端配置
if [ ! -f "backend/config.env" ]; then
    echo "创建后端配置文件..."
    cat > backend/config.env << EOL
SECRET_KEY=dev_secret_key
JWT_SECRET_KEY=jwt_dev_secret_key
DATABASE_URI=sqlite:///industrial_knowledge.db
EOL
    echo "[提示] 已创建默认配置文件。生产环境请修改backend/config.env中的密钥和数据库设置。"
fi

# 检查数据库是否存在
if [ ! -f "backend/industrial_knowledge.db" ]; then
    echo "初始化数据库..."
    cd backend
    python init_db.py
    if [ $? -ne 0 ]; then
        echo "[错误] 初始化数据库失败。"
        cd ..
        exit 1
    fi
    cd ..
fi

# 设置uploads目录权限
echo "设置uploads目录权限..."
mkdir -p backend/uploads
chmod -R 755 backend/uploads

echo ""
echo "==================================================="
echo "环境设置完成！"
echo ""
echo "运行后端: cd backend && python run.py"
echo "运行前端: cd frontend && npm run dev"
echo "==================================================="
