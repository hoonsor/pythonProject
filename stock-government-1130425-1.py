import os
import requests
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# 設定儲存HTML檔案的路徑
B = 'D:\\截圖\\'  # 請填寫你的路徑

# 動態陣列X，用於儲存股票代碼
X = []

# 選擇CSV檔案並讀取股票代碼
def select_and_read_csv():
    root = tk.Tk()
    root.withdraw()  # 不顯示tkinter主視窗
    file_path = filedialog.askopenfilename(title="選擇股票代碼CSV檔案", filetypes=[("CSV files", "*.csv")])
    if file_path:  # 確認選擇了檔案
        with open(file_path, 'r') as file:
            line = file.readline()
            # 循环替换所有连续的逗号为单个逗号
            while ',,' in line:
                line = line.replace(',,', ',')
            # 移除"VolumeRank="，並將剩餘部分以逗號分隔後轉換為列表
            codes = line.replace("VolumeRank=", "").strip().split(',')
            # 清理每個代碼的前後雙引號
            cleaned_codes = [code.strip('"') for code in codes]
            X.extend(cleaned_codes)  # 將清理後的股票代碼添加到動態陣列X

def check_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        # 使用 Big5 解碼響應內容
        content = response.content.decode('big5', 'ignore')
        if '檔案不存在' in content:
            return True  # 網頁內容包含「檔案不存在」
        else:
            return False
    except requests.RequestException:
        return False  # 網絡請求失敗，預設為不包含「檔案不存在」

select_and_read_csv()

# 取得本地西元日期並格式化
current_date = datetime.now().strftime('%Y/%m/%d')

# 創建HTML檔案
file_name = os.path.join(B, f'Stock_Links_{datetime.now().strftime("%Y%m%d")}.html')
with open(file_name, 'w', encoding='utf-8') as file:
    file.write('<html><head><title>股票代碼超連結</title></head><body>\n')
    file.write(f'<h4>更新日期：{current_date}</h4>\n')
    file.write('<h5>※以下資料為免費公開資訊觀測站一般性資料整理。</h5>\n')
    file.write('<h5>僅供學員練習使用，請自行學習練習判斷。</h5>\n')
    for i in X:
        url_twse = f"https://mops.twse.com.tw/server-java/t164sb01?step=1&CO_ID={i}&SYEAR=2023&SSEASON=4&REPORT_ID=C"
        if check_page_content(url_twse):
            url_tpex = f"https://www.tpex.org.tw/web/regular_emerging/corporateInfo/regular/regular_stock_detail.php?l=zh-tw&stk_code={i}"
            file.write(f'<h5><a href="{url_tpex}">證券櫃台買賣中心一般性資料網址（{i}）</a></h5>\n')  # 設定大一點的字型
        else:
            file.write(f'<h5><a href="{url_twse}">公開資訊觀測站一般性資料網址（{i}）</a></h5>\n')  # 設定大一點的字型
    file.write('</body></html>\n')

print(f"HTML 文件已生成：{file_name}")

# 使用webbrowser打開創建的HTML檔案
webbrowser.open_new_tab(file_name)
