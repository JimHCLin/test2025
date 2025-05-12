import customtkinter as ctk
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.filedialog as filedialog
from scipy.signal import find_peaks
import os  # 檔案名稱處理

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
                self.df = pd.read_csv(file_path, encoding='big5')  # 加入 encoding 解決中文亂碼/錯誤
            except UnicodeDecodeError:
                try:
                    self.df = pd.read_csv(file_path, encoding='utf-8-sig')
                except Exception as e:
                    print(f"讀取失敗：{e}")
                    return

            self.csv_textbox.delete(1.0, ctk.END)
            self.csv_textbox.insert(ctk.END, self.df.to_string(index=False))

            if '時間' not in self.df.columns or '數值' not in self.df.columns:
                print("CSV 檔案缺少 '時間' 或 '數值' 欄位")
                return

            self.df['時間'] = pd.to_numeric(self.df['時間'], errors='coerce')
            self.df['數值'] = pd.to_numeric(self.df['數值'], errors='coerce')
            self.df = self.df.dropna(subset=['時間', '數值'])

            self.x_data = self.df['時間'].tolist()
            self.y_data = self.df['數值'].tolist()

            self.ax_time.clear()
            self.ax_time.plot(self.x_data, self.y_data, label="數據")
            self.ax_time.set_title("時域信號")
            self.ax_time.set_xlabel("時間 (秒)")
            self.ax_time.set_ylabel("數值")
            self.ax_time.legend()
            self.ax_time.relim()
            self.ax_time.autoscale_view()

            self.ax_freq.clear()
            self.compute_and_plot_fft()
            #self.ax_freq.relim()
            #self.ax_freq.autoscale_view()

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

        #print("頻域峰值:")
        #for freq, mag in zip(peak_frequencies, peak_magnitudes):
            #print(f"頻率: {freq:.2f} Hz, 幅度: {mag:.2f}")

        self.ax_freq.plot(positive_frequencies, positive_magnitude, label="FFT 結果")
        self.ax_freq.scatter(peak_frequencies, peak_magnitudes, color='red', label="峰值")
        self.ax_freq.set_title("頻域 (FFT) 結果")
        self.ax_freq.set_xlabel("頻率 (Hz)")
        self.ax_freq.set_ylabel("幅度")
        self.ax_freq.set_xlim(0, max(positive_frequencies))
        self.ax_freq.set_ylim(0, 5e7)  # 加這行固定 Y 軸最大值為 1×10^8
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
                self.ax_time.relim()
                self.ax_time.autoscale_view()

                self.compute_and_plot_fft()
                #self.ax_freq.relim()
                #self.ax_freq.autoscale_view()

                self.canvas.draw()
                self.index += 1

            self.after(500, self.update_plot)

    def print_all_data(self):
        content = "X 資料（時間）:\n" + str(self.x_data) + "\n\n"
        content += "Y 資料（數值）:\n" + str(self.y_data)
        self.csv_textbox.delete(1.0, ctk.END)
        self.csv_textbox.insert(ctk.END, content)

    def save_chart_as_png(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)
            print(f"圖表已儲存為 {file_path}")

    def export_data_to_csv(self):
        if not self.x_data or not self.y_data:
            print("沒有資料可匯出")
            return
        df = pd.DataFrame({"時間": self.x_data, "數值": self.y_data})
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
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
        self.ax_time.relim()
        self.ax_time.autoscale_view()

        self.compute_and_plot_fft()
        #self.ax_freq.relim()
        #self.ax_freq.autoscale_view()

        self.canvas.draw()

    def clear_data(self):
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
        self.filename_label.configure(text="未載入任何檔案")
        self.canvas.draw()

if __name__ == "__main__":
    app = RealtimePlotApp()
    app.mainloop()
