from instaloader import Instaloader, Profile
from itertools import count
import re
import csv
import sys

# 創建Instaloader實例
L = Instaloader()

# 嘗試從目前的目錄下的CSV檔讀取登錄憑證
try:
    with open('credentials.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        credentials = list(reader)
        if len(credentials) < 2:
            raise ValueError("CSV檔案格式不正確，必須包含兩行，分別是帳號和密碼。")

    # 使用讀取到的憑證登錄
    L.login(credentials[0][0], credentials[1][0])
except FileNotFoundError:
    print("找不到 'credentials.csv' 檔，請確保它位於程式相同的目錄下。")
    sys.exit(1)
except ValueError as e:
    print(e)
    sys.exit(1)
except Exception as e:
    print(f"登錄失敗：{e}")
    sys.exit(1)

# 嘗試獲取特定用戶的帖子
try:
    profile = Profile.from_username(L.context, "karrytradecom")

    # 獲取最新的帖子
    posts = profile.get_posts()
    post = next(posts)

    # 讀取帖子的文本和其他資訊
    text = post.caption
    # 使用規則運算式轉換特定格式的文本
    text = re.sub(r'#(\w+)', r'#\1,', text)  # 將符合模式的字串轉換為所需格式
    # 將文本中的分行符號轉換為HTML的換行標籤
    text_html = text.replace('\n', '<br>')
    date_str = post.date.strftime("%Y%m%d")  # 格式化日期

    # 準備存儲圖片的HTML代碼
    images_html = ""
    counter = count(1)  # 創建一個計數器，從1開始

    if post.typename == 'GraphSidecar':
        for node in post.get_sidecar_nodes():
            if node.is_video:
                continue  # 如果側邊欄的節點是視頻，則跳過
            number_str = str(next(counter)).zfill(2)  # 保證編號是兩位數
            filename = f"{date_str}_{post.owner_username}_{number_str}"
            L.download_pic(filename, node.display_url, post.date_utc)
            images_html += f'<img src="{filename}.jpg" alt="Post image {number_str}">\n'
    else:
        if not post.is_video:
            number_str = '01'  # 單個圖片時，預設編號為01
            filename = f"{date_str}_{post.owner_username}_{number_str}"
            L.download_pic(filename, post.url, post.date_utc)
            images_html += f'<img src="{filename}.jpg" alt="Post image">\n'

    # 生成HTML，註解部分為用不到的文字

    #    <h1>Post from {post.date.strftime('%Y-%m-%d')}</h1>
    #    {images_html}
    html_content = f"""
    <html>
    <head>
        <title>Instagram Post on {post.date.strftime('%Y-%m-%d')}</title>
    </head>
    <body>
        <h3>{text_html}</h3>
    </body>
    </html>
    """
    # 儲存為HTML檔
    with open(f"{date_str}_post.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML檔已生成。")

except StopIteration:
    print("沒有找到帖子或無法訪問。")
except Exception as e:
    print(f"在嘗試獲取帖子時發生錯誤：{e}")

