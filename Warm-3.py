import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
import os
import csv
import logging
import sys
from logging.handlers import RotatingFileHandler

# 設置日誌
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('ptt_crawler.log', maxBytes=10000, backupCount=1, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# 獲取當前執行檔的目錄
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(__file__)

# 讀取config.csv來獲取line_notify_token
config_path = os.path.join(application_path, 'config.csv')
try:
    with open(config_path, mode='r', encoding='big5') as infile:
        reader = csv.reader(infile)
        config = list(reader)
        line_notify_token = config[0][0]
    logging.info('設定檔載入成功')
except Exception as e:
    logging.error(f'無法載入設定檔: {e}')
    messagebox.showerror("錯誤", f"無法載入設定檔: {e}")
    sys.exit(1)

# 設置csv_path和output_path
csv_path = os.path.join(application_path, 'ptt爬蟲.csv')
output_path = os.path.join(application_path, 'ptt_output.txt')

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PTT爬蟲推播訊息')
        self.withdraw()
        logging.info("啟動主迴圈...")
        run_main_loop()


def send_line_notify(notification_message, token):
    logging.info("發送Line通知...")
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': notification_message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data)
    if response.status_code == 200:
        logging.info('Line通知發送成功')
    else:
        logging.error('Line通知發送失敗')
        messagebox.showerror("錯誤", "發送Line通知失敗，請檢查Token是否正確")
        exit()

def PreviousPage(url):
    logging.info(f"獲取上一頁連結: {url}")
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    prev_link_tag = soup.find('a', string='‹ 上頁')
    if prev_link_tag:
        logging.info("找到上一頁連結")
        return 'https://www.ptt.cc' + prev_link_tag['href']
    else:
        logging.info("未找到上一頁連結")
        return None

def run_main_loop():
    previous_day = None
    while True:
        today = (datetime.now()).strftime("%m/%d").lstrip("0")
        if today != previous_day:
            logging.info(f"搜索的日期是：{today}")
            previous_day = today
            open(output_path, 'w').close()
            logging.info(f"已清空{output_path}內容")
        try:
            df = pd.read_csv(csv_path, encoding='big5')
            logging.info("CSV檔讀取成功")
        except Exception as e:
            logging.error(f"讀取csv檔失敗: {e}")
            messagebox.showerror("錯誤", f"讀取csv檔失敗: {e}")
            send_line_notify(f"讀取csv檔失敗: {e}", line_notify_token)
            exit()

        existing_posts = get_existing_posts(output_path)

        for index, row in df.iterrows():
            board_name = row['板名']
            keyword1 = row['關鍵字1']
            keyword2 = row['關鍵字2'] if '關鍵字2' in row and not pd.isnull(row['關鍵字2']) else None
            url = f'https://www.ptt.cc/bbs/{board_name}/index.html'
            logging.info(f"處理版面: {board_name}")

            while url:
                logging.info(f"訪問頁面: {url}")
                try:
                    posts, page_has_posts = search_page(url, keyword1, keyword2, today)
                except requests.exceptions.RequestException as e:
                    logging.error("請求異常，可能是訪問過於頻繁")
                    print("過於頻繁的訪問，IP被封鎖，請隔一段時間後再執行程式")
                    send_line_notify("過於頻繁的訪問，IP被封鎖，請隔一段時間後再執行程式", line_notify_token)
                    exit()

                new_posts = [post for post in posts if post not in existing_posts]

                if new_posts:
                    message = f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ".join(new_posts)
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
                    write_posts(new_posts, output_path)
                    send_line_notify(message, line_notify_token)
                else:
                    logging.info("目前無新的資料")
                    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 目前無新的資料")
#                    send_line_notify("目前無新的資料", line_notify_token)

                if not page_has_posts:
                    logging.info("本頁沒有新帖子，停止搜索")
                    break
                url = PreviousPage(url)

        logging.info("等待60秒後繼續下一輪搜索...")
        time.sleep(60)

def get_existing_posts(output_path):
    if not os.path.exists(output_path):
        return []
    with open(output_path, 'r', encoding='utf-8') as file:  # 使用 utf-8 編碼打開檔
        return file.read().splitlines()

def write_posts(posts, output_path):
    with open(output_path, 'a', encoding='utf-8') as file:  # 使用 utf-8 編碼打開檔
        for post in posts:
            file.write(post + '\n')


def search_page(url, keyword1, keyword2, today):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    entries = soup.find_all('div', class_='r-ent')
    found_posts = []
    page_has_posts = False

    for entry in entries:
        title_div = entry.find('div', class_='title')
        date_div = entry.find('div', class_='date')
        if date_div and title_div.a:
            date_text = date_div.text.strip().lstrip("0")
            title_text = title_div.a.text.strip()
            link = 'https://www.ptt.cc' + title_div.a['href']
            if date_text == today and keyword1 in title_text and (keyword2 is None or keyword2 in title_text):
                found_posts.append(f"{date_text} {title_text} {link}")
                page_has_posts = True

    if not found_posts:
        logging.info(f"在{url}未找到符合條件的帖子")
    return found_posts, page_has_posts

if __name__ == '__main__':
    app = Application()
    app.mainloop()
