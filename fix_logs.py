#!/usr/bin/env python3
"""
快速修復腳本：創建缺失的日誌目錄
"""

import os
import sys

def create_logs_directory():
    """創建缺失的日誌目錄"""
    logs_path = os.path.join('mysite', 'logs')
    
    try:
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)
            print(f"✅ 已創建日誌目錄: {logs_path}")
        else:
            print(f"✅ 日誌目錄已存在: {logs_path}")
        
        # 創建一個空的 app.log 文件
        log_file = os.path.join(logs_path, 'app.log')
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("# Django 應用日誌文件\n")
                f.write("# 創建時間: " + str(os.popen('date').read().strip()) + "\n")
            print(f"✅ 已創建日誌文件: {log_file}")
        else:
            print(f"✅ 日誌文件已存在: {log_file}")
            
        return True
        
    except Exception as e:
        print(f"❌ 創建日誌目錄時發生錯誤: {e}")
        return False

def main():
    print("🔧 開始修復日誌目錄問題...")
    
    if create_logs_directory():
        print("\n🎉 日誌目錄問題已修復！")
        print("現在可以正常運行 Django 應用程式了。")
    else:
        print("\n❌ 修復失敗，請檢查權限或手動創建目錄。")
        sys.exit(1)

if __name__ == "__main__":
    main()

