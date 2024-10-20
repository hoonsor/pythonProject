import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import csv

def setup_root():
    """設置並返回主 tkinter 實例"""
    root = tk.Tk()
    root.withdraw()  # 隱藏主窗口
    return root

def select_csv_file(root, title="選擇 CSV 檔案"):
    """使用給定的 root 實例來顯示檔案選擇對話框"""
    file_path = filedialog.askopenfilename(
        parent=root,
        title=title,
        filetypes=[("CSV files", "*.csv")],
        defaultextension=".csv"
    )
    if not file_path:
        messagebox.showinfo("信息", "未選擇檔案", parent=root)
        return None
    return file_path

def query_financial_period(root, csv_path):
    """與用戶互動以獲取年份和季度信息，並修改 CSV 文件"""
    year = simpledialog.askstring("輸入年份", "請輸入所欲查詢的年份：", parent=root)
    if not year or not year.isdigit():
        messagebox.showerror("錯誤", "未輸入有效的年份", parent=root)
        return

    date_range_start = ''
    date_range_end = ''

    def select_quarter(quarter):
        nonlocal date_range_start, date_range_end
        if quarter == 1:
            date_range_start = f'AsOf{year}0331'
            date_range_end = f'From{year}0101To{year}0331'
        elif quarter == 2:
            date_range_start = f'AsOf{year}0630'
            date_range_end = f'From{year}0401To{year}0630'
        elif quarter == 3:
            date_range_start = f'AsOf{year}0930'
            date_range_end = f'From{year}0701To{year}0930'
        elif quarter == 4:
            date_range_start = f'AsOf{year}1231'
            date_range_end = f'From{year}1001To{year}1231'
        root.quit()

    select_window = tk.Toplevel(root)
    select_window.title("請選擇季別")
    tk.Label(select_window, text="請選擇季別：").pack(pady=10)

    for i in range(1, 5):
        tk.Button(select_window, text=f'第{i}季', command=lambda i=i: select_quarter(i)).pack(fill='x')

    root.mainloop()

    if date_range_start and date_range_end:
        modify_csv(root, csv_path, date_range_start, date_range_end)

def modify_csv(root, original_csv_path, start_date, end_date):
    """讀取 CSV 文件並替換特定文字，另存為新檔案"""
    new_csv_path = filedialog.asksaveasfilename(
        parent=root,
        title="保存修改後的 CSV 檔案",
        filetypes=[("CSV files", "*.csv")],
        defaultextension=".csv"
    )
    if not new_csv_path:
        messagebox.showinfo("信息", "未選擇儲存檔案", parent=root)
        return

    try:
        with open(original_csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            lines = [row for row in reader]

        modified_lines = [
            [col.replace('AA', start_date).replace('BB', end_date) for col in row] for row in lines
        ]

        with open(new_csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(modified_lines)

        messagebox.showinfo("成功", "CSV 文件已更新並另存為: " + new_csv_path, parent=root)
    except Exception as e:
        messagebox.showerror("錯誤", f"處理文件時發生錯誤: {e}", parent=root)

def main():
    root = setup_root()
    csv_path = select_csv_file(root, "請選擇 CSV 檔案")
    if csv_path:
        query_financial_period(root, csv_path)
    root.destroy()

if __name__ == "__main__":
    main()
