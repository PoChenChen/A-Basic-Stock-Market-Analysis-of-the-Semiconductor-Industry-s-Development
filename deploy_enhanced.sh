#!/bin/bash

# 增強版股票分析預測系統部署腳本
# 適用於 Linux/macOS 環境

echo "🚀 開始部署增強版股票分析預測系統..."

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
mkdir -p mysite/logs
mkdir -p mysite/staticfiles
mkdir -p mysite/media
mkdir -p data_backup
mkdir -p prediction_reports

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

# 創建配置文件
echo "⚙️ 創建預測配置文件..."
if [ ! -f "prediction_config.json" ]; then
    cat > prediction_config.json << 'EOF'
{
  "prediction_periods": {
    "short": 7,
    "medium": 30,
    "long": 90
  },
  "window_sizes": {
    "short": 20,
    "medium": 30,
    "long": 60
  },
  "model_parameters": {
    "epochs": 50,
    "batch_size": 32,
    "learning_rate": 0.001,
    "lstm_layers": [128, 64, 32],
    "dropout_rate": 0.2
  },
  "data_settings": {
    "min_data_points": 100,
    "train_test_split": 0.8,
    "validation_split": 0.2
  },
  "output_settings": {
    "chart_quality": "high",
    "save_predictions": true,
    "generate_report": true
  }
}
EOF
    echo "✅ 預測配置文件已創建"
else
    echo "✅ 預測配置文件已存在"
fi

# 設定執行權限
echo "🔐 設定執行權限..."
chmod +x enhanced_prediction.py
chmod +x auto_data_collector.py
chmod +x interactive_prediction.py

# 測試新功能
echo "🧪 測試新功能..."
echo "測試互動式配置界面..."
python interactive_prediction.py --show

echo "測試自動化數據收集器..."
python auto_data_collector.py test

# 顯示部署完成訊息
echo ""
echo "🎉 增強版部署完成！"
echo ""
echo "📋 新增功能:"
echo "✅ 多時間區間預測 (短期/中期/長期)"
echo "✅ 疊加模型預測曲線"
echo "✅ 自動化數據抓取"
echo "✅ 互動式配置界面"
echo "✅ 增強的LSTM模型"
echo ""
echo "📋 使用方法:"
echo "1. 互動式配置: python interactive_prediction.py"
echo "2. 增強版預測: python enhanced_prediction.py"
echo "3. 自動數據收集: python auto_data_collector.py collect"
echo "4. 定時任務: python auto_data_collector.py schedule"
echo "5. 啟動Web服務: cd mysite && python manage.py runserver"
echo ""
echo "📚 詳細說明請參考 README.md 文件"
echo "📝 日誌文件位置: logs/"
echo "⚙️ 配置文件: prediction_config.json"
echo ""
echo "🔧 如需幫助，請查看 README.md 或提交 Issue"
