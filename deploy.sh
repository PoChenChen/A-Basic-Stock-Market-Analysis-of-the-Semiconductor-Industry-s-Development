#!/bin/bash

# 股票分析預測系統部署腳本
# 適用於 Linux/macOS 環境

echo "🚀 開始部署股票分析預測系統..."

# 檢查 Python 版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ 錯誤: 需要 Python 3.8 或更高版本，當前版本: $python_version"
    exit 1
fi
echo "✅ Python 版本檢查通過: $python_version"

# 創建虛擬環境
if [ ! -d ".venv" ]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv .venv
else
    echo "✅ 虛擬環境已存在"
fi

# 啟動虛擬環境
echo "🔧 啟動虛擬環境..."
source .venv/bin/activate

# 升級 pip
echo "⬆️ 升級 pip..."
pip install --upgrade pip

# 安裝依賴套件
echo "📚 安裝依賴套件..."
pip install -r requirements.txt

# 創建必要目錄
echo "📁 創建必要目錄..."
mkdir -p logs
mkdir -p mysite/staticfiles
mkdir -p mysite/media

# 進入 Django 專案目錄
cd mysite

# 執行資料庫遷移
echo "🗄️ 執行資料庫遷移..."
python manage.py makemigrations
python manage.py migrate

# 收集靜態文件
echo "📦 收集靜態文件..."
python manage.py collectstatic --noinput

# 創建超級用戶（如果不存在）
if [ ! -f "superuser_created" ]; then
    echo "👤 創建超級用戶..."
    echo "請輸入超級用戶資訊:"
    python manage.py createsuperuser
    touch superuser_created
else
    echo "✅ 超級用戶已存在"
fi

# 返回根目錄
cd ..

# 檢查數據文件
echo "📊 檢查數據文件..."
if [ ! -d "mysite/data" ]; then
    echo "⚠️ 警告: 數據目錄不存在，請確保已放置必要的 CSV 文件"
fi

# 顯示部署完成訊息
echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 下一步操作:"
echo "1. 啟動開發伺服器: cd mysite && python manage.py runserver"
echo "2. 訪問網站: http://localhost:8000"
echo "3. 執行數據抓取: python industry_data.py"
echo "4. 執行股價預測: python Learing.py"
echo ""
echo "📚 詳細說明請參考 README.md 文件"
echo "📝 日誌文件位置: logs/app.log"
echo ""
echo "🔧 如需幫助，請查看 README.md 或提交 Issue"

