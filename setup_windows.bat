@echo off
SETLOCAL EnableExtensions

echo ===================================================
echo ���ڴ�ģ�͵Ĺ�ҵ֪ʶ��ϵͳ - ������ű�
echo ===================================================
echo.

:: ���Python�Ƿ�װ
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [����] δ��⵽Python���밲װPython 3.9����߰汾��
    goto :end
)

:: ���Python�汾
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo ��⵽Python�汾: %PYTHON_VERSION%

:: ���pip�Ƿ����
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [����] δ��⵽pip����ȷ��pip�Ѱ�װ��
    goto :end
)

:: ����Ƿ��Ѿ��������⻷��
if exist venv\ (
    echo ��⵽�Ѵ��ڵ����⻷����
    choice /M "�Ƿ����´������⻷����"
    if errorlevel 2 goto activate_venv
    
    echo ɾ���������⻷��...
    rmdir /S /Q venv
)

:: �������⻷��
echo �����µ����⻷��...
python -m venv venv
if %errorlevel% neq 0 (
    echo [����] �������⻷��ʧ�ܡ�
    goto :end
)

:activate_venv
:: �������⻷��
echo �������⻷��...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [����] �������⻷��ʧ�ܡ�
    goto :end
)

:: ����pip
echo ����pip�����°汾...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [����] ����pipʧ�ܣ�����ʹ�õ�ǰ�汾��
)

:: ��װ�������
echo ��װ�������...
if exist requirements-windows.txt (
    echo ʹ��Windowsר�������ļ�...
    pip install -r requirements-windows.txt 2> pip_error.log
) else (
    echo ʹ��ͨ�������ļ�...
    pip install -r requirements.txt 2> pip_error.log
)

if %errorlevel% neq 0 (
    echo [����] ��װ����ʱ���ִ�����鿴pip_error.log�ļ��˽����顣
    echo ���Ե�����װ��������...
    pip install flask flask-cors flask-jwt-extended flask-sqlalchemy
    pip install SQLAlchemy PyMySQL python-dotenv Pillow requests bcrypt
    
    if %ERRORLEVEL% neq 0 (
        echo [����] ����������װʧ�ܣ����ֶ���黷����
    ) else (
        echo [��Ϣ] ����������װ�ɹ���
        if %PROCESSOR_ARCHITECTURE%==AMD64 (
            echo ���԰�װpywin32...
            pip install pywin32
        )
    )
)

:: ���Node.js�Ƿ�װ
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [����] δ��⵽Node.js��ǰ�˿�����ҪNode.js 14+��
    goto backend_setup
)

:: ��װǰ������
echo ��װǰ������...
cd frontend
npm install
if %errorlevel% neq 0 (
    echo [����] ��װǰ������ʱ���ִ������ֶ���顣
) else (
    echo ��鲢�޸�ǰ�������İ�ȫ©��...
    npm audit fix
    if %errorlevel% neq 0 (
        echo [����] ĳЩ��ȫ©���޷��Զ��޸�����鿴npm audit���档
    ) else (
        echo [��Ϣ] ��ȫ©�����޸���
    )
)
cd ..

:backend_setup
:: ���������
if not exist backend\config.env (
    echo ������������ļ�...
    (
        echo SECRET_KEY=dev_secret_key
        echo JWT_SECRET_KEY=jwt_dev_secret_key
        echo DATABASE_URI=sqlite:///industrial_knowledge.db
    ) > backend\config.env
    echo [��ʾ] �Ѵ���Ĭ�������ļ��������������޸�backend\config.env�е���Կ�����ݿ����á�
)

:: ���SQLite���ݿ��Ƿ����
if not exist backend\industrial_knowledge.db (
    echo ��ʼ�����ݿ�...
    cd backend
    python init_db.py
    if %errorlevel% neq 0 (
        echo [����] ��ʼ�����ݿ�ʧ�ܡ�
        cd ..
        goto :end
    )
    cd ..
)

:: ���Microsoft Office (Word)
reg query "HKEY_CLASSES_ROOT\Word.Application" >nul 2>&1
if %errorlevel% neq 0 (
    echo [����] δ��⵽Microsoft Word���ĵ�תPDF���ܿ��ܲ����á�
)

echo.
echo ===================================================
echo ����������ɣ�
echo.
echo ���к��: cd backend && python run.py
echo ����ǰ��: cd frontend && npm run dev
echo ===================================================

:end
pause
