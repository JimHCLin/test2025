import customtkinter as ctk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.filedialog as filedialog
from scipy.signal import find_peaks
import os  # 檔案名稱處理
from tkinter import messagebox

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
        self.top_frequencies = []  # 用來儲存前5大頻率
        self.top_magnitudes = []  # 用來儲存前5大幅度

        # 建立圖表
        self.fig, (self.ax_time, self.ax_freq) = plt.subplots(2, 1, figsize=(6, 6))
        self.ax_time.set_title("時域訊號")
        self.ax_time.set_xlabel("時間(秒)")
        self.ax_time.set_ylabel("三軸RMS數值")

        self.ax_freq.set_title("頻域(FFT)訊號")
        self.ax_freq.set_xlabel("頻率(Hz)")
        self.ax_freq.set_ylabel("振幅")

        self.fig.tight_layout()

        # 嵌入圖表
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20)

        # 按鈕區框架
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # 左側按鈕區
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.load_button = ctk.CTkButton(self.left_frame, text="讀取 CSV", command=self.load_csv)
        self.load_button.pack(side="top", padx=5, pady=5)

        self.update_button = ctk.CTkButton(self.left_frame, text="更新資料", command=self.start_update)
        #self.update_button.pack(side="top", padx=5, pady=5)

        self.stop_button = ctk.CTkButton(self.left_frame, text="停止更新", command=self.stop_update)
        #self.stop_button.pack(side="top", padx=5, pady=5)

        self.print_button = ctk.CTkButton(self.left_frame, text="列出目前資料", command=self.print_all_data)
        self.print_button.pack(side="top", padx=5, pady=5)

        self.save_button = ctk.CTkButton(self.left_frame, text="儲存圖表", command=self.save_chart_as_png)
        self.save_button.pack(side="top", padx=5, pady=5)

        self.export_button = ctk.CTkButton(self.left_frame, text="匯出資料", command=self.export_data_to_csv)
        self.export_button.pack(side="top", padx=5, pady=5)

        self.show_all_button = ctk.CTkButton(self.left_frame, text="顯示全部資料", command=self.show_all_data)
        #self.show_all_button.pack(side="top", padx=5, pady=5)

        self.clear_button = ctk.CTkButton(self.left_frame, text="清除資料", command=self.clear_data)
        self.clear_button.pack(side="top", padx=5, pady=5)

        # 右側顯示區
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # 顯示讀取的檔案名稱
        self.filename_label = ctk.CTkLabel(self.right_frame, text="未載入任何檔案", anchor="w")
        self.filename_label.pack(fill="x", padx=10, pady=(5, 0))

        # 資料顯示區
        self.csv_textbox = ctk.CTkTextbox(self.right_frame, width=1000, height=200)
        self.csv_textbox.pack(pady=5, padx=10, fill="none", expand=False)
        
    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            filename = os.path.basename(file_path)
            self.filename_label.configure(text=f"讀取檔案: {filename}")

            try:
                self.df = pd.read_csv(file_path, encoding='big5',header=3)  # 加入 encoding 解決中文亂碼/錯誤
            except UnicodeDecodeError:
                try:
                    self.df = pd.read_csv(file_path, encoding='utf-8-sig')
                except Exception as e:
                    print(f"讀取失敗：{e}")
                    return

            # 顯示欄位名稱，這樣你可以確認 CSV 內容
            print(f"CSV 欄位名稱test: {self.df.columns.tolist()}")#先註解
            #print("CSV 檔案的欄位：", self.df.columns)

            # 檢查是否包含 Xaxis、Yaxis、Zaxis 欄位
            required_cols = ['Xaxis', 'Yaxis', 'Zaxis']
            if not all(col in self.df.columns for col in required_cols):
                messagebox.showerror("錯誤", "CSV 檔案缺少 Xaxis、Yaxis 或 Zaxis 欄位")
                print(f"錯誤: 缺少以下欄位之一: {required_cols}")
                return

            self.csv_textbox.delete(1.0, ctk.END)
            self.csv_textbox.insert(ctk.END, self.df.to_string(index=False))

            # 只讀取 B6:D85937 的資料
            #self.df = self.df.iloc[5:85937]  # 取 B6~D85937 對應第6~85937列
            self.df = self.df.iloc[1:85937]  # 取 B6~D85937 對應第6~85937列

            # 移除欄位名稱空白
            self.df.columns = self.df.columns.str.strip()

            # 確保 Xaxis、Yaxis、Zaxis 欄位存在
            if 'Xaxis' not in self.df.columns or 'Yaxis' not in self.df.columns or 'Zaxis' not in self.df.columns:
                print("錯誤：CSV 檔案缺少 Xaxis、Yaxis 或 Zaxis 欄位")
                return

            # 將欄位轉為數值型態
            self.df['Xaxis'] = pd.to_numeric(self.df['Xaxis'], errors='coerce')
            self.df['Yaxis'] = pd.to_numeric(self.df['Yaxis'], errors='coerce')
            self.df['Zaxis'] = pd.to_numeric(self.df['Zaxis'], errors='coerce')
            self.df = self.df.dropna(subset=['Xaxis', 'Yaxis', 'Zaxis'])

            # 計算 RMS = sqrt(Xaxis² + Yaxis² + Zaxis²)
            rms = np.sqrt(self.df['Xaxis']**2 + self.df['Yaxis']**2 + self.df['Zaxis']**2)
            self.y_data = rms.tolist()

            # 固定時間軸 X
            sample_count = min(len(self.y_data), 85932)
            self.x_data = np.round(0.000128008 + 0.000128 * np.arange(sample_count), 9).tolist()
            self.y_data = self.y_data[:sample_count]

            self.ax_time.clear()
            self.ax_time.plot(self.x_data, self.y_data, label="數據")
            self.ax_time.set_title("時域訊號")
            self.ax_time.set_xlabel("時間(秒)")
            self.ax_time.set_ylabel("三軸RMS數值")
            self.ax_time.legend()
            self.ax_time.relim()
            self.ax_time.autoscale_view()

            self.ax_freq.clear()
            self.compute_and_plot_fft()

            self.canvas.draw()

    def compute_and_plot_fft(self):
        if len(self.y_data) < 2:
            return

        signal_fft = np.fft.fft(self.y_data)
        dt = self.x_data[1] - self.x_data[0]
        frequencies_fft = np.fft.fftfreq(len(self.y_data), dt)
        magnitude = np.abs(signal_fft)

        positive_frequencies = frequencies_fft[:len(frequencies_fft)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]

        peaks, _ = find_peaks(positive_magnitude, height=0)
        peak_frequencies = positive_frequencies[peaks]
        peak_magnitudes = positive_magnitude[peaks]

        # 儲存前 5 大峰值頻率和幅度
        sorted_indices = np.argsort(peak_magnitudes)[-5:][::-1]  # 排序並取最大5個
        self.top_frequencies = peak_frequencies[sorted_indices]
        self.top_magnitudes = peak_magnitudes[sorted_indices]

        self.ax_freq.plot(positive_frequencies, positive_magnitude, label="FFT 結果")
        self.ax_freq.scatter(self.top_frequencies, self.top_magnitudes, color='red', label="前 5 大峰值")
        self.ax_freq.set_title("頻域(FFT)訊號")
        self.ax_freq.set_xlabel("頻率(Hz)")
        self.ax_freq.set_ylabel("振幅")
        self.ax_freq.set_xlim(0, max(positive_frequencies))
        self.ax_freq.set_ylim(0, 5e7)
        self.ax_freq.legend()

        peak_info = "前 5 大頻率與幅度:\n"
        for i in range(5):
            peak_info += f"頻率: {self.top_frequencies[i]:.4f} Hz, 幅度: {self.top_magnitudes[i]:.2f}\n"

        self.csv_textbox.delete(1.0, ctk.END)
        self.csv_textbox.insert(ctk.END, peak_info)

    def start_update(self):
        if not self.update_running:
            self.update_running = True
            self.update_data()

    def stop_update(self):
        self.update_running = False

    def update_data(self):
        if self.update_running and len(self.x_data) > 0 and len(self.y_data) > 0:
            self.index += 1
            if self.index >= len(self.x_data):
                self.index = 0
            self.ax_time.clear()
            self.ax_time.plot(self.x_data[:self.index], self.y_data[:self.index], label="數據")
            self.ax_time.set_title("時域訊號")
            self.ax_time.set_xlabel("時間(秒)")
            self.ax_time.set_ylabel("三軸RMS數值")
            self.ax_time.legend()
            self.ax_time.relim()
            self.ax_time.autoscale_view()

            self.ax_freq.clear()
            self.compute_and_plot_fft()
            self.canvas.draw()

            self.after(100, self.update_data)

    def print_all_data(self):
        #print("時間軸 (x_data):", self.x_data)
        #print("RMS數值 (y_data):", self.y_data)
        print("RMS數值 (y_data):",self.y_data[:20])
        #self.df['ax']
        #print("Xaxis:")
        #print(self.df['Xaxis'].head(20).to_string(index=False))
        print(f"Xaxis數值:{self.df['Xaxis'].head(20).to_string(index=False)}\n")
        print(f"Yaxis數值:{self.df['Yaxis'].head(20).to_string(index=False)}\n")
        print(f"Zaxis數值:{self.df['Zaxis'].head(20).to_string(index=False)}\n")

    def clear_data(self):
        self.x_data.clear()
        self.y_data.clear()
        self.ax_time.clear()
        self.ax_freq.clear()
        self.canvas.draw()
        self.csv_textbox.delete(1.0, ctk.END)

    def save_chart_as_png(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if save_path:
            self.fig.savefig(save_path)
            print(f"圖表已儲存至: {save_path}")

    def export_data_to_csv(self):
        if self.df is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if save_path:
                self.df.to_csv(save_path, index=False)
                print(f"資料已儲存至: {save_path}")

    def show_all_data(self):
        if self.df is not None:
            self.csv_textbox.delete(1.0, ctk.END)
            #self.csv_textbox.insert(ctk.END, self.df.to_string(index=False))
            first_20 = self.y_data[:20]
            self.csv_textbox.insert(ctk.END, f"前 20 筆 Y 資料：\n{first_20}")
            #print(self.y_data[:20])

if __name__ == "__main__":
    app = RealtimePlotApp()
    app.mainloop()
