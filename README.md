# 股票分析預測系統 (Stock Analysis and Prediction System)

## 專案概述

這是一個基於 Django 和機器學習的股票分析預測系統，專門針對台灣半導體產業進行分析。系統整合了股票數據抓取、產業分析、股價預測和可視化功能。

## 🚀 主要功能

- **產業分析**: 半導體產業公司排名和分類
- **股價數據**: 2020-2025年（民國109-114年）完整股價數據
- **機器學習預測**: 使用LSTM模型進行股價預測
- **K線圖可視化**: 自動生成包含預測線的K線圖
- **Web介面**: 響應式網頁介面，支援搜尋和篩選

## 📊 數據來源

- **TWSE (台灣證券交易所)**: 2020-2025年上市公司數據
- **產業分類**: 半導體相關產業分類
- **股價數據**: 開盤價、收盤價、最高價、最低價、成交量

## 🛠️ 技術架構

### 後端技術
- **Django 5.2.3**: Web框架
- **SQLite**: 資料庫
- **Pandas**: 數據處理
- **NumPy**: 數值計算

### 機器學習
- **TensorFlow 2.15.0**: 深度學習框架
- **LSTM**: 長短期記憶網路
- **Scikit-learn**: 數據預處理
- **MinMaxScaler**: 數據標準化

### 前端技術
- **Bootstrap 5.3.0**: UI框架
- **HTML5/CSS3**: 響應式設計
- **Django Templates**: 模板引擎

## 📁 專案結構

```
final/
├── mysite/                          # Django 專案目錄
│   ├── webapp/                      # 主要應用
│   │   ├── models.py               # 數據模型
│   │   ├── views.py                # 視圖邏輯
│   │   ├── admin.py                # 管理介面
│   │   └── migrations/             # 資料庫遷移
│   ├── templates/                  # HTML 模板
│   ├── STATIC/                     # 靜態文件
│   │   └── kline_output/          # K線圖輸出
│   ├── data/                       # CSV 數據文件
│   └── mysite/                     # Django 設定
├── Learing.py                      # 機器學習預測主程序
├── industry_data.py                # 產業數據處理
├── test.py                         # 數據抓取程序
├── requirements.txt                 # Python 依賴套件
├── .gitignore                      # Git 忽略文件
└── README.md                       # 專案說明文件
```

## 🔧 安裝與設定

### 環境需求
- Python 3.8+
- pip
- 虛擬環境 (推薦)

### 安裝步驟

1. **克隆專案**
```bash
git clone <repository-url>
cd final
```

2. **創建虛擬環境**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

3. **安裝依賴套件**
```bash
pip install -r requirements.txt
```

4. **環境變數設定**
```bash
# 複製環境變數範例文件
cp .env.example .env
# 編輯 .env 文件，設定必要的環境變數
```

5. **資料庫遷移**
```bash
cd mysite
python manage.py migrate
python manage.py createsuperuser
```

6. **啟動開發伺服器**
```bash
python manage.py runserver
```

## 📈 使用說明

### 1. 數據抓取順序
按照以下順序執行數據抓取程序：

```bash
# 1. 抓取產業排名資訊
python industry_data.py

# 2. 抓取股價數據 (2020-2025年)
python test.py

# 3. 執行機器學習預測
python Learing.py
```

### 2. Web介面使用
1. 訪問 `http://localhost:8000`
2. 查看半導體產業公司列表
3. 點擊公司名稱查看詳細資訊
4. 查看K線圖和近期股價

### 3. 股價預測
- 系統自動為每家公司生成LSTM預測模型
- K線圖包含實際股價和預測股價
- 預測結果儲存在 `mysite/STATIC/kline_output/` 目錄

### 4. 🆕 增強版預測功能
- **多時間區間預測**: 短期（7天）、中期（30天）、長期（90天）
- **互動式配置**: `python interactive_prediction.py`
- **自動化數據收集**: `python auto_data_collector.py collect`
- **定時任務**: `python auto_data_collector.py schedule`
- **增強版預測**: `python enhanced_prediction.py`

## 🔄 最新優化內容 (2025年更新)

### 1. 時間範圍擴展
- **原本**: 2020-2024年數據
- **優化後**: 2020-2025年數據（包含民國114年）
- **修改文件**: `Learing.py` 第16行

### 2. 股價顯示優化
- **原本**: 只顯示特定年份的股價
- **優化後**: 優先顯示最新年份（民國114年）的股價數據
- **修改文件**: `mysite/webapp/views.py` 的 `company_detail` 函數

### 3. 系統架構改進
- 添加完整的日誌記錄系統
- 改進錯誤處理和異常捕獲
- 優化靜態文件配置
- 添加環境變數支援

