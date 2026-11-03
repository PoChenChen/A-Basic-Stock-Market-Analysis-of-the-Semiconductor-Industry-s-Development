#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增強版股票預測系統
支援短期（7天）、中期（30天）、長期（90天）預測
疊加多個模型產生的預測曲線
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_prediction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== 參數設定 ==========
class PredictionConfig:
    def __init__(self):
        self.data_dir = "mysite/data"
        self.years = range(2020, 2026)  # 包含民國114年
        self.output_dir = "mysite/STATIC/kline_output"
        self.logs_dir = "logs"
        
        # 預測時間區間設定
        self.prediction_periods = {
            'short': 7,      # 短期：7天
            'medium': 30,    # 中期：30天
            'long': 90       # 長期：90天
        }
        
        # 模型參數
        self.window_sizes = {
            'short': 20,     # 短期預測使用20天窗口
            'medium': 30,    # 中期預測使用30天窗口
            'long': 60       # 長期預測使用60天窗口
        }
        
        self.epochs = 50
        self.batch_size = 32
        self.learning_rate = 0.001

# ========== 數據處理函數 ==========
def load_and_prepare_data(config):
    """載入並準備數據"""
    logger.info("開始載入數據...")
    
    df_all = []
    for year in config.years:
        file_path = os.path.join(config.data_dir, f"TWSE_{year}_all_companies.csv")
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                df_all.append(df)
                logger.info(f"成功載入 {year} 年數據，共 {len(df)} 筆記錄")
            except Exception as e:
                logger.error(f"載入 {year} 年數據時發生錯誤: {e}")
        else:
            logger.warning(f"檔案不存在：{file_path}")
    
    if not df_all:
        logger.error("沒有找到任何數據文件")
        return pd.DataFrame()
    
    # 合併所有年份數據
    combined_df = pd.concat(df_all, ignore_index=True)
    logger.info(f"數據合併完成，總共 {len(combined_df)} 筆記錄")
    
    return combined_df

def clean_stock_data(df):
    """清理股票數據"""
    logger.info("開始清理數據...")
    
    # 清理列名
    df.columns = df.columns.str.strip()
    
    # 移除無效數據
    df = df.dropna(subset=['公司名稱', '股票代碼'])
    
    # 清理日期格式
    def safe_parse_date(date_str):
        try:
            if pd.isna(date_str):
                return None
            
            date_str = str(date_str)
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    year = int(parts[0])
                    if year < 1911:
                        year += 1911
                    return f"{year}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
            return date_str
        except:
            return None
    
    df['日期'] = df['日期'].apply(safe_parse_date)
    df = df.dropna(subset=['日期'])
    
    # 轉換日期格式
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
    df = df.dropna(subset=['日期'])
    
    # 清理數值欄位
    numeric_columns = ['成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
            df[col] = df[col].replace(['--', 'nan', 'None'], np.nan)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 移除無效價格數據
    df = df.dropna(subset=['開盤價', '最高價', '最低價', '收盤價'])
    
    # 重命名欄位
    df.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '成交股數': 'Volume',
        '公司名稱': 'Company',
        '股票代碼': 'Code'
    }, inplace=True)
    
    logger.info(f"數據清理完成，剩餘 {len(df)} 筆有效記錄")
    return df

# ========== 機器學習模型 ==========
def create_enhanced_lstm_model(input_shape, output_steps=1):
    """創建增強的LSTM模型"""
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(output_steps)
    ])
    
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
    return model

def prepare_sequences(data, window_size, prediction_steps):
    """準備序列數據"""
    X, y = [], []
    for i in range(len(data) - window_size - prediction_steps + 1):
        X.append(data[i:i + window_size])
        y.append(data[i + window_size:i + window_size + prediction_steps])
    return np.array(X), np.array(y)

