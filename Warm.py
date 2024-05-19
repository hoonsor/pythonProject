import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import time
import os

# 减少一天的日期
#today = (datetime.now() - timedelta(days=1)).strftime("%m/%d").lstrip("0")

# 今天的日期
today = (datetime.now()).strftime("%m/%d").lstrip("0")
print(f"搜尋的日期是：{today}")


# 定义 PreviousPage 函数
def PreviousPage(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    prev_link_tag = soup.find('a', string='‹ 上頁')
    if prev_link_tag:
        return 'https://www.ptt.cc' + prev_link_tag['href']
    return None


# 定义一个函数来处理每页的搜索
def search_page(url, keyword1, keyword2=None):
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


# 读取之前的帖子，避免重复输出
def get_existing_posts():
    if not os.path.exists(output_path):
        return []
    with open(output_path, 'r', encoding='big5') as file:
        return file.read().splitlines()


# 写入新的帖子到文本文件
def write_posts(posts):
    with open(output_path, 'a', encoding='big5') as file:
        for post in posts:
            file.write(post + '\n')


# 发送 Line 通知的函数
def send_line_notify(notification_message):

    line_notify_token = 'xg82zpDgusUytp9UrB9kJLSmWA0u8R7lRtLiRRYOi12'
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': f'Bearer {line_notify_token}'
    }
    data = {
        'message': notification_message
    }
    requests.post(line_notify_api, headers=headers, data=data)


# 文件路径
csv_path = 'C:/Users/user/Desktop/ptt爬蟲.csv'
output_path = 'C:/Users/user/Desktop/ptt_output.txt'

# 主循环
while True:
    df = pd.read_csv(csv_path, encoding='big5')
    existing_posts = get_existing_posts()

    for index, row in df.iterrows():
        board_name = row['板名']
        keyword1 = row['關鍵字1']
        keyword2 = row['關鍵字2'] if '關鍵字2' in row and not pd.isnull(row['關鍵字2']) else None
        url = f'https://www.ptt.cc/bbs/{board_name}/index.html'
        print(f"\n● 板名：[{board_name}] 关键字：[{keyword1}{'+' + keyword2 if keyword2 else ''}]")
        send_line_notify(f"\n● 板名：[{board_name}] 关键字：[{keyword1}{'+' + keyword2 if keyword2 else ''}]")  # 发送 Line 通知

        new_posts = []
        while url:
            posts, page_has_posts = search_page(url, keyword1, keyword2)
            new_posts += [post for post in posts if post not in existing_posts]
            if not page_has_posts:  # 如果这一页没有找到任何帖子，则停止搜索
                break
            url = PreviousPage(url)
        if new_posts:
            message = '\n'.join(new_posts)
            print(message)
            write_posts(new_posts)
            send_line_notify(message)  # 发送 Line 通知
        else:
            print("目前無新的資料")
            send_line_notify("目前無新的資料")  # 发送 Line 通知


    time.sleep(2)  # 暂停 60 秒
