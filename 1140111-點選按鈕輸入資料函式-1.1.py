import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

def create_button_window(title, x_count, y_count, button_labels, width=300, height=250):
    """建立包含按鈕的對話框，回傳按下按鈕的字串值，按鈕數量由 X 和 Y 軸決定。"""
    try:
        total_buttons = x_count * y_count
        if len(button_labels) < total_buttons:
            raise ValueError(f"button_labels 必須包含至少 {total_buttons} 個字串。")

        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")  # 設定視窗大小
        dialog.attributes('-topmost', True)

        user_selection = None

        def on_button_click(value):
            nonlocal user_selection
            user_selection = value
            dialog.destroy()

        def on_closing():
            if messagebox.askokcancel("關閉視窗", "您確定要關閉視窗嗎？"):
                dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_closing)

        # 建立按鈕的 XxY 網格
        frame = ttk.Frame(dialog)
        frame.pack(expand=True, fill=tk.BOTH, pady=20, padx=20)

        for i, label in enumerate(button_labels[:total_buttons]):
            button = ttk.Button(frame, text=label, command=lambda l=label: on_button_click(l))
            button.grid(row=i // x_count, column=i % x_count, padx=10, pady=10, sticky="nsew")

        # 設定每個網格的權重，使按鈕均勻分佈
        for i in range(x_count):
            frame.grid_columnconfigure(i, weight=1)
        for i in range(y_count):
            frame.grid_rowconfigure(i, weight=1)

        dialog.grab_set()
        dialog.focus_set()
        dialog.wait_window()

        return user_selection

    except ValueError as ve:
        messagebox.showerror("錯誤", str(ve))
        return None
    except Exception as e:
        messagebox.showerror("錯誤", f"發生未預期的錯誤：{e}")
        return None

# 範例使用方式：
if __name__ == "__main__":
    x_count = 4
    y_count = 2
    labels = ["按鈕1", "按鈕2", "按鈕3", "按鈕4", "按鈕5", "按鈕6", "按鈕7", "按鈕8"]
    result = create_button_window("按鈕選擇視窗", x_count, y_count, labels, width=800, height=600)
    if result:
        print("使用者選擇：", result)
