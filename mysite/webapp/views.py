import os
import logging
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.core.exceptions import ValidationError
from .models import Company, Industry, StockPrice

# 配置日誌
logger = logging.getLogger(__name__)


def index(request):
    # 取得「半導體」關鍵字的相關產業（可視情況調整名稱比對）
    semiconductor_industries = Industry.objects.filter(name__icontains='半導體')

    # 篩選 2023 年，屬於半導體相關產業的公司
    companies = Company.objects.filter(
        industry__in=semiconductor_industries,
        year=2023
    ).order_by('rank')

    # 假設你預寫好一段文字分析，今年的股市（可存在資料庫、Markdown 或手動撰寫）
    stock_summary_2025 = """
    2025年台灣股市在AI與半導體擴張帶動下持續成長，加權指數突破20,000點，
    半導體族群尤其強勁，台積電與IC設計股獲外資青睞，預期下半年仍具動能。
    """

    context = {
        'companies': companies,
        'stock_summary': stock_summary_2025.strip(),
    }
    return render(request, 'index.html', context)

def industry_detail(request, pk):
    industry = get_object_or_404(Industry, pk=pk)

    # 分成台灣與國外公司（可根據你的 country 欄位做調整）
    taiwan_companies = Company.objects.filter(industry=industry, country="台灣").order_by('rank')
    global_companies = Company.objects.exclude(country="台灣").filter(industry=industry).order_by('country', 'rank')

    return render(request, 'industry_detail.html', {
        'industry': industry,
        'taiwan_companies': taiwan_companies,
        'global_companies': global_companies,
    })

def industry_detail_by_name(request, name):
    # 產業名稱可能含有URL編碼，保險起見處理一次（可選）
    from urllib.parse import unquote
    name = unquote(name)

    # 忽略大小寫比對產業名稱
    industry = get_object_or_404(Industry, name__iexact=name)

    companies = Company.objects.filter(industry=industry).order_by('rank')

    context = {
        'industry': industry,
        'companies': companies,
    }
    return render(request, 'industry_detail.html', context)

def company_list(request):
    query = request.GET.get('q', '')
    # industry_filter = request.GET.get('industry')
    year_filter = request.GET.get('year')

    companies = Company.objects.all()

    # 搜尋
    if query:
        companies = companies.filter(Q(name__icontains=query) | Q(symbol__icontains=query))

    # 產業篩選
    industry_filter = request.GET.get('industry')
    try:
        industry_filter = int(industry_filter)
        companies = companies.filter(industry_id=industry_filter)
    except (ValueError, TypeError):
        industry_filter = None  # 無效值就不篩選

    # 年度篩選
    if year_filter:
        companies = companies.filter(year=year_filter)

    # 分頁
    paginator = Paginator(companies.order_by('rank'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    industries = Industry.objects.all()
    years = Company.objects.values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'page_obj': page_obj,
        'query': query,
        'industry_filter': industry_filter,
        'year_filter': year_filter,
        'industries': industries,
        'years': years,
    }
    return render(request, 'company_list.html', context)

def company_detail(request, pk):
    try:
        company = get_object_or_404(Company, pk=pk)
        logger.info(f"查看公司詳細資訊: {company.name} ({company.symbol})")

        # K 線圖路徑
        kline_filename = f"{company.name}_{company.symbol}_kline.png"
        kline_img_path = f'kline_output/{company.name}_{company.symbol}_kline.png'

        # 讀取最新年份的股價數據（包含民國114年/西元2025年）
        recent_prices = []
        data_dir = 'data'
        
        # 從最新年份開始讀取，確保包含民國114年的數據
        years_to_check = [2025, 2024, 2023, 2022, 2021, 2020]  # 優先讀取最新年份
        
        for year in years_to_check:
            csv_path = os.path.join(data_dir, f'TWSE_{year}_all_companies.csv')
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path)
                    if '股票代碼' in df.columns:
                        company_data = df[df['股票代碼'].astype(str) == str(company.symbol)]
                        if not company_data.empty:
                            # 按日期排序，取最新的5筆數據
                            company_data = company_data.sort_values(by='日期', ascending=False).head(5)
                            
                            for _, row in company_data.iterrows():
                                recent_prices.append({
                                    'date': row['日期'],
                                    'open': row['開盤價'],
                                    'close': row['收盤價'],
                                    'high': row['最高價'],
                                    'low': row['最低價'],
                                    'volume': row['成交股數'],
                                })
                            
                            logger.info(f"成功讀取 {company.name} 的 {year} 年股價數據，共 {len(recent_prices)} 筆")
                            # 如果找到數據，就跳出循環
                            break
                except Exception as e:
                    logger.error(f"讀取 {csv_path} 時發生錯誤: {e}")
                    continue
        
        if not recent_prices:
            logger.warning(f"未找到 {company.name} 的股價數據")

        context = {
            'company': company,
            'kline_img_path': kline_img_path,
            'stock_prices': recent_prices,
            'industry': company.industry,
        }
        return render(request, 'company_detail.html', context)
        
    except Exception as e:
        logger.error(f"查看公司詳細資訊時發生錯誤: {e}")
        raise Http404("無法載入公司資訊")