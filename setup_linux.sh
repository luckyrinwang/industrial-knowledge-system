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
    read -p "是否安装LibreOffice和中文字体? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 检测Linux发行版
        if [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            echo "检测到Debian/Ubuntu系统，使用apt安装..."
            sudo apt update
            sudo apt install -y libreoffice \
                ca-certificates \
                fonts-noto-cjk \
                fonts-arphic-ukai \
                fonts-arphic-uming \
                fonts-wqy-zenhei \
                fonts-wqy-microhei
        elif [ -f /etc/redhat-release ]; then
            # CentOS/RHEL
            echo "检测到CentOS/RHEL系统，使用yum安装..."
            sudo yum install -y libreoffice \
                google-noto-cjk-fonts \
                wqy-microhei-fonts \
                wqy-zenhei-fonts
        else
            echo "[错误] 无法确定Linux发行版，请手动安装LibreOffice和中文字体。"
        fi
    fi
else
    # LibreOffice已安装，检查中文字体
    echo "LibreOffice已安装，检查中文字体..."
    FONTS_MISSING=false
    
    # 检查常见中文字体目录
    if [ ! -d "/usr/share/fonts/truetype/wqy" ] && [ ! -d "/usr/share/fonts/opentype/noto" ]; then
        FONTS_MISSING=true
    fi
    
    if [ "$FONTS_MISSING" = true ]; then
        echo "[警告] 可能缺少中文字体，这可能导致PDF转换中文乱码。"
        read -p "是否安装中文字体? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ -f /etc/debian_version ]; then
                # Debian/Ubuntu
                sudo apt update
                sudo apt install -y fonts-noto-cjk \
                    fonts-arphic-ukai \
                    fonts-arphic-uming \
                    fonts-wqy-zenhei \
                    fonts-wqy-microhei
            elif [ -f /etc/redhat-release ]; then
                # CentOS/RHEL
                sudo yum install -y google-noto-cjk-fonts \
                    wqy-microhei-fonts \
                    wqy-zenhei-fonts
            fi
            
            # 更新字体缓存
            echo "更新字体缓存..."
            sudo fc-cache -f -v
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
PORT=5000
EOL
    echo "[提示] 已创建默认配置文件。生产环境请修改backend/config.env中的密钥和数据库设置。"
fi

# 检查前端配置
if [ ! -f "frontend/.env" ]; then
    echo "创建前端环境配置文件..."
    cat > frontend/.env << EOL
FRONTEND_PORT=3000
BACKEND_PORT=5000
BACKEND_URL=http://localhost:5000
EOL
    echo "[提示] 已创建前端环境配置文件。可以修改frontend/.env自定义端口设置。"
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

# 检查系统locale设置
echo "检查系统中文locale设置..."
if ! locale -a | grep -q "zh_CN.utf8\|zh_CN.UTF-8"; then
    echo "[警告] 系统可能缺少中文locale，这可能影响中文PDF转换。"
    read -p "是否配置中文locale? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f /etc/debian_version ]; then
            # Debian/Ubuntu
            sudo apt install -y locales
            echo "zh_CN.UTF-8 UTF-8" | sudo tee -a /etc/locale.gen
            sudo locale-gen
        elif [ -f /etc/redhat-release ]; then
            # CentOS/RHEL
            sudo yum install -y glibc-locale-source glibc-langpack-zh
        fi
    fi
fi

echo ""
echo "==================================================="
echo "环境设置完成！"
echo ""
echo "运行后端: cd backend && python run.py"
echo "运行前端: cd frontend && npm run dev"
echo "==================================================="
