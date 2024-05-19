from PIL import Image

try:
    img = Image.open("icon.ico")
    print("Icon loaded successfully.")
    img.show()  # 显示图标以确认加载正确
except IOError:
    print("Failed to load icon.")
