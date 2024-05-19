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
            while ',,' in line:
                line = line.replace(',,', ',')
            codes = line.replace("VolumeRank=", "").strip().split(',')
            cleaned_codes = [code.strip('"') for code in codes]
            X.extend(cleaned_codes)  # 將清理後的股票代碼添加到動態陣列X

# 檢查頁面內容
def check_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        content = response.content.decode('big5', 'ignore')
        if '檔案不存在' in content:
            log_message(f"'{url}' - 檔案不存在")
            return True
        else:
            log_message(f"'{url}' - 檔案存在")
            return False
    except requests.RequestException as e:
        log_message(f"訪問 '{url}' 時發生錯誤: {e}")
        return False

# 寫入日誌檔案
def log_message(message):
    with open(os.path.join(B, 'log.txt'), 'a', encoding='utf-8') as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

select_and_read_csv()

current_date = datetime.now().strftime('%Y/%m/%d')

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
            file.write(f'<h5><a href="{url_tpex}">證券櫃台買賣中心一般性資料網址（{i}）</a></h5>\n')
        else:
            file.write(f'<h5><a href="{url_twse}">公開資訊觀測站一般性資料網址（{i}）</a></h5>\n')
    file.write('</body></html>\n')

print(f"HTML 文件已生成：{file_name}")

# 使用webbrowser打開創建的HTML檔案
webbrowser.open_new_tab(file_name)
