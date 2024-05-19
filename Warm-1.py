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

# 设置日志
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('ptt_crawler.log', maxBytes=10000, backupCount=1, encoding='utf-8')  # 明确设置 encoding
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# 检查config.csv是否存在并读取配置
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.csv')
    if os.path.exists(config_path):
        with open(config_path, mode='r', encoding='big5') as infile:
            reader = csv.reader(infile)
            config = list(reader)
        logging.info('配置文件加载成功')
        return config[0][0], config[1][0], config[2][0]
    else:
        logging.warning('未找到配置文件')
        messagebox.showwarning('警告', '未找到程式同路徑下的設定檔（config.csv）')
        return None, None, None

# 保存配置到config.csv
def save_config(line_notify_token, csv_path, output_path):
    config_path = os.path.join(os.path.dirname(__file__), 'config.csv')
    with open(config_path, mode='w', newline='', encoding='big5') as outfile:
        writer = csv.writer(outfile)
        writer.writerow([line_notify_token])
        writer.writerow([csv_path])
        writer.writerow([output_path])
    logging.info('配置文件已保存')

# 定义应用界面类
class Application(tk.Tk):
    def __init__(self, line_notify_token, csv_path, output_path):
        super().__init__()
        self.title('PTT爬蟲推播訊息')
        self.withdraw()  # 始终隐藏窗口
        if line_notify_token and csv_path and output_path:
            run_main_loop(line_notify_token, csv_path, output_path)
        else:
            # 如果配置不存在，可以在这里处理（例如显示错误消息或退出程序）
            messagebox.showerror("錯誤", "缺少必要的設定檔")
            self.destroy()  # 关闭程序

    # 创建输入界面的部件
    def create_widgets(self):
        tk.Label(self, text='Line權杖').grid(row=0)
        tk.Label(self, text='ptt搜尋資料之csv路徑').grid(row=1)
        tk.Label(self, text='比對資料暫存檔路徑').grid(row=2)

        self.token_entry = tk.Entry(self)
        self.token_entry.grid(row=0, column=1)
        self.csv_path_entry = tk.Entry(self)
        self.csv_path_entry.grid(row=1, column=1)
        self.output_path_entry = tk.Entry(self)
        self.output_path_entry.grid(row=2, column=1)

        tk.Button(self, text='確定', command=self.confirm).grid(row=3, column=0)
        tk.Button(self, text='取消', command=self.cancel).grid(row=3, column=1)

    # 确认按钮的操作
    def confirm(self):
        line_notify_token = self.token_entry.get()
        csv_path = self.csv_path_entry.get()
        output_path = self.output_path_entry.get()

        if not line_notify_token or not csv_path or not output_path:
            messagebox.showwarning('警告', '尚未輸入變數路徑')
        else:
            save_config(line_notify_token, csv_path, output_path)  # 保存配置
            self.withdraw()  # 隐藏窗口
            run_main_loop(line_notify_token, csv_path, output_path)

    # 取消按钮的操作
    def cancel(self):
        self.destroy()

# 发送Line通知的函数
def send_line_notify(notification_message, token):
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': notification_message}
    response = requests.post('https://notify-api.line.me/api/notify', headers=headers, data=data)
    if response.status_code == 200:
        logging.info('Line通知发送成功')
    else:
        logging.error('Line通知发送失败')
        messagebox.showerror("錯誤", "發送Line通知失敗，請檢查Token是否正確")
        exit()

# 定义 PreviousPage 函数
def PreviousPage(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    prev_link_tag = soup.find('a', string='‹ 上頁')
    if prev_link_tag:
        return 'https://www.ptt.cc' + prev_link_tag['href']
    return None

# 主循环函数，包括读取CSV、访问网页、处理数据
def run_main_loop(line_notify_token, csv_path, output_path):
    today = (datetime.now()).strftime("%m/%d").lstrip("0")
    print(f"搜索的日期是：{today}")

    try:
        df = pd.read_csv(csv_path, encoding='big5')
    except Exception as e:
        messagebox.showerror("錯誤", f"讀取csv文件失敗: {e}")
        send_line_notify(f"讀取csv文件失敗: {e}", line_notify_token)
        exit()

    existing_posts = get_existing_posts(output_path)

    for index, row in df.iterrows():
        board_name = row['板名']
        keyword1 = row['關鍵字1']
        keyword2 = row['關鍵字2'] if '關鍵字2' in row and not pd.isnull(row['關鍵字2']) else None
        url = f'https://www.ptt.cc/bbs/{board_name}/index.html'

        while url:
            try:
                posts, page_has_posts = search_page(url, keyword1, keyword2, today)
            except requests.exceptions.RequestException as e:
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
                print("目前無新的資料")
                send_line_notify("目前無新的資料", line_notify_token)

            if not page_has_posts:  # 如果这一页没有找到任何帖子，则停止搜索
                break
            url = PreviousPage(url)

        time.sleep(5)  # 暂停 60 秒

# 获取以前的帖子，避免重复输出
def get_existing_posts(output_path):
    if not os.path.exists(output_path):
        return []
    with open(output_path, 'r', encoding='big5') as file:
        return file.read().splitlines()

# 将新的帖子写入文本文件
def write_posts(posts, output_path):
    with open(output_path, 'a', encoding='big5') as file:
        for post in posts:
            file.write(post + '\n')

# 访问页面并搜索符合条件的帖子
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

    return found_posts, page_has_posts

if __name__ == '__main__':
    line_notify_token, csv_path, output_path = load_config()  # 尝试加载配置
    app = Application(line_notify_token, csv_path, output_path)
    app.mainloop()