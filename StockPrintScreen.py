import tkinter as tk
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os
import sys  # Used to get the path of the .exe

# Set the path to save screenshots
B = 'D:\\截圖\\'  # Please fill in your path

# Create a dynamic array X
X = []

def on_key_press(event):
    if event.keysym == 'Return':
        X.append(entry.get())
        entry.delete(0, tk.END)
    elif event.keysym == 'Escape':
        root.destroy()

root = tk.Tk()
root.title("請輸入股票代號")

tk.Label(root, text="請輸入股票代號").pack()

entry = tk.Entry(root)
entry.bind('<KeyPress>', on_key_press)
entry.pack()

root.mainloop()

# Configure webdriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Specify the path of the webdriver as the same directory as the current executable
current_path = os.path.dirname(os.path.abspath(sys.argv[0]))
webdriver_path = os.path.join(current_path, 'chromedriver.exe')
webdriver_service = Service(webdriver_path)

# Open Chrome browser
browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# Open the URL for each element in the dynamic array X, adjust the font size to 80%, and take a screenshot
for i in X:
    url = "https://mops.twse.com.tw/mops/web/t146sb05"
    browser.get(url)
    browser.execute_script(f'document.getElementById("co_id").value = "{i}";')
    browser.find_element(By.CSS_SELECTOR, '#search_bar1 input[type="button"]').click()
    time.sleep(3)
    screenshot_filename = os.path.join(B, f'{datetime.now().strftime("%Y%m%d")}-{i}.png')
    browser.save_screenshot(screenshot_filename)

browser.quit()
