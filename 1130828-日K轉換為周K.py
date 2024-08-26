import pandas as pd
import numpy as np
from datetime import timedelta
import tkinter as tk
from tkinter import filedialog

# 啟動 TK 介面來選擇文件
root = tk.Tk()
root.withdraw()  # 用來隱藏主視窗

# 選擇輸入檔案
file_path = filedialog.askopenfilename(title='選擇轉換前的Excel檔案')
if not file_path:
    print("未選擇檔案，程式結束。")
    exit()

# 讀取 Excel 文件
try:
    data = pd.read_excel(file_path)
except Exception as e:
    print(f"讀取文件失敗: {e}")
    exit()

# 確保日期格式正確
data['日期'] = pd.to_datetime(data['日期'])

# 將數據按日期排序
data.sort_values('日期', ascending=False, inplace=True)

# 計算每週的數據
weekly_data = []
for name, week in data.groupby(pd.Grouper(key='日期', freq='W-MON')):
    if week.empty:
        continue

    week_data = {
        '日期': name.strftime('%Y/%m/%d'),  # 使用星期一的日期
        '成交量': week['成交量'].sum(),
        '開盤價': week.iloc[0]['開盤價'],  # 周一的開盤價
        '最高價': week['最高價'].max(),
        '最低價': week['最低價'].min(),
        '收盤價': week.iloc[-1]['收盤價']  # 周五或最後一個交易日的收盤價
    }
    weekly_data.append(week_data)

# 轉換為 DataFrame
weekly_df = pd.DataFrame(weekly_data)

# 讓使用者選擇儲存位置
save_path = filedialog.asksaveasfilename(title='另存新檔', defaultextension=".xlsx")
if not save_path:
    print("未選擇儲存位置，程式結束。")
    exit()

# 寫入 Excel 文件
try:
    weekly_df.to_excel(save_path, index=False)
    print("檔案已儲存至：", save_path)
except Exception as e:
    print(f"寫入文件失敗: {e}")
