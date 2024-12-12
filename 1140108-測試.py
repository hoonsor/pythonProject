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


# 範例
def main_app():
    root = tk.Tk()
    root.title("主應用程式")
    ttk.Label(root, text="這是主應用程式視窗。").pack(pady=20)

    def open_dialog():
        image_file = "python_logo.png"
        if not os.path.exists(image_file):
            dummy_image = Image.new("RGB", (100, 100), "white")
            dummy_image.save(image_file)
        user_input = create_input_window("輸入視窗", "請輸入文字：", width=400, height=300,
                                         image_path=image_file)  # 使用寬高參數
        if user_input:
            print("使用者輸入：", user_input)
        user_input2 = create_input_window("輸入視窗2", "請輸入文字2：", width=500, height=400)  # 不使用圖片
        if user_input2:
            print("使用者輸入2：", user_input2)

    ttk.Button(root, text="開啟輸入視窗", command=open_dialog).pack()
    root.mainloop()


if __name__ == "__main__":
    main_app()