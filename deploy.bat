@echo off
chcp 65001 >nul
echo 🚀 開始部署股票分析預測系統...

REM 檢查 Python 版本
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到 Python，請確保已安裝 Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python 檢查通過

REM 創建虛擬環境
if not exist ".venv" (
    echo 📦 創建虛擬環境...
    python -m venv .venv
) else (
    echo ✅ 虛擬環境已存在
)

REM 啟動虛擬環境
echo 🔧 啟動虛擬環境...
call .venv\Scripts\activate.bat

REM 升級 pip
echo ⬆️ 升級 pip...
python -m pip install --upgrade pip

REM 安裝依賴套件
echo 📚 安裝依賴套件...
pip install -r requirements.txt

REM 創建必要目錄
echo 📁 創建必要目錄...
if not exist "logs" mkdir logs
if not exist "mysite\logs" mkdir mysite\logs
if not exist "mysite\staticfiles" mkdir mysite\staticfiles
if not exist "mysite\media" mkdir mysite\media

REM 進入 Django 專案目錄
cd mysite

REM 執行資料庫遷移
echo 🗄️ 執行資料庫遷移...
python manage.py makemigrations
python manage.py migrate

REM 收集靜態文件
echo 📦 收集靜態文件...
python manage.py collectstatic --noinput

REM 創建超級用戶（如果不存在）
if not exist "superuser_created" (
    echo 👤 創建超級用戶...
    echo 請輸入超級用戶資訊:
    python manage.py createsuperuser
    echo. > superuser_created
) else (
    echo ✅ 超級用戶已存在
)

REM 返回根目錄
cd ..

REM 檢查數據文件
echo 📊 檢查數據文件...
if not exist "mysite\data" (
    echo ⚠️ 警告: 數據目錄不存在，請確保已放置必要的 CSV 文件
)

REM 顯示部署完成訊息
echo.
echo 🎉 部署完成！
echo.
echo 📋 下一步操作:
echo 1. 啟動開發伺服器: cd mysite ^&^& python manage.py runserver
echo 2. 訪問網站: http://localhost:8000
echo 3. 執行數據抓取: python industry_data.py
echo 4. 執行股價預測: python Learing.py
echo.
echo 📚 詳細說明請參考 README.md 文件
echo 📝 日誌文件位置: logs/app.log
echo.
echo 🔧 如需幫助，請查看 README.md 或提交 Issue
pause
