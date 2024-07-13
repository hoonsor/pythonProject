import tkinter as tk
from tkinter import filedialog
from bs4 import BeautifulSoup
import csv
import os

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
        title_tag = soup.find('title', string=lambda text: '2023Q4 Financial report' in text)
        company_code = title_tag.text.split()[0] if title_tag else "-"
        row_data.append(company_code)

        # 解析營業利益（損失）、繼續營業單位稅前淨利（淨損）、基本每股盈餘合計
        for item_code in ['6900', '7900', '9750']:
            value = process_financial_data(soup, item_code, 'From20230101To20231231')
            row_data.extend([item_code, value])
    except Exception as e:
        print("An error occurred while processing the file:", e)
        row_data = [file_path.split('/')[-1]] + ['-'] * 6  # 檔案名稱 + 六個'-'表示錯誤
    return row_data

def process_financial_data(soup, item_code, date_range):
    """從HTML中提取特定財務數據。"""
    row = soup.find('td', style="text-align:center", string=item_code)
    if row:
        net_income_tag = row.find_next_sibling('td', class_="amt").find('ix:nonfraction', contextref=date_range)
        if net_income_tag:
            net_income = net_income_tag.text.replace(',', '')  # 移除逗號
            if net_income_tag.get('sign') == '-':
                net_income = '-' + net_income
            return net_income
    return "-"  # 當資料不存在時返回'-'

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
