import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from io import StringIO

def get_data(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        tables = []
        titles = []

        for table in soup.find_all('table'):
            title_tag = None
            for prev in table.find_all_previous():
                if prev.name in ['strong', 'h2', 'h3'] and prev.get_text(strip=True):
                    title_tag = prev
                    break
            title = title_tag.get_text(strip=True) if title_tag else "無標題"

            # 讀取表格
            df = pd.read_html(StringIO(str(table)))[0]

            # 插入來源標題為第一列
            empty_row = [''] * df.shape[1]
            df.loc[-1] = empty_row  # 新增一空白列
            df.index = df.index + 1  # 所有 index +1
            df = df.sort_index()  # 重新排序
            df.iloc[0, 0] = title  # 第一列第一欄放標題文字

            tables.append(df)
            titles.append(title)

        print(f"{url} 共取得 {len(tables)} 個表格")
        return tables, titles

    except Exception as e:
        print(f"抓取表格錯誤({url}) :", e)
        return [], []


def save_merged_table(table, name):
    filename = f"{name}_merged.csv"
    table.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"💾 合併表格已儲存：{filename}")

if __name__ == '__main__':
    urls = {
        'ic_packaging': 'https://www.sipo.org.tw/industry-overview/industry-ranking/item/4033-ic-packaging-and-testing-industry-ranking.html',
        'ic_design': 'https://www.sipo.org.tw/industry-overview/industry-ranking/item/4032-ic-design-industry-ranking.html',
        'ic_foundry': 'https://www.sipo.org.tw/industry-overview/industry-ranking/item/4031-ic-foundry-industry-ranking.html',
        'semiconductor': 'https://www.sipo.org.tw/industry-overview/industry-ranking/item/4030-semiconductor-industry-ranking.html'
    }

    all_merged = []

    for name, url in urls.items():
        print(f"\n==== 產業類別：{name} ====")
        tables, titles = get_data(url)

        if tables:
            merged = pd.concat(tables, ignore_index=True)
            merged['產業類別'] = name
            save_merged_table(merged, name)
            all_merged.append(merged)
        else:
            print(f" {name} 沒有抓到任何表格")

    # 所有產業的總表
    if all_merged:
        final_df = pd.concat(all_merged, ignore_index=True)
        final_df.to_csv("all_industry_merged.csv", index=False, encoding='utf-8-sig')
        print("所有產業表格已整合並儲存為 all_industry_merged.csv")
