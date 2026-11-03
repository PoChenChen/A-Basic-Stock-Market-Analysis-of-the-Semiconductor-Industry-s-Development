import pandas as pd
import os

# 設定來源資料夾
data_dir = "mysite/data"
summary_list = []

# 讀取每年資料並彙總
for year in range(2020, 2025):
    file = os.path.join(data_dir, f"TWSE_{year}_all_companies.csv")
    if not os.path.exists(file):
        print(f"⚠️ {year} 資料不存在")
        continue

    df = pd.read_csv(file)

    # 整理成交資訊（去除逗號並轉為數字）
    df["收盤價"] = pd.to_numeric(df["收盤價"].astype(str).str.replace(",", ""), errors='coerce')
    df["成交股數"] = pd.to_numeric(df["成交股數"].astype(str).str.replace(",", ""), errors='coerce')
    df["成交金額"] = pd.to_numeric(df["成交金額"].astype(str).str.replace(",", ""), errors='coerce')

    # 彙總：年度總成交量、總成交金額、平均收盤價
    summary = df.groupby(["公司名稱", "股票代碼"]).agg({
        "成交股數": "sum",
        "成交金額": "sum",
        "收盤價": "mean"
    }).reset_index()

    summary["年度"] = year
    summary = summary.rename(columns={"收盤價": "平均收盤價", "成交股數": "總成交股數", "成交金額": "總成交金額"})

    summary_list.append(summary)

# 合併所有年份
df_summary = pd.concat(summary_list, ignore_index=True)

# 儲存
df_summary.to_csv("TWSE_年度統計_含EPS.csv", index=False, encoding="utf-8-sig")
print("✅ 已儲存年度統計彙總表：TWSE_年度統計_含EPS.csv")