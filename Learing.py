import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from datetime import datetime

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== 參數 ==========
data_dir = "mysite/data"
years = range(2020, 2026)  # 修正為包含民國114年(西元2025年)
window = 30
epochs = 10
batch_size = 16
output_dir = "mysite/STATIC/kline_output"
os.makedirs(output_dir, exist_ok=True)

# ========== 函式區塊 ==========

def load_all_years(data_dir, years):
    df_all = []
    for year in years:
        file = os.path.join(data_dir, f"TWSE_{year}_all_companies.csv")
        if os.path.exists(file):
            try:
                df = pd.read_csv(file)
                df_all.append(df)
                logger.info(f"成功載入 {year} 年數據，共 {len(df)} 筆記錄")
            except Exception as e:
                logger.error(f"載入 {year} 年數據時發生錯誤: {e}")
        else:
            logger.warning(f"檔案不存在：{file}")
    
    if not df_all:
        logger.error("沒有找到任何數據文件")
        return pd.DataFrame()
    
    return pd.concat(df_all, ignore_index=True)

def safe_parse_date(d):
    try:
        parts = str(d).split('/')
        year = int(parts[0])
        if year < 1911:
            year += 1911
        return f"{year}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
    except:
        return None

def clean_number_column(df, col):
    return (
        df[col].astype(str)
        .str.replace(',', '', regex=False)
        .replace('--', np.nan)
        .str.extract(r'([\d\.]+)')
        .astype(float)
    )

def clean_and_prepare(df):
    df.columns = df.columns.str.strip()
    df.dropna(subset=['公司名稱'], inplace=True)
    df['日期'] = df['日期'].astype(str).apply(safe_parse_date)
    df = df.dropna(subset=['日期'])
    df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d')

    for col in ['成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價']:
        df[col] = clean_number_column(df, col)

    df.dropna(subset=['開盤價', '最高價', '最低價', '收盤價'], inplace=True)
    df.rename(columns={
        '開盤價': 'Open',
        '最高價': 'High',
        '最低價': 'Low',
        '收盤價': 'Close',
        '公司名稱': 'Company',
        '股票代碼': 'Code'
    }, inplace=True)
    return df

def create_sequences(data, window):
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i:i + window])
        y.append(data[i + window])
    return np.array(X), np.array(y)

def train_lstm_model(X_train, y_train, window, epochs, batch_size):
    model = Sequential([
        LSTM(64, input_shape=(window, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)
    return model

def predict_and_plot(company, code, group, window, epochs, batch_size, output_dir):
    group = group.sort_values('日期')
    group.set_index('日期', inplace=True)
    prices = group[['Open', 'High', 'Low', 'Close']].copy()

    if len(prices) <= window + 10:
        print(f"⏭️ {company} 資料太少，跳過")
        return

    scaler = MinMaxScaler()
    scaled_close = scaler.fit_transform(prices[['Close']])
    X, y = create_sequences(scaled_close, window)
    if len(X) == 0:
        print(f"⏭️ {company} 序列製作失敗")
        return

    split = int(len(X) * 0.8)
    X_train, y_train = X[:split], y[:split]
    X_test, y_test = X[split:], y[split:]

    X_train = X_train.reshape((-1, window, 1))
    X_test = X_test.reshape((-1, window, 1))

    model = train_lstm_model(X_train, y_train, window, epochs, batch_size)
    pred_scaled = model.predict(X_test, verbose=0)
    pred = scaler.inverse_transform(pred_scaled)
    true = scaler.inverse_transform(y_test)

    pred_index = prices.index[split + window:]
    pred_df = pd.DataFrame({'收盤價': true.flatten(), '預測價': pred.flatten()}, index=pred_index)

    plot_data = prices.copy()
    plot_data.loc[pred_df.index, '預測價'] = pred_df['預測價']

    apds = [mpf.make_addplot(plot_data['預測價'], color='red')]
    filename = f"{output_dir}/{company}_{code}_kline.png"
    mpf.plot(prices,
             type='candle',
             addplot=apds,
             title=f'Predicted closing price',
             ylabel='Price',
             style='yahoo',
             volume=False,
             savefig=filename)
    print(f"✅ 已完成圖表：{company}({code})")

if __name__ == "__main__":
    try:
        # 創建必要的目錄
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        logger.info("開始執行股票預測分析")
        logger.info(f"參數設定: window={window}, epochs={epochs}, batch_size={batch_size}")
        
        df = load_all_years(data_dir, years)
        if df.empty:
            logger.error("無法載入數據，程序終止")
            exit(1)
            
        df = clean_and_prepare(df)
        logger.info(f"數據清理完成，共 {len(df)} 筆記錄")
        
        company_count = 0
        for (company, code), group in df.groupby(['Company', 'Code']):
            try:
                predict_and_plot(company, code, group, window, epochs, batch_size, output_dir)
                company_count += 1
            except Exception as e:
                logger.error(f"處理公司 {company}({code}) 時發生錯誤: {e}")
                continue
        
        logger.info(f"🎉 完成！共處理 {company_count} 家公司，圖表儲存至：{output_dir}")
        
    except Exception as e:
        logger.error(f"程序執行時發生嚴重錯誤: {e}")
        exit(1)