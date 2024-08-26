import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# 啟動 TK 介面來選擇文件
root = tk.Tk()
root.withdraw()  # 用來隱藏主視窗

# 選擇輸入檔案
file_path = filedialog.askopenfilename(title='選擇轉換前的Excel檔案或CSV檔案')
if not file_path:
    print("未選擇檔案，程式結束。")
    exit()

# 根據檔案類型讀取數據
try:
    file_extension = os.path.splitext(file_path)[1]
    if file_extension in ['.xls', '.xlsx']:
        data = pd.read_excel(file_path)
    elif file_extension == '.csv':
        data = pd.read_csv(file_path)
    else:
        raise ValueError("不支持的檔案類型")
except Exception as e:
    print(f"讀取文件失敗: {e}")
    exit()

# 確保日期格式正確
data['date'] = pd.to_datetime(data['date'])

# 將數據按日期排序
data.sort_values('date', ascending=True, inplace=True)

# 計算每週的數據
weekly_data = []
for _, week in data.groupby(data['date'].dt.to_period('W-MON')):
    if week.empty:
        continue

    # 從星期一到星期五的數據，如果星期一獨立則單獨作為一筆
    if len(week) == 1 and week.iloc[0]['date'].dayofweek == 0:  # 星期一獨立一天
        week_data = {
            'date': week.iloc[0]['date'].strftime('%Y/%m/%d'),
            'volume': week.iloc[0]['volume'],
            'open': week.iloc[0]['open'],
            'high': week.iloc[0]['high'],
            'low': week.iloc[0]['low'],
            'close': week.iloc[0]['close']
        }
    else:
        week_data = {
            'date': week.iloc[0]['date'].strftime('%Y/%m/%d'),  # 星期一的日期
            'volume': week['volume'].sum(),
            'open': week.iloc[0]['open'],  # 周一的開盤價
            'high': week['high'].max(),
            'low': week['low'].min(),
            'close': week.iloc[-1]['close']  # 最後一個交易日的收盤價
        }
    weekly_data.append(week_data)

# 轉換為 DataFrame 並排序
weekly_df = pd.DataFrame(weekly_data)
weekly_df['date'] = pd.to_datetime(weekly_df['date'])
weekly_df.sort_values('date', ascending=False, inplace=True)  # 最新的日期在前

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