def train_prediction_model(company_data, window_size, prediction_steps, config):
    """訓練預測模型"""
    try:
        # 準備數據
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(company_data[['Close']])
        
        # 創建序列
        X, y = prepare_sequences(scaled_data, window_size, prediction_steps)
        
        if len(X) < 10:  # 數據太少
            return None, None, None
        
        # 分割訓練和測試數據
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # 創建和訓練模型
        model = create_enhanced_lstm_model((window_size, 1), prediction_steps)
        
        # 早停機制
        from tensorflow.keras.callbacks import EarlyStopping
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        history = model.fit(
            X_train, y_train,
            epochs=config.epochs,
            batch_size=config.batch_size,
            validation_data=(X_test, y_test),
            callbacks=[early_stopping],
            verbose=0
        )
        
        return model, scaler, history
        
    except Exception as e:
        logger.error(f"模型訓練失敗: {e}")
        return None, None, None

# ========== 預測函數 ==========
def predict_future_prices(model, scaler, last_sequence, prediction_steps):
    """預測未來價格"""
    try:
        # 使用最後的序列進行預測
        future_predictions = []
        current_sequence = last_sequence.copy()
        
        for _ in range(prediction_steps):
            # 預測下一個值
            next_pred = model.predict(current_sequence.reshape(1, -1, 1), verbose=0)
            future_predictions.append(next_pred[0, 0])
            
            # 更新序列（移除最早的值，添加預測值）
            current_sequence = np.roll(current_sequence, -1)
            current_sequence[-1] = next_pred[0, 0]
        
        # 反標準化
        future_prices = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
        return future_prices.flatten()
        
    except Exception as e:
        logger.error(f"預測失敗: {e}")
        return None

