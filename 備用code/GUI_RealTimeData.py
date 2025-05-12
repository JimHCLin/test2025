import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter.filedialog as filedialog

# 設定中文字型
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
matplotlib.rcParams['axes.unicode_minus'] = False

class RealtimePlotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("即時數據視覺化")
        self.geometry("800x750")
        ctk.set_appearance_mode("light")

        # 初始化資料
        self.x_data = []
        self.y_data = []
        self.update_running = False
        self.df = None
        self.index = 0

        # 建立圖表
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.line, = self.ax.plot([], [], label="數據", color='blue')
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 50)
        self.ax.set_title("即時資料圖")
        self.ax.set_xlabel("時間 (秒)")
        self.ax.set_ylabel("數值 (°C)")
        self.ax.legend()
        self.fig.tight_layout()

        # 嵌入圖表
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20)

        # 按鈕區，這個 frame 用來包含所有按鈕和資料顯示區
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # 左側 Frame 用於放置按鈕
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # 讀取 CSV 按鈕（放置在最上面）
        self.load_button = ctk.CTkButton(self.left_frame, text="讀取 CSV", command=self.load_csv)
        self.load_button.pack(side="top", padx=5, pady=5)

        # 其他按鈕（放置在讀取 CSV 按鈕下方）
        self.update_button = ctk.CTkButton(self.left_frame, text="更新資料", command=self.start_update)
        self.update_button.pack(side="top", padx=5, pady=5)

        self.stop_button = ctk.CTkButton(self.left_frame, text="停止更新", command=self.stop_update)
        self.stop_button.pack(side="top", padx=5, pady=5)

        self.print_button = ctk.CTkButton(self.left_frame, text="列出目前資料", command=self.print_all_data)
        self.print_button.pack(side="top", padx=5, pady=5)

        self.save_button = ctk.CTkButton(self.left_frame, text="儲存圖表", command=self.save_chart_as_png)
        self.save_button.pack(side="top", padx=5, pady=5)

        self.export_button = ctk.CTkButton(self.left_frame, text="匯出資料", command=self.export_data_to_csv)
        self.export_button.pack(side="top", padx=5, pady=5)

        self.show_all_button = ctk.CTkButton(self.left_frame, text="顯示全部資料", command=self.show_all_data)
        self.show_all_button.pack(side="top", padx=5, pady=5)

        # 右側 Frame 用於放置 csv_textbox
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 設定 csv_textbox 的大小為固定大小
        self.csv_textbox = ctk.CTkTextbox(self.right_frame, width=1000, height=300)  # 固定大小
        self.csv_textbox.pack(pady=5, padx=10, fill="none", expand=False)  # 讓它保持固定大小

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path)
            self.csv_textbox.delete(1.0, ctk.END)
            self.csv_textbox.insert(ctk.END, self.df.to_string(index=False))

            if '時間' not in self.df.columns or '數值' not in self.df.columns:
                print("CSV 檔案缺少 '時間' 或 '數值' 欄位")
                return

            self.df['時間'] = pd.to_numeric(self.df['時間'], errors='coerce')
            self.df['數值'] = pd.to_numeric(self.df['數值'], errors='coerce')
            self.df = self.df.dropna(subset=['時間', '數值'])

            self.index = 50  # 下一筆資料從第 51 筆開始更新
            preview = self.df.head(50)

            self.x_data = preview['時間'].tolist()
            self.y_data = preview['數值'].tolist()

            self.line.set_xdata(self.x_data)
            self.line.set_ydata(self.y_data)
            self.ax.set_xlim(min(self.x_data), max(self.x_data))
            self.ax.set_ylim(min(self.y_data) - 5, max(self.y_data) + 5)
            self.canvas.draw()

    def start_update(self):
        if not self.update_running and self.df is not None:
            self.update_running = True
            self.update_plot()

    def stop_update(self):
        self.update_running = False

    def update_plot(self):
        if self.update_running and self.df is not None:
            if self.index < len(self.df):
                new_time = self.df.loc[self.index, '時間']
                new_value = self.df.loc[self.index, '數值']

                self.x_data.append(new_time)
                self.y_data.append(new_value)

                self.line.set_xdata(self.x_data)
                self.line.set_ydata(self.y_data)
                self.ax.set_xlim(min(self.x_data), max(self.x_data))
                self.ax.set_ylim(min(self.y_data) - 5, max(self.y_data) + 5)
                self.canvas.draw()

                self.index += 1

            self.after(500, self.update_plot)

    def print_all_data(self):
        content = "X 資料（時間）:\n" + str(self.x_data) + "\n\n"
        content += "Y 資料（數值）:\n" + str(self.y_data)
        self.csv_textbox.delete(1.0, ctk.END)
        self.csv_textbox.insert(ctk.END, content)

    def save_chart_as_png(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)
            print(f"圖表已儲存為 {file_path}")

    def export_data_to_csv(self):
        if not self.x_data or not self.y_data:
            print("沒有資料可匯出")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            df = pd.DataFrame({'時間': self.x_data, '數值': self.y_data})
            df.to_csv(file_path, index=False)
            print(f"資料已匯出至 {file_path}")

    def show_all_data(self):
        if self.df is None:
            print("尚未讀取任何資料")
            return

        self.x_data = self.df['時間'].tolist()
        self.y_data = self.df['數值'].tolist()

        self.line.set_xdata(self.x_data)
        self.line.set_ydata(self.y_data)
        self.ax.set_xlim(min(self.x_data), max(self.x_data))
        self.ax.set_ylim(min(self.y_data) - 5, max(self.y_data) + 5)
        self.canvas.draw()
        print("已顯示全部資料")

if __name__ == "__main__":
    app = RealtimePlotApp()
    app.mainloop()
