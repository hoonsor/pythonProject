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
from logging.handlers import RotatingFileHandler

# 設置日誌
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('ptt_crawler.log', maxBytes=10000, backupCount=1, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 檢查config.csv是否存在並讀取配置
def load_config():
    logging.info("嘗試載入設定檔...")
    config_path = os.path.join(os.path.dirname(__file__), 'config.csv')
    if os.path.exists(config_path):
        with open(config_path, mode='r', encoding='big5') as infile:
            reader = csv.reader(infile)
            config = list(reader)
        logging.info('設定檔載入成功')
        return config[0][0], config[1][0], config[2][0]
    else:
        logging.warning('未找到設定檔')
        messagebox.showwarning('警告', '未找到程式同路徑下的設定檔（config.csv）')
        return None, None, None

def save_config(line_notify_token, csv_path, output_path):
    logging.info("保存配置到config.csv...")
    config_path = os.path.join(os.path.dirname(__file__), 'config.csv')
    with open(config_path, mode='w', newline='', encoding='big5') as outfile:
        writer = csv.writer(outfile)
        writer.writerow([line_notify_token])
        writer.writerow([csv_path])
        writer.writerow([output_path])
    logging.info('設定檔已保存')

class Application(tk.Tk):
    def __init__(self, line_notify_token, csv_path, output_path):
        super().__init__()
        self.title('PTT爬蟲推播訊息')
        self.withdraw()
        if line_notify_token and csv_path and output_path:
            logging.info("啟動主迴圈...")
            run_main_loop(line_notify_token, csv_path, output_path)
        else:
            messagebox.showerror("錯誤", "缺少必要的設定檔")
            self.destroy()

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

def run_main_loop(line_notify_token, csv_path, output_path):
    previous_day = None
    while True:
        today = (datetime.now()).strftime("%m/%d").lstrip("0")
        if today != previous_day:
            logging.info(f"搜索的日期是：{today}")
            previous_day = today
            # 日期改變時清空output_path檔
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
                    message = '\n'.join(new_posts)
                    print(message)
                    write_posts(new_posts, output_path)
                    send_line_notify(message, line_notify_token)
                else:
                    logging.info("目前無新的資料")
                    print("目前無新的資料")
                    send_line_notify("目前無新的資料", line_notify_token)

                if not page_has_posts:
                    logging.info("本頁沒有新帖子，停止搜索")
                    break
                url = PreviousPage(url)

        logging.info("等待5秒後繼續下一輪搜索...")
        time.sleep(5)

def get_existing_posts(output_path):
    if not os.path.exists(output_path):
        return []
    with open(output_path, 'r', encoding='big5') as file:
        return file.read().splitlines()

def write_posts(posts, output_path):
    with open(output_path, 'a', encoding='big5') as file:
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
    line_notify_token, csv_path, output_path = load_config()
    app = Application(line_notify_token, csv_path, output_path)
    app.mainloop()
