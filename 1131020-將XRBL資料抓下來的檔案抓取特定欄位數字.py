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

    csv_item_code = select_csv_file("選擇「爬取之項目編號」csv檔案")
    csv_title = select_csv_file("選擇「檔案標題」csv檔案")

    if folder_path:
        files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith('.html')]
        data = []
        for file_path in files:
            data.append(process_html(file_path, csv_item_code))
        save_to_csv(data, csv_title)
    root.destroy()

def process_html(file_path, csv_item_code):
    """讀取並處理 HTML 文件，從中提取所需的資訊，返回一行資料。"""
    print("Processing HTML file:", file_path)
    row_data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        soup = BeautifulSoup(content, 'html.parser')

        # 解析標題中的公司代碼
        title_tag = soup.find('title', string=lambda text: 'Financial report' in text)
        company_code = title_tag.text.split()[0] if title_tag else "-"
        row_data.append(company_code)

        # 創建一個字典，將項目代碼映射到其對應的財報期間
        financial_periods = csv_to_dict(csv_item_code)
        # 使用字典中的資訊來執行處理財報數據的函數
        for item_code, period in financial_periods.items():
            value = process_financial_data(soup, item_code, period)
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

def save_to_csv(data, csv_title):
    """將所有提取的數據保存到一個 CSV 文件中。"""
    save_path = filedialog.asksaveasfilename(filetypes=[("CSV files", "*.csv")], defaultextension=".csv")
    if save_path:
        try:
            with open(save_path, 'w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                headers = read_csv_headers(csv_title)
                writer.writerow(headers)
                writer.writerows(data)
            print("File saved successfully:", save_path)
        except Exception as e:
            print("An error occurred while saving the file:", e)

def read_csv_headers(csv_path):
    """讀取指定 CSV 文件的第一列數據作為列表返回。

    參數:
        csv_path (str): CSV 文件的路徑。

    返回:
        list: 包含 CSV 文件第一列數據的列表。
    """
    headers = []
    try:
        with open(csv_path, newline='', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            # 假設標頭資料都在第一列的不同行中
            headers = [row[0] for row in reader]  # 讀取每一行的第一個元素
    except FileNotFoundError:
        print(f"無法找到文件: {csv_path}")
    except Exception as e:
        print(f"讀取文件時發生錯誤: {e}")

    return headers

def csv_to_dict(csv_path):
    """讀取 CSV 文件，將第一列設定為字典的鍵，第二列設定為字典的值。

    參數:
        csv_path (str): CSV 文件的路徑。

    返回:
        dict: 從 CSV 文件的第一和第二列構建的字典。
    """
    result_dict = {}
    try:
        with open(csv_path, newline='', encoding='utf-8-sig') as file:  # 使用 utf-8-sig 來自動處理 BOM
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    continue  # 如果該行沒有至少兩個元素，則跳過
                key = row[0]  # 第一列為鍵
                value = row[1]  # 第二列為值
                result_dict[key] = value
    except FileNotFoundError:
        print(f"無法找到文件: {csv_path}")
    except Exception as e:
        print(f"讀取文件時發生錯誤: {e}")

    return result_dict


def select_csv_file(title="選擇 CSV 檔案"):
    """顯示檔案選擇對話框，讓使用者選擇一個 CSV 檔案。

    參數:
        title (str): 對話框的標題。

    返回:
        str: 選擇的 CSV 檔案路徑，如果未選擇則返回 None。
    """
    # 初始化 Tkinter root
    root = tk.Tk()
    root.withdraw()  # 隱藏主視窗

    # 打開檔案選擇對話框
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=[("CSV files", "*.csv")],
        defaultextension=".csv"
    )

    # 如果未選擇檔案，返回 None
    if not file_path:
        print("未選擇檔案")
        return None

    # 返回選擇的檔案路徑
    return file_path

# 使用示例：
# csv_path = select_csv_file("請選擇要處理的 CSV 檔案")
# if csv_path:
#     print("選擇的檔案路徑:", csv_path)



open_folder_browser()