### 4. 代碼品質提升
- 統一錯誤處理方式
- 添加詳細的日誌記錄
- 改進代碼可讀性和維護性
- 添加參數驗證

### 5. 系統架構修復
- 修復日誌目錄缺失問題 (`No such file or directory: 'mysite/logs/app.log'`)
- 更新部署腳本自動創建必要目錄結構
- 創建快速修復腳本 `fix_logs.py`
- 確保 Django 日誌系統正常運作

## 📝 修改記錄

### 2025年主要修改

| 日期 | 修改內容 | 修改文件 | 影響範圍 |
|------|----------|----------|----------|
| 2025-01 | 擴展年份範圍至2025年 | `Learing.py` | 數據範圍 |
| 2025-01 | 優化股價顯示邏輯 | `views.py` | 用戶體驗 |
| 2025-01 | 添加日誌系統 | 多個文件 | 系統監控 |
| 2025-01 | 改進錯誤處理 | 多個文件 | 系統穩定性 |
| 2025-01 | 優化Django設定 | `settings.py` | 系統配置 |
| 2025-01 | 修復日誌目錄問題 | `deploy.sh`, `deploy.bat`, `fix_logs.py` | 系統穩定性 |

### 技術改進詳情

1. **Learing.py 優化**
   - 年份範圍從 `range(2020, 2025)` 改為 `range(2020, 2026)`
   - 添加完整的日誌記錄
   - 改進錯誤處理和異常捕獲
   - 添加目錄創建和參數驗證

2. **Django Views 優化**
   - 股價數據讀取邏輯改進
   - 優先讀取最新年份數據
   - 添加日誌記錄和錯誤處理
   - 改進用戶體驗

3. **Django Settings 優化**
   - 添加環境變數支援
   - 配置完整的日誌系統
   - 優化靜態文件設定
   - 改進安全性配置

## 🚨 注意事項

1. **數據更新**: 確保定期更新CSV數據文件
2. **模型訓練**: LSTM模型需要足夠的歷史數據
3. **記憶體使用**: 大量數據處理時注意記憶體使用量
4. **生產環境**: 部署前請修改安全設定

## ✅ 已完成的新功能

### 1. 🎯 互動式預測配置系統
- **多時間區間預測**: 支援短期（7天）、中期（30天）、長期（90天）分析
- **可調整參數**: 用戶可自定義預測天數、模型參數、數據設定
- **友好界面**: 提供互動式命令行配置界面
- **配置文件**: 自動保存和載入用戶設定

### 2. 📈 疊加模型預測曲線
- **多模型整合**: 不同時間區間使用不同的LSTM模型
- **預測曲線疊加**: 在K線圖上同時顯示短期、中期、長期預測
- **視覺化增強**: 高品質圖表，支援成交量顯示
- **趨勢分析**: 便於觀察短期與中期趨勢變化

### 3. 🤖 自動化預測流程
- **完整流程**: 涵蓋資料抓取、特徵工程、模型訓練與結果輸出
- **智能調優**: 自動調整模型參數，支援早停機制
- **批量處理**: 自動處理所有上市公司
- **報告生成**: 自動生成預測分析報告

### 4. 📊 自動化數據抓取
- **即時更新**: 自動抓取最新股市資料
- **定時執行**: 支援定時任務（每天下午3:30收集數據，4:00執行預測）
- **智能備份**: 自動備份舊數據，避免數據丟失
- **API整合**: 直接整合TWSE API，確保數據準確性

## 🆕 新增文件說明

| 文件名 | 功能描述 | 使用方法 |
|--------|----------|----------|
| `enhanced_prediction.py` | 增強版預測程序 | `python enhanced_prediction.py` |
| `auto_data_collector.py` | 自動化數據收集器 | `python auto_data_collector.py collect` |
| `interactive_prediction.py` | 互動式配置界面 | `python interactive_prediction.py` |
| `prediction_config.json` | 預測配置文件 | 自動生成，可手動編輯 |
| `deploy_enhanced.sh` | 增強版部署腳本 | `./deploy_enhanced.sh` |
| `fix_logs.py` | 快速修復日誌目錄問題 | `python fix_logs.py` |

## 🤝 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 📞 聯絡資訊

如有問題或建議，請透過以下方式聯絡：
- 專案 Issues: [GitHub Issues](https://github.com/username/repo/issues)
- 電子郵件: andy30326mango@gmail.com

## 🙏 致謝

- 感謝台灣證券交易所提供公開數據
- 感謝開源社群的支持和貢獻
- 感謝所有使用者和測試者的回饋

---

**最後更新**: 2025年1月  
**版本**: 3.0.0 (增強版)  
**維護者**: Your Name
