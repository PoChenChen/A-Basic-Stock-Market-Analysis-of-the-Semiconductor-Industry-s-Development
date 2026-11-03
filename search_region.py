import re
import requests
import pandas as pd
import json
import time
from urllib.parse import quote


# 依公司名稱查詢股票資訊
def get_company_info(company_name):
    company_name = company_name.strip()
    if not company_name:
        print("⚠️ 空的公司名稱，略過")
        return None

    encoded_name = quote(company_name)  # 例如「輝達」→ %E8%BC%9D%E9%81%94
    url = f"https://tw.stock.yahoo.com/_td-stock/api/resource/SearchService;searchTerm={encoded_name}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ HTTP 錯誤 {response.status_code}：{company_name}")
            return None

        results = response.json()
        for item in results.get("items", []):
            if item.get("type") == "EQUITY":
                return {
                    "symbol": item.get("symbol"),
                    "exchange": item.get("exchange"),
                    "longName": item.get("longName"),
                    "shortName": item.get("shortName")
                }

        print(f"⚠️ 找不到股票資料：{company_name}")
        return None

    except Exception as e:
        print(f"❌ 查詢錯誤：{company_name} => {e}")
        return None

# 主流程：讀CSV → 查詢 → 儲存JSON
def process_csv_and_save_json(csv_file_path, output_json_path):
    df = pd.read_csv(csv_file_path)
    company_column = df.columns[1]  # 假設第一欄是公司名稱
    companies = df[company_column].dropna().unique()

    results = {}
    for name in companies:
        print(f"🔍 查詢公司：{name}")
        info = get_company_info(name)
        if info:
            results[name] = info
        else:
            results[name] = {"error": "查無資料"}
        time.sleep(1)  # 防止封鎖

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 已儲存至 {output_json_path}")

# ✅ 範例執行（請替換檔名）
if __name__ == "__main__":
    process_csv_and_save_json("all_industry_data.csv", "company_info.json")
