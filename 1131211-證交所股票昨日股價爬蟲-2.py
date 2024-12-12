"""

本程式碼使用之API方式參考 https://vocus.cc/article/667ebabbfd897800016b3086 網頁撰寫，如果想要獲取更多資訊可查看上述網頁

本程式會在執行後去證交所使用API抓取所有股票代號昨日之收盤股價
並且輸出為xlsx檔案，跳出視窗讓使用者選擇儲存位置
輸出的檔案共有3欄，第1欄為股票代號、第2欄為股票名稱、第3欄為昨日收盤價

"""


# 引入requests庫
import requests
# 引入json庫
import json
# 引入pandas庫
import pandas as pd
# 引入tkinter的filedialog來選擇儲存檔案的路徑
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

# 定義API的URL
url = 'https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL'
# 發送GET請求
res = requests.get(url)

# 檢查返回狀態
if res.status_code == 200:
    print("Request successful!")
else:
    print("Request failed!")

# 解析JSON數據
jsondata = json.loads(res.text)

# 將JSON數據轉換為DataFrame
df = pd.DataFrame(jsondata)

# 將"Code"列設置為索引
df.set_index("Code", inplace=True)

# 將空字符串替換為'0'
df.replace('', '0', inplace=True)

# 將"Code"欄位轉換為字符串格式，以保留前置零
df.index = df.index.astype(str)

# 將除了"Name"列以外的所有列轉換為浮點數
df[df.columns.difference(['Name'])] = df[df.columns.difference(['Name'])].astype(float)

# 顯示DataFrame
print(df)

# 只保留第1欄和第7欄（索引 0 和 6）
df_filtered = df.iloc[:, [0, 6]]

# 使用tkinter的asksaveasfilename來讓使用者選擇儲存Excel檔案的位置
Tk().withdraw()  # 不顯示主視窗
file_path = asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], title="Save Excel file")

# 如果使用者選擇了路徑，則保存為Excel
if file_path:
    # 使用ExcelWriter並設置欄位格式
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, sheet_name='Sheet1', index=True)

        # 獲取xlsxwriter物件
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # 設定'Code'欄位格式為文本
        text_format = workbook.add_format({'num_format': '@'})
        worksheet.set_column('A:A', 15, text_format)  # 調整A欄的寬度及格式
        # 設定其餘欄位為自動格式（保持數字格式）
        worksheet.set_column('B:B', 15)  # 調整B欄的寬度

    print(f"File saved to: {file_path}")
else:
    print("No file selected.")
