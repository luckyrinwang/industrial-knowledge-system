import os
import sys

# 将当前目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入Flask应用
from app import app

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    app.run(debug=True, host='0.0.0.0', port=port) 