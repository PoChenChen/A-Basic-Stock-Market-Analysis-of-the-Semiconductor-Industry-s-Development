#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析預測系統配置檢查腳本
檢查系統環境、依賴套件、數據文件等配置
"""

import os
import sys
import importlib
import pandas as pd
from pathlib import Path

def check_python_version():
    """檢查 Python 版本"""
    print("🐍 檢查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 版本過低: {version.major}.{version.minor}.{version.micro}")
        print("   需要 Python 3.8 或更高版本")
        return False

def check_dependencies():
    """檢查依賴套件"""
    print("\n📚 檢查依賴套件...")
    required_packages = [
        'django', 'pandas', 'numpy', 'matplotlib', 
        'mplfinance', 'sklearn', 'tensorflow'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少套件: {', '.join(missing_packages)}")
        print("請執行: pip install -r requirements.txt")
        return False
    return True

def check_directory_structure():
    """檢查目錄結構"""
    print("\n📁 檢查目錄結構...")
    required_dirs = [
        'mysite',
        'mysite/webapp',
        'mysite/templates',
        'mysite/STATIC',
        'mysite/data',
        'logs'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - 目錄不存在")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️ 缺少目錄: {', '.join(missing_dirs)}")
        return False
    return True

def check_data_files():
    """檢查數據文件"""
    print("\n📊 檢查數據文件...")
    data_dir = Path("mysite/data")
    
    if not data_dir.exists():
        print("❌ 數據目錄不存在")
        return False
    
    csv_files = list(data_dir.glob("TWSE_*_all_companies.csv"))
    if not csv_files:
        print("❌ 未找到 TWSE 數據文件")
        return False
    
    print(f"✅ 找到 {len(csv_files)} 個數據文件:")
    for file in csv_files:
        print(f"   - {file.name}")
    
    return True

def check_django_config():
    """檢查 Django 配置"""
    print("\n⚙️ 檢查 Django 配置...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.mysite.settings')
        import django
        django.setup()
        
        from django.conf import settings
        print("✅ Django 設定載入成功")
        print(f"   資料庫: {settings.DATABASES['default']['ENGINE']}")
        print(f"   靜態文件: {settings.STATIC_URL}")
        print(f"   調試模式: {settings.DEBUG}")
        
        return True
    except Exception as e:
        print(f"❌ Django 配置錯誤: {e}")
        return False

def check_models():
    """檢查數據模型"""
    print("\n🗄️ 檢查數據模型...")
    
    try:
        from mysite.webapp.models import Company, Industry
        
        company_count = Company.objects.count()
        industry_count = Industry.objects.count()
        
        print(f"✅ 公司數量: {company_count}")
        print(f"✅ 產業數量: {industry_count}")
        
        return True
    except Exception as e:
        print(f"❌ 數據模型檢查失敗: {e}")
        return False

def check_static_files():
    """檢查靜態文件"""
    print("\n🖼️ 檢查靜態文件...")
    
    static_dir = Path("mysite/STATIC")
    kline_dir = static_dir / "kline_output"
    
    if not static_dir.exists():
        print("❌ 靜態文件目錄不存在")
        return False
    
    if kline_dir.exists():
        kline_files = list(kline_dir.glob("*.png"))
        print(f"✅ K線圖文件: {len(kline_files)} 個")
    else:
        print("⚠️ K線圖目錄不存在")
    
    return True

def generate_report(results):
    """生成檢查報告"""
    print("\n" + "="*50)
    print("📋 配置檢查報告")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{check_name}: {status}")
    
    print(f"\n總體結果: {passed}/{total} 項檢查通過")
    
    if passed == total:
        print("🎉 所有檢查都通過！系統配置正確。")
    else:
        print("⚠️ 部分檢查失敗，請根據上述提示進行修正。")
    
    return passed == total

def main():
    """主函數"""
    print("🔍 股票分析預測系統配置檢查")
    print("="*50)
    
    results = {}
    
    # 執行各項檢查
    results["Python 版本"] = check_python_version()
    results["依賴套件"] = check_dependencies()
    results["目錄結構"] = check_directory_structure()
    results["數據文件"] = check_data_files()
    results["Django 配置"] = check_django_config()
    results["數據模型"] = check_models()
    results["靜態文件"] = check_static_files()
    
    # 生成報告
    success = generate_report(results)
    
    # 返回退出碼
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

