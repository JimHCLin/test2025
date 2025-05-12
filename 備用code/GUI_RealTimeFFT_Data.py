import customtkinter as ctk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.filedialog as filedialog
from scipy.signal import find_peaks

# 設定中文字型
import matplotlib
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
        self.fig, (self.ax_time, self.ax_freq) = plt.subplots(2, 1, figsize=(6, 6))
        self.ax_time.set_title("時域信號")
        self.ax_time.set_xlabel("時間 (秒)")
        self.ax_time.set_ylabel("數值")

        self.ax_freq.set_title("頻域 (FFT) 結果")
        self.ax_freq.set_xlabel("頻率 (Hz)")
        self.ax_freq.set_ylabel("幅度")
        #self.ax_freq.set_xlim(0, 400)  # 限制頻率範圍
        #self.ax_freq.set_xlim(min(positive_frequencies), max(positive_frequencies))

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

        # 新增清除資料的按鈕
        self.clear_button = ctk.CTkButton(self.left_frame, text="清除資料", command=self.clear_data)
        self.clear_button.pack(side="top", padx=5, pady=5)

        # 右側 Frame 用於放置 csv_textbox
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 設定 csv_textbox 的大小為固定大小
        self.csv_textbox = ctk.CTkTextbox(self.right_frame, width=1000, height=200)  # 固定大小
        self.csv_textbox.pack(pady=5, padx=10, fill="none", expand=False)  # 讓它保持固定大小

    def load_csv(self):
        """讀取 CSV 並更新時域和頻域圖表"""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            # 讀取 CSV 資料
            self.df = pd.read_csv(file_path)
            self.csv_textbox.delete(1.0, ctk.END)  # 清空目前的 Textbox
            self.csv_textbox.insert(ctk.END, self.df.to_string(index=False))  # 顯示資料在 Textbox

            # 檢查 CSV 是否包含 "時間" 和 "數值" 欄位
            if '時間' not in self.df.columns or '數值' not in self.df.columns:
                print("CSV 檔案缺少 '時間' 或 '數值' 欄位")
                return

            # 確保數據是數值型態
            self.df['時間'] = pd.to_numeric(self.df['時間'], errors='coerce')
            self.df['數值'] = pd.to_numeric(self.df['數值'], errors='coerce')
            self.df = self.df.dropna(subset=['時間', '數值'])  # 刪除 NaN 值

            # 更新 x_data 和 y_data
            self.x_data = self.df['時間'].tolist()
            self.y_data = self.df['數值'].tolist()

            # 顯示在時域圖表
            self.ax_time.clear()  # 清除現有的圖表
            self.ax_time.plot(self.x_data, self.y_data, label="數據")
            self.ax_time.set_title("時域信號")
            self.ax_time.set_xlabel("時間 (秒)")
            self.ax_time.set_ylabel("數值")
            self.ax_time.legend()

            # 計算並顯示頻域 (FFT)
            self.ax_freq.clear()  # 清除現有的頻域圖表
            self.compute_and_plot_fft()

            # 更新畫布
            self.canvas.draw()

    def compute_and_plot_fft(self):
        """計算傅立葉轉換 (FFT) 並繪製頻域圖表，並列出峰值"""
        # 傅立葉轉換（FFT）
        signal_fft = np.fft.fft(self.y_data)
        frequencies_fft = np.fft.fftfreq(len(self.y_data), self.x_data[1] - self.x_data[0])

        # 計算幅度
        magnitude = np.abs(signal_fft)

        # 只顯示正頻率部分
        positive_frequencies = frequencies_fft[:len(frequencies_fft)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]

        # 找出頻域的峰值
        peaks, _ = find_peaks(positive_magnitude, height=0)  # 設定高度門檻以過濾小的峰值
        peak_frequencies = positive_frequencies[peaks]  # 對應的頻率
        print(f"peak_frequencies:{peak_frequencies}")
        peak_magnitudes = positive_magnitude[peaks]  # 對應的幅度
        #
        self.ax_freq.set_xlim(min(positive_frequencies), max(positive_frequencies))

        # 打印出峰值頻率和幅度
        print("頻域峰值:")
        for freq, mag in zip(peak_frequencies, peak_magnitudes):
            print(f"頻率: {freq:.2f} Hz, 幅度: {mag:.2f}")

        # 繪製頻域圖
        self.ax_freq.plot(positive_frequencies, positive_magnitude, label="FFT 結果")
        self.ax_freq.scatter(peak_frequencies, peak_magnitudes, color='red', label="峰值")  # 在圖表上標示峰值
        self.ax_freq.set_title("頻域 (FFT) 結果")
        self.ax_freq.set_xlabel("頻率 (Hz)")
        self.ax_freq.set_ylabel("幅度")
        self.ax_freq.legend()

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

                self.ax_time.plot(self.x_data, self.y_data, label="數據")
                self.ax_time.set_xlim(min(self.x_data), max(self.x_data))
                self.ax_time.set_ylim(min(self.y_data) - 5, max(self.y_data) + 5)

                # 更新頻域圖
                self.compute_and_plot_fft()

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
        df = pd.DataFrame({"時間": self.x_data, "數值": self.y_data})
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
        if file_path:
            df.to_csv(file_path, index=False)
            print(f"資料已匯出至 {file_path}")

    def show_all_data(self):
        self.ax_time.clear()
        self.ax_time.plot(self.x_data, self.y_data, label="數據")
        self.ax_time.set_xlim(min(self.x_data), max(self.x_data))
        self.ax_time.set_ylim(min(self.y_data) - 5, max(self.y_data) + 5)
        self.ax_time.set_title("時域信號")
        self.ax_time.set_xlabel("時間 (秒)")
        self.ax_time.set_ylabel("數值 ")
        self.ax_time.legend()

        self.compute_and_plot_fft()

        self.canvas.draw()

    def clear_data(self):
        """清除資料並重置圖表"""
        self.x_data = []
        self.y_data = []
        self.df = None
        self.index = 0

        self.ax_time.clear()
        self.ax_freq.clear()

        self.ax_time.set_title("時域信號")
        self.ax_time.set_xlabel("時間 (秒)")
        self.ax_time.set_ylabel("數值 ")

        self.ax_freq.set_title("頻域 (FFT) 結果")
        self.ax_freq.set_xlabel("頻率 (Hz)")
        self.ax_freq.set_ylabel("幅度")

        self.csv_textbox.delete(1.0, ctk.END)

        self.canvas.draw()

if __name__ == "__main__":
    app = RealtimePlotApp()
    app.mainloop()