# ========== 可視化函數 ==========
def create_enhanced_chart(company_data, predictions, company_name, code, config):
    """創建增強的K線圖"""
    try:
        # 準備K線圖數據
        chart_data = company_data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        chart_data.index = company_data['日期']
        
        # 創建未來日期
        last_date = chart_data.index[-1]
        future_dates = []
        for period_name, days in config.prediction_periods.items():
            period_dates = [last_date + timedelta(days=i+1) for i in range(days)]
            future_dates.extend(period_dates)
        
        # 添加預測數據到圖表
        addplots = []
        colors = ['red', 'blue', 'green']
        
        for i, (period_name, days) in enumerate(config.prediction_periods.items()):
            if period_name in predictions and predictions[period_name] is not None:
                # 創建預測數據
                pred_dates = [last_date + timedelta(days=j+1) for j in range(days)]
                pred_values = predictions[period_name][:days]
                
                if len(pred_values) == len(pred_dates):
                    pred_df = pd.DataFrame({
                        'Close': pred_values
                    }, index=pred_dates)
                    
                    # 添加到圖表
                    addplots.append(mpf.make_addplot(
                        pred_df['Close'],
                        color=colors[i % len(colors)],
                        width=2,
                        label=f'{period_name.capitalize()} ({days}天)'
                    ))
        
        # 創建圖表
        filename = f"{config.output_dir}/{company_name}_{code}_enhanced_kline.png"
        
        # 設定圖表樣式
        style = mpf.make_mpf_style(
            base_mpf_style='yahoo',
            volume=True,
            addplot_config=dict(
                legend=True,
                legend_loc='upper left'
            )
        )
        
        # 繪製圖表
        mpf.plot(
            chart_data,
            type='candle',
            addplot=addplots,
            title=f'{company_name} ({code}) - 增強版預測圖表',
            ylabel='價格 (TWD)',
            volume=True,
            style=style,
            savefig=filename,
            figsize=(15, 10),
            dpi=300
        )
        
        logger.info(f"✅ 增強版圖表已生成: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"圖表生成失敗: {e}")
        return None

# ========== 主要預測流程 ==========
def predict_company_stock(company_name, code, company_data, config):
    """為單一公司進行預測"""
    logger.info(f"開始預測 {company_name} ({code}) 的股價")
    
    try:
        # 按日期排序
        company_data = company_data.sort_values('日期')
        
        if len(company_data) < 100:  # 數據不足
            logger.warning(f"{company_name} 數據不足，跳過預測")
            return None
        
        predictions = {}
        
        # 為每個預測時間區間訓練模型
        for period_name, prediction_steps in config.prediction_periods.items():
            window_size = config.window_sizes[period_name]
            
            logger.info(f"訓練 {period_name} 期預測模型 (預測 {prediction_steps} 天)")
            
            # 訓練模型
            model, scaler, history = train_prediction_model(
                company_data, window_size, prediction_steps, config
            )
            
            if model is not None and scaler is not None:
                # 準備最後的序列進行預測
                last_sequence = company_data['Close'].tail(window_size).values
                last_sequence_scaled = scaler.transform(last_sequence.reshape(-1, 1)).flatten()
                
                # 預測未來價格
                future_prices = predict_future_prices(
                    model, scaler, last_sequence_scaled, prediction_steps
                )
                
                if future_prices is not None:
                    predictions[period_name] = future_prices
                    logger.info(f"{period_name} 期預測完成，預測 {len(future_prices)} 個值")
                else:
                    predictions[period_name] = None
                    logger.warning(f"{period_name} 期預測失敗")
            else:
                predictions[period_name] = None
                logger.warning(f"{period_name} 期模型訓練失敗")
        
        # 生成增強版圖表
        if any(pred is not None for pred in predictions.values()):
            chart_file = create_enhanced_chart(
                company_data, predictions, company_name, code, config
            )
            return chart_file
        else:
            logger.warning(f"{company_name} 所有預測都失敗")
            return None
            
    except Exception as e:
        logger.error(f"預測 {company_name} 時發生錯誤: {e}")
        return None

# ========== 主程序 ==========
def main():
    """主程序"""
    try:
        # 創建配置
        config = PredictionConfig()
        
        # 創建必要目錄
        os.makedirs(config.output_dir, exist_ok=True)
        os.makedirs(config.logs_dir, exist_ok=True)
        
        logger.info("🚀 開始執行增強版股票預測分析")
        logger.info(f"預測時間區間: {config.prediction_periods}")
        logger.info(f"模型參數: epochs={config.epochs}, batch_size={config.batch_size}")
        
        # 載入和準備數據
        raw_data = load_and_prepare_data(config)
        if raw_data.empty:
            logger.error("無法載入數據，程序終止")
            return
        
        # 清理數據
        clean_data = clean_stock_data(raw_data)
        if clean_data.empty:
            logger.error("數據清理後為空，程序終止")
            return
        
        # 按公司分組進行預測
        company_groups = clean_data.groupby(['Company', 'Code'])
        total_companies = len(company_groups)
        successful_predictions = 0
        
        logger.info(f"開始處理 {total_companies} 家公司")
        
        for (company_name, code), company_data in company_groups:
            try:
                result = predict_company_stock(company_name, code, company_data, config)
                if result:
                    successful_predictions += 1
                    
            except Exception as e:
                logger.error(f"處理公司 {company_name} ({code}) 時發生錯誤: {e}")
                continue
        
        # 總結報告
        logger.info("🎉 增強版預測分析完成！")
        logger.info(f"成功預測: {successful_predictions}/{total_companies} 家公司")
        logger.info(f"圖表儲存至: {config.output_dir}")
        
        # 生成預測報告
        generate_prediction_report(config, successful_predictions, total_companies)
        
    except Exception as e:
        logger.error(f"程序執行時發生嚴重錯誤: {e}")
        raise

def generate_prediction_report(config, successful, total):
    """生成預測報告"""
    try:
        report_file = f"{config.logs_dir}/prediction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("增強版股票預測分析報告\n")
            f.write("=" * 50 + "\n")
            f.write(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"預測時間區間: {config.prediction_periods}\n")
            f.write(f"成功預測: {successful}/{total} 家公司\n")
            f.write(f"成功率: {successful/total*100:.1f}%\n")
            f.write(f"輸出目錄: {config.output_dir}\n")
            f.write(f"日誌目錄: {config.logs_dir}\n")
        
        logger.info(f"預測報告已生成: {report_file}")
        
    except Exception as e:
        logger.error(f"生成報告失敗: {e}")

if __name__ == "__main__":
    main()

