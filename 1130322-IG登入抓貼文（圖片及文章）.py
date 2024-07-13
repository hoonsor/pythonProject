from instaloader import Instaloader, Profile
from itertools import count
import re



# 创建Instaloader实例并登录
L = Instaloader()
# L.login("hoonsorasus@gmail.com", "LU16216!^@!^")  # 替换为你的Instagram账号和密码

# 尝试获取特定用户的帖子
try:
    profile = Profile.from_username(L.context, "karrytradecom")  # 替换 'your_username' 为目标Instagram用户名

    # 获取最新的帖子
    posts = profile.get_posts()
    post = next(posts)

    # 读取帖子的文本和其他信息
    text = post.caption
    # 使用正则表达式转换特定格式的文本
    text = re.sub(r'#(\w+)', r'#\1,', text)  # 将符合模式的字符串转换为所需格式
    # 将文本中的换行符转换为HTML的换行标签
    text_html = text.replace('\n', '<br>')
    date_str = post.date.strftime("%Y%m%d")  # 格式化日期

    # 准备存储图片的HTML代码
    images_html = ""
    counter = count(1)  # 创建一个计数器，从1开始

    if post.typename == 'GraphSidecar':
        for node in post.get_sidecar_nodes():
            if node.is_video:
                continue  # 如果侧边栏的节点是视频，则跳过
            number_str = str(next(counter)).zfill(2)  # 保证编号是两位数
            filename = f"{date_str}_{post.owner_username}_{number_str}"
            L.download_pic(filename, node.display_url, post.date_utc)
            images_html += f'<img src="{filename}.jpg" alt="Post image {number_str}">\n'
    else:
        if not post.is_video:
            number_str = '01'  # 单个图片时，默认编号为01
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
    # 储存为HTML文件
    with open(f"{date_str}_post.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML文件已生成。")

except StopIteration:
    # 如果没有帖子或无法访问，则打印消息
    print("没有找到帖子或无法访问。")

except Exception as e:
    # 打印出其他异常
    print(f"在尝试获取帖子时发生错误：{e}")