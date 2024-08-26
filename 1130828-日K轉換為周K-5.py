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
group_details = []
for _, week in data.groupby(data['date'].dt.isocalendar().week):
    if week.empty:
        continue

    # 獲取週內所有日期和對應的星期幾
    week_info = week['date'].apply(lambda x: (x.strftime('%Y-%m-%d'), x.strftime('%A')))
    group_details.append(list(week_info))

# 將分組信息轉換為 DataFrame
group_df = pd.DataFrame(group_details)

# 輸出週分組信息
group_df.to_csv('group_details.csv', index=False, header=False)

print("分組信息已輸出至 'group_details.csv'。")
