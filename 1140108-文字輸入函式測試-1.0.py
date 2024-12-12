import tkinter as tk
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


# 範例使用方式：
if __name__ == "__main__":
    image_file = r"C:\Users\hoonsor\Pictures\烏魯魯.png"
    if not os.path.exists(image_file):
        dummy_image = Image.new("RGB", (100, 100), "white")
        dummy_image.save(image_file)

    # 有圖片，設定視窗大小
    user_text_with_image = create_input_window("有圖片的視窗", "請輸入文字（有圖）：", width=400, height=350, image_path=image_file)
    if user_text_with_image:
        print("使用者輸入（有圖）：", user_text_with_image)

    # 沒有圖片，使用預設視窗大小
    user_text_no_image = create_input_window("沒有圖片的視窗", "請輸入文字（無圖）：")
    if user_text_no_image:
        print("使用者輸入（無圖）：", user_text_no_image)

    # 有圖片，只設定寬度
    user_text_width_only = create_input_window("只有寬度的視窗", "請輸入文字（只有寬度）：", width=500,image_path=image_file)
    if user_text_width_only:
        print("使用者輸入（只有寬度）：", user_text_width_only)