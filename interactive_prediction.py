#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
互動式股票預測配置界面
支援用戶自定義預測參數和時間區間
提供友好的命令行交互界面
"""

import os
import sys
import logging
import json
import pandas as pd
from datetime import datetime, timedelta
import argparse
from pathlib import Path

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/interactive_prediction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== 預測配置類 ==========
class InteractivePredictionConfig:
    def __init__(self):
        self.config_file = "prediction_config.json"
        self.default_config = {
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
                "save_predictions": True,
                "generate_report": True
            }
        }
        self.load_config()
    
    def load_config(self):
        """載入配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info("配置文件載入成功")
            else:
                self.config = self.default_config.copy()
                self.save_config()
                logger.info("創建新的默認配置文件")
        except Exception as e:
            logger.error(f"載入配置文件失敗: {e}")
            self.config = self.default_config.copy()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info("配置文件保存成功")
        except Exception as e:
            logger.error(f"保存配置文件失敗: {e}")
    
    def update_config(self, section, key, value):
        """更新配置"""
        try:
            if section in self.config:
                if key in self.config[section]:
                    self.config[section][key] = value
                    logger.info(f"配置更新: {section}.{key} = {value}")
                    return True
                else:
                    logger.warning(f"配置項 {section}.{key} 不存在")
                    return False
            else:
                logger.warning(f"配置節 {section} 不存在")
                return False
        except Exception as e:
            logger.error(f"更新配置失敗: {e}")
            return False

