import tkinter as tk
from tkinter import messagebox

class TransparentWatermarkApp:
    def __init__(self, root, text_lines, horizontal_margin, vertical_margin, opacity=0.5, shift_interval=5000, shift_amount=0.1, font=("Arial", 20, "bold"), text_color='red'):
        self.root = tk.Toplevel(root)
        self.text_lines = text_lines
        self.opacity = opacity
        self.shift_interval = shift_interval
        self.shift_amount = shift_amount

        self.colors = ['red', 'blue', 'green', 'purple']
        self.current_color_index = 0
        self.text_color = text_color

        self.screen_width = self.root.winfo_screenwidth() - 2 * horizontal_margin
        self.screen_height = self.root.winfo_screenheight() - 2 * vertical_margin

        self.labels = []
        self.create_labels(font)

        self.root.attributes('-alpha', self.opacity)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.configure(bg='white')
        self.root.wm_attributes('-transparentcolor', 'white')
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+{horizontal_margin}+{vertical_margin}")

        self.schedule_shift()

    def create_labels(self, font):
        self.clear_labels()
        for i in range(9):
            label = tk.Label(self.root, text="\n".join(self.text_lines), font=font, bg='white', fg=self.text_color, borderwidth=0, highlightthickness=0)
            self.labels.append(label)
            label.place(x=0, y=0)

        self.update_label_positions()

    def update_label_positions(self):
        grid_width = self.screen_width / 3
        grid_height = self.screen_height / 3

        for i, label in enumerate(self.labels):
            grid_x = (i % 3) * grid_width
            grid_y = (i // 3) * grid_height
            label_x = grid_x + grid_width / 2 - label.winfo_reqwidth() / 2
            label_y = grid_y + grid_height / 2 - label.winfo_reqheight() / 2
            label.place(x=label_x, y=label_y)

    def schedule_shift(self):
        self.root.after(self.shift_interval, self.shift_labels)

    def shift_labels(self):
        for label in self.labels:
            current_x = label.winfo_x()
            new_x = (current_x + self.screen_width * self.shift_amount) % self.screen_width
            label.place(x=new_x)

        self.update_label_color()
        self.schedule_shift()

    def update_label_color(self):
        self.current_color_index = (self.current_color_index + 1) % len(self.colors)
        self.text_color = self.colors[self.current_color_index]
        for label in self.labels:
            label.config(fg=self.text_color)

    def clear_labels(self):
        for label in self.labels:
            label.destroy()
        self.labels = []


class DataEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("浮水印資料設定")

        labels = ["姓名：", "身份證字號：", "生日：", "電話：", "移動間隔秒數：", "透明度（0至1）：", "字體大小：", "顯示位置上下扣除間隔（px）：", "顯示位置左右扣除間隔（px）："]
        self.text_entries = [tk.Entry(root) for _ in labels]

        for i, label_text in enumerate(labels):
            label = tk.Label(root, text=label_text)
            label.grid(row=i, column=0)
            self.text_entries[i].grid(row=i, column=1)

        self.run_button = tk.Button(root, text="執行", command=self.run)
        self.run_button.grid(row=9, column=0)
        self.stop_button = tk.Button(root, text="停止", command=self.stop)
        self.stop_button.grid(row=9, column=1)

    def run(self):
        text_lines = [entry.get() for entry in self.text_entries[:-5]]
        try:
            shift_interval_seconds = int(self.text_entries[-5].get())
            shift_interval_milliseconds = shift_interval_seconds * 1000
            opacity = float(self.text_entries[-4].get())
            font_size = int(self.text_entries[-3].get())
            vertical_margin = int(self.text_entries[-2].get())
            horizontal_margin = int(self.text_entries[-1].get())

            if not 0 <= opacity <= 1 or font_size < 1 or vertical_margin < 1 or horizontal_margin < 1:
                raise ValueError

            self.watermark_app = TransparentWatermarkApp(self.root, text_lines, horizontal_margin, vertical_margin, opacity=opacity, font=("Microsoft JhengHei", font_size, "bold"), text_color='red', shift_interval=shift_interval_milliseconds)
            self.root.withdraw()

        except ValueError:
            messagebox.showerror("錯誤", "請確保所有輸入值均為正確的格式")

    def stop(self):
        self.root.destroy()

root = tk.Tk()

app = DataEntryApp(root)
root.mainloop()