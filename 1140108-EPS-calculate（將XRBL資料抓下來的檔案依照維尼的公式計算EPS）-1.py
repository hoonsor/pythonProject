import tkinter as tk
from tkinter import filedialog
from bs4 import BeautifulSoup
import csv

from tkinter import ttk, messagebox
from PIL import Image, ImageTk

import os


def create_input_window(title, prompt, width=300, height=250, image_path=None):
    """建立包含圖片和文字輸入的對話框 (不使用父視窗)。"""
    try:
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")  # 設定視窗大小
        dialog.attributes('-topmost', True)

        if image_path:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"找不到圖片：{image_path}")

            image = Image.open(image_path)
            image_ratio = image.size[1] / image.size[0]
            new_width = width  # 根據視窗寬度調整圖片大小
            new_height = int(new_width * image_ratio)
            if new_height > height / 2:  # 如果圖片高度超過視窗一半，則縮小圖片
                new_height = int(height / 2)
                new_width = int(new_height / image_ratio)
            image = image.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            image_label = ttk.Label(dialog, image=photo)
            image_label.pack(pady=(10, 0))

        prompt_label = ttk.Label(dialog, text=prompt)
        prompt_label.pack(pady=(10, 0))

        entry = ttk.Entry(dialog)
        entry.pack(pady=(5, 10))

        user_input = None

        def on_ok():
            nonlocal user_input
            user_input = entry.get()
            dialog.destroy()

        def on_closing():
            if messagebox.askokcancel("關閉視窗", "您確定要關閉視窗嗎？"):
                dialog.destroy()
            else:
                user_input = ""

        ok_button = ttk.Button(dialog, text="確定", command=on_ok)
        ok_button.pack()

        dialog.protocol("WM_DELETE_WINDOW", on_closing)

        dialog.grab_set()
        dialog.focus_set()
        dialog.wait_window()

        return user_input

    except FileNotFoundError as e:
        messagebox.showerror("錯誤", str(e))
        return None
    except Exception as e:
        messagebox.showerror("錯誤", f"發生未預期的錯誤：{e}")
        return None

def open_folder_browser():
    """開啟資料夾選擇對話框並處理選定資料夾內的所有 HTML 文件。"""
    root = tk.Tk()
    root.withdraw()  # 隱藏 tkinter 主視窗
    folder_path = filedialog.askdirectory()
    if folder_path:
        files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.html')]
        data = []
        for file_path in files:
            data.append(process_html(file_path))
        save_to_csv(data)
    root.destroy()

def process_html(file_path):
    """讀取並處理 HTML 文件，從中提取所需的資訊，返回一行資料。"""
    print("Processing HTML file:", file_path)
    row_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        soup = BeautifulSoup(content, 'html.parser')

        # 解析標題中的公司代碼
        title_tag = soup.find('title', string=lambda text: create_input_window("請輸入財報網頁標題", "請輸入財報網頁標題：") in text)
        company_code = title_tag.text.split()[0] if title_tag else "-"
        row_data.append(company_code)

        # 解析營業利益（損失）、繼續營業單位稅前淨利（淨損）、基本每股盈餘合計
        for item_code in ['6900', '7900', '9750']:
            # value = process_financial_data(soup, item_code, 'From20240101To20240930')
            value = process_financial_data(soup, item_code, create_input_window("請輸入財報起訖時間", "請輸入財報起訖時間："))
            row_data.extend([item_code, value])
    except Exception as e:
        print("An error occurred while processing the file:", e)
        row_data = [file_path.split('/')[-1]] + ['-'] * 6  # 檔案名稱 + 六個'-'表示錯誤
    return row_data

def process_financial_data(soup, item_code, date_range):
    """從HTML中提取特定財務數據。"""
    row = soup.find('td', style="text-align:center", string=item_code)
    if row:
        # 正確的方法：找到父節點<tr>，然後找到所有class_="amt"的<td>，再過濾contextref
        parent_row = row.find_parent('tr')
        if parent_row:
            amt_cells = parent_row.find_all('td', class_="amt")
            for cell in amt_cells:
                nonfraction_tag = cell.find('ix:nonfraction', contextref=date_range)
                if nonfraction_tag:
                    net_income = nonfraction_tag.text.replace(',', '')
                    if nonfraction_tag.get('sign') == '-':
                        net_income = '-' + net_income
                    return net_income
    return "-"

def save_to_csv(data):
    """將所有提取的數據保存到一個 CSV 文件中。"""
    save_path = filedialog.asksaveasfilename(filetypes=[("CSV files", "*.csv")], defaultextension=".csv")
    if save_path:
        try:
            with open(save_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = ['Company Code', 'Item Code 6900', 'Net Operating Income 2023', 'Item Code 7900', 'Profit before tax 2023', 'Item Code 9750', 'EPS 2023']
                writer.writerow(headers)
                writer.writerows(data)
            print("File saved successfully:", save_path)
        except Exception as e:
            print("An error occurred while saving the file:", e)

open_folder_browser()