# ========== 互動式界面 ==========
class InteractiveInterface:
    def __init__(self, config):
        self.config = config
    
    def show_main_menu(self):
        """顯示主選單"""
        while True:
            print("\n" + "="*60)
            print("🎯 互動式股票預測配置系統")
            print("="*60)
            print("1. 📊 查看當前配置")
            print("2. ⚙️  修改預測參數")
            print("3. 🕐  設定預測時間區間")
            print("4. 🤖  調整模型參數")
            print("5. 💾  數據設定")
            print("6. 📈  輸出設定")
            print("7. 🚀  執行預測")
            print("8. 💾  保存配置")
            print("9. 🔄  重置為默認值")
            print("0. 🚪  退出")
            print("="*60)
            
            choice = input("請選擇操作 (0-9): ").strip()
            
            if choice == "1":
                self.show_current_config()
            elif choice == "2":
                self.modify_prediction_params()
            elif choice == "3":
                self.set_prediction_periods()
            elif choice == "4":
                self.adjust_model_params()
            elif choice == "5":
                self.configure_data_settings()
            elif choice == "6":
                self.configure_output_settings()
            elif choice == "7":
                self.execute_prediction()
            elif choice == "8":
                self.config.save_config()
                print("✅ 配置已保存")
            elif choice == "9":
                self.reset_to_default()
            elif choice == "0":
                print("👋 感謝使用，再見！")
                break
            else:
                print("❌ 無效選擇，請重新輸入")
    
    def show_current_config(self):
        """顯示當前配置"""
        print("\n📊 當前配置:")
        print("-" * 40)
        
        for section, settings in self.config.config.items():
            print(f"\n🔹 {section.upper()}:")
            for key, value in settings.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
    
    def modify_prediction_params(self):
        """修改預測參數"""
        print("\n⚙️ 修改預測參數")
        print("-" * 40)
        
        periods = self.config.config["prediction_periods"]
        print("當前預測時間區間:")
        for period, days in periods.items():
            print(f"  {period}: {days} 天")
        
        try:
            for period in periods.keys():
                new_value = input(f"請輸入 {period} 期預測天數 (當前: {periods[period]}): ").strip()
                if new_value:
                    new_days = int(new_value)
                    if new_days > 0:
                        self.config.update_config("prediction_periods", period, new_days)
                    else:
                        print("❌ 天數必須大於0")
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    def set_prediction_periods(self):
        """設定預測時間區間"""
        print("\n🕐 設定預測時間區間")
        print("-" * 40)
        
        print("可用的預測類型:")
        print("1. 短期預測 (1-14天)")
        print("2. 中期預測 (15-60天)")
        print("3. 長期預測 (61-180天)")
        print("4. 自定義預測")
        
        choice = input("請選擇預測類型 (1-4): ").strip()
        
        if choice == "1":
            self.set_short_term_prediction()
        elif choice == "2":
            self.set_medium_term_prediction()
        elif choice == "3":
            self.set_long_term_prediction()
        elif choice == "4":
            self.set_custom_prediction()
        else:
            print("❌ 無效選擇")
    
    def set_short_term_prediction(self):
        """設定短期預測"""
        print("\n📅 短期預測設定")
        print("-" * 40)
        
        try:
            days = int(input("請輸入預測天數 (1-14): ").strip())
            if 1 <= days <= 14:
                self.config.update_config("prediction_periods", "short", days)
                self.config.update_config("window_sizes", "short", max(10, days * 2))
                print("✅ 短期預測設定完成")
            else:
                print("❌ 天數必須在1-14之間")
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    def set_medium_term_prediction(self):
        """設定中期預測"""
        print("\n📅 中期預測設定")
        print("-" * 40)
        
        try:
            days = int(input("請輸入預測天數 (15-60): ").strip())
            if 15 <= days <= 60:
                self.config.update_config("prediction_periods", "medium", days)
                self.config.update_config("window_sizes", "medium", max(20, days))
                print("✅ 中期預測設定完成")
            else:
                print("❌ 天數必須在15-60之間")
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    def set_long_term_prediction(self):
        """設定長期預測"""
        print("\n📅 長期預測設定")
        print("-" * 40)
        
        try:
            days = int(input("請輸入預測天數 (61-180): ").strip())
            if 61 <= days <= 180:
                self.config.update_config("prediction_periods", "long", days)
                self.config.update_config("window_sizes", "long", max(40, days // 2))
                print("✅ 長期預測設定完成")
            else:
                print("❌ 天數必須在61-180之間")
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    def set_custom_prediction(self):
        """設定自定義預測"""
        print("\n📅 自定義預測設定")
        print("-" * 40)
        
        try:
            period_name = input("請輸入預測期間名稱 (如: custom): ").strip()
            if period_name:
                days = int(input("請輸入預測天數: ").strip())
                if days > 0:
                    self.config.config["prediction_periods"][period_name] = days
                    self.config.config["window_sizes"][period_name] = max(20, days // 2)
                    print(f"✅ 自定義預測 '{period_name}' 設定完成")
                else:
                    print("❌ 天數必須大於0")
            else:
                print("❌ 期間名稱不能為空")
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    def adjust_model_params(self):
        """調整模型參數"""
        print("\n🤖 調整模型參數")
        print("-" * 40)
        
        model_params = self.config.config["model_parameters"]
        print("當前模型參數:")
        for key, value in model_params.items():
            print(f"  {key}: {value}")
        
        try:
            epochs = input(f"請輸入訓練輪數 (當前: {model_params['epochs']}): ").strip()
            if epochs:
                self.config.update_config("model_parameters", "epochs", int(epochs))
            
            batch_size = input(f"請輸入批次大小 (當前: {model_params['batch_size']}): ").strip()
            if batch_size:
                self.config.update_config("model_parameters", "batch_size", int(batch_size))
            
            lr = input(f"請輸入學習率 (當前: {model_params['learning_rate']}): ").strip()
            if lr:
                self.config.update_config("model_parameters", "learning_rate", float(lr))
            
            print("✅ 模型參數調整完成")
            
        except ValueError:
            print("❌ 請輸入有效的數值")
    
    def configure_data_settings(self):
        """配置數據設定"""
        print("\n💾 數據設定")
        print("-" * 40)
        
        data_settings = self.config.config["data_settings"]
        print("當前數據設定:")
        for key, value in data_settings.items():
            print(f"  {key}: {value}")
        
        try:
            min_points = input(f"請輸入最小數據點數 (當前: {data_settings['min_data_points']}): ").strip()
            if min_points:
                self.config.update_config("data_settings", "min_data_points", int(min_points))
            
            split_ratio = input(f"請輸入訓練測試分割比例 (當前: {data_settings['train_test_split']}): ").strip()
            if split_ratio:
                ratio = float(split_ratio)
                if 0.5 <= ratio <= 0.9:
                    self.config.update_config("data_settings", "train_test_split", ratio)
                else:
                    print("❌ 分割比例必須在0.5-0.9之間")
            
            print("✅ 數據設定配置完成")
            
        except ValueError:
            print("❌ 請輸入有效的數值")
    
    def configure_output_settings(self):
        """配置輸出設定"""
        print("\n📈 輸出設定")
        print("-" * 40)
        
        output_settings = self.config.config["output_settings"]
        print("當前輸出設定:")
        for key, value in output_settings.items():
            print(f"  {key}: {value}")
        
        try:
            quality = input("請選擇圖表品質 (low/medium/high, 當前: {output_settings['chart_quality']}): ").strip().lower()
            if quality in ['low', 'medium', 'high']:
                self.config.update_config("output_settings", "chart_quality", quality)
            
            save_pred = input("是否保存預測結果? (y/n, 當前: {output_settings['save_predictions']}): ").strip().lower()
            if save_pred in ['y', 'yes']:
                self.config.update_config("output_settings", "save_predictions", True)
            elif save_pred in ['n', 'no']:
                self.config.update_config("output_settings", "save_predictions", False)
            
            gen_report = input("是否生成報告? (y/n, 當前: {output_settings['generate_report']}): ").strip().lower()
            if gen_report in ['y', 'yes']:
                self.config.update_config("output_settings", "generate_report", True)
            elif gen_report in ['n', 'no']:
                self.config.update_config("output_settings", "generate_report", False)
            
            print("✅ 輸出設定配置完成")
            
        except Exception as e:
            print(f"❌ 配置失敗: {e}")
    
    def execute_prediction(self):
        """執行預測"""
        print("\n🚀 執行預測")
        print("-" * 40)
        
        # 檢查增強版預測程序是否存在
        if not os.path.exists("enhanced_prediction.py"):
            print("❌ 增強版預測程序不存在，請先創建 enhanced_prediction.py")
            return
        
        # 確認執行
        confirm = input("確定要執行預測分析嗎? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            try:
                print("🚀 開始執行預測...")
                
                # 執行預測程序
                import subprocess
                result = subprocess.run([
                    sys.executable, "enhanced_prediction.py"
                ], capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode == 0:
                    print("✅ 預測執行成功！")
                    if result.stdout:
                        print("輸出信息:")
                        print(result.stdout)
                else:
                    print("❌ 預測執行失敗")
                    if result.stderr:
                        print("錯誤信息:")
                        print(result.stderr)
                        
            except Exception as e:
                print(f"❌ 執行預測時發生錯誤: {e}")
        else:
            print("❌ 取消執行")
    
    def reset_to_default(self):
        """重置為默認值"""
        print("\n🔄 重置為默認值")
        print("-" * 40)
        
        confirm = input("確定要重置所有配置為默認值嗎? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            self.config.config = self.config.default_config.copy()
            self.config.save_config()
            print("✅ 配置已重置為默認值")
        else:
            print("❌ 取消重置")

# ========== 命令行參數解析 ==========
def parse_arguments():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description="互動式股票預測配置系統")
    parser.add_argument("--config", "-c", help="配置文件路徑")
    parser.add_argument("--show", "-s", action="store_true", help="顯示當前配置")
    parser.add_argument("--execute", "-e", action="store_true", help="直接執行預測")
    parser.add_argument("--reset", "-r", action="store_true", help="重置為默認配置")
    
    return parser.parse_args()

# ========== 主程序 ==========
def main():
    """主程序"""
    try:
        # 解析命令行參數
        args = parse_arguments()
        
        # 創建配置對象
        config = InteractivePredictionConfig()
        
        # 處理命令行參數
        if args.show:
            # 顯示配置
            print("📊 當前配置:")
            print(json.dumps(config.config, indent=2, ensure_ascii=False))
            return
        
        if args.reset:
            # 重置配置
            config.config = config.default_config.copy()
            config.save_config()
            print("✅ 配置已重置為默認值")
            return
        
        if args.execute:
            # 直接執行預測
            if os.path.exists("enhanced_prediction.py"):
                print("🚀 直接執行預測...")
                import subprocess
                subprocess.run([sys.executable, "enhanced_prediction.py"])
            else:
                print("❌ 增強版預測程序不存在")
            return
        
        # 啟動互動式界面
        interface = InteractiveInterface(config)
        interface.show_main_menu()
        
    except KeyboardInterrupt:
        print("\n👋 程序被用戶中斷")
    except Exception as e:
        logger.error(f"程序執行時發生錯誤: {e}")
        print(f"❌ 程序執行失敗: {e}")

if __name__ == "__main__":
    main()

