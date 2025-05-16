import threading
import time
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
        self.summary_data = []  # 用來儲存所有檔案的分析結果
        self.x_data = []
        self.y_data = []
        self.update_running = False
        self.df = None
        self.index = 0
        self.top_frequencies = []  # 用來儲存前5大頻率
        self.top_magnitudes = []  # 用來儲存前5大幅度
        self.fft_top_df = pd.DataFrame()  # 用來儲存 FFT 前五大頻率與振幅
        self.filename=""
        self.analysis_result = ""
        self.topFiveFftFreqs = ""
        self.topFiveFftAmp = ""
        self.file_date_str= ""
        self.rms_value = 0.0
        self.base_freq = 0
        self.base_amp = 0
        self.max_freq = 0
        self.max_amp = 0
        self.percent_diff = 0


        # 建立圖表
        #self.fig, (self.ax_time, self.ax_freq) = plt.subplots(2, 1, figsize=(6, 6))
        self.fig, (self.ax_time, self.ax_freq, self.ax_energy) = plt.subplots(3, 1, figsize=(6, 6))
        self.ax_time.set_title("時域訊號")
        self.ax_time.set_xlabel("時間(秒)")
        self.ax_time.set_ylabel("三軸RMS數值")

        self.ax_freq.set_title("頻域(FFT)訊號")
        self.ax_freq.set_xlabel("頻率(Hz)")
        self.ax_freq.set_ylabel("振幅")
        ###  0515 新增
        #self.ax_energy.set_title("第三張圖")
        #self.ax_energy.set_xlabel("X軸標籤")
        #self.ax_energy.set_ylabel("Y軸標籤")
        self.ax_energy.set_title("時域總能量圖")
        self.ax_energy.set_xlabel("時間(秒)")
        self.ax_energy.set_ylabel("累積能量")

        self.fig.tight_layout()
        ##
        # 創建並佈局進度條
        # 使用 pack 來佈局進度條
        self.progress = ctk.CTkProgressBar(self, width=300, height=20)
        self.progress.pack(pady=10)
        self.progress.set(0)  # 初始為 0%
        ###

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

        ###
        # 新增按鈕：選擇資料夾並處理所有TSV檔案
        self.batch_process_button = ctk.CTkButton(self.left_frame, text="批次處理資料夾", command=self.batch_process_folder)
        self.batch_process_button.pack(side="top", padx=5, pady=5)
        ###

        self.load_button = ctk.CTkButton(self.left_frame, text="讀取 CSV", command=self.load_csv)
        self.load_button.pack(side="top", padx=5, pady=5)

        self.update_button = ctk.CTkButton(self.left_frame, text="更新資料", command=self.start_update)
        #self.update_button.pack(side="top", padx=5, pady=5)

        self.stop_button = ctk.CTkButton(self.left_frame, text="停止更新", command=self.stop_update)
        #self.stop_button.pack(side="top", padx=5, pady=5)

        self.print_button = ctk.CTkButton(self.left_frame, text="列出目前資料", command=self.print_all_data)
        #self.print_button.pack(side="top", padx=5, pady=5)

        self.export_button = ctk.CTkButton(self.left_frame, text="匯出文字框的所有資訊", command=self.export_data_to_csv)
        self.export_button.pack(side="top", padx=5, pady=5)
        
        self.save_button = ctk.CTkButton(self.left_frame, text="儲存圖表", command=self.save_chart_as_png)
        self.save_button.pack(side="top", padx=5, pady=5)

        self.show_fft_button = ctk.CTkButton(self.left_frame, text="顯示 FFT 前五大", command=self.show_fft_top)
        #self.show_fft_button.pack(side="top", padx=5, pady=5)

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

    def batch_process_folder(self):
        folder_path = filedialog.askdirectory(title="選擇資料夾")
        if not folder_path:
            return

        tsv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.tsv')]
        total_files_length = len(tsv_files)
        print(f"total_files_length:{total_files_length}")

        if total_files_length == 0:
            messagebox.showerror("錯誤", "請選擇至少一個檔案！")
            return

        self.folder_path = folder_path
        self.tsv_files = tsv_files
        self.total_files_length = total_files_length
        self.current_index = 0
        self.summary_data.clear()  # 清除舊資料
        self.progress.set(0)       # 重設進度條
        self.process_next_file()  # 啟動第一個檔案處理
        #

    def is_end_of_batch(self):
        return self.current_index >= self.total_files_length


    def load_tsv_file(self, file_path):
        df = pd.read_csv(file_path, delimiter='\t', encoding='utf-8', header=3)
        df.columns = df.columns.str.strip()
        return df
    
    def validate_axes_columns(self, df, raise_error=False, filename=""):
        required_cols = ['Xaxis', 'Yaxis', 'Zaxis']
        df.columns = df.columns.str.strip()
        for col in required_cols:
            if col not in df.columns:
                if raise_error:
                    raise ValueError(f"缺少必要欄位: {col}")
                else:
                    messagebox.showerror("錯誤", f"{filename} 檔案缺少欄位：{col}")
                    return False
        return True

    def prepare_rms_from_df(self, df):
        acc = self.compute_acceleration_magnitude(df)# 單筆資料的合成加速度
        self.y_data = acc.tolist()#85932筆合成加速度資料
        self.y_data_array = np.array(self.y_data)#85932筆資料

        self.rms_value = self.compute_rms(self.y_data_array)#一天只會有一筆資料 時域
        #RMS 如果持續升高 → 表示馬達振動強度變大 → 代表健康狀況可能正在惡化


        self.csv_textbox.insert(ctk.END, f"RMS 值 :{self.rms_value}\n")


        ####
        #rms_array = np.sqrt(df['Xaxis']**2 + df['Yaxis']**2 + df['Zaxis']**2)
        #self.y_data = rms_array.tolist()#85932筆資料
        sample_count = min(len(self.y_data), 85932)
        self.x_data = np.round(0.000128008 + 0.000128 * np.arange(sample_count), 9).tolist()
        self.y_data = self.y_data[:sample_count]
        #self.rms_value = np.sqrt(np.mean(np.square(self.y_data)))
        #self.rms_value = self.compute_rms(rms_array)#一筆資料

    def plot_time_domain(self, x_data=None, y_data=None):
        self.ax_time.clear()
        x_data = x_data if x_data is not None else self.x_data
        y_data = y_data if y_data is not None else self.y_data
        self.ax_time.plot(x_data, y_data, label="數據")
        self.ax_time.set_title("時域訊號")
        self.ax_time.set_xlabel("時間(秒)")
        self.ax_time.set_ylabel("三軸RMS數值")
        self.ax_time.legend()
        self.ax_time.relim()
        self.ax_time.autoscale_view()

    def save_fft_results(self, tsv_file):
        output_image_path = os.path.join(self.folder_path, f"Diagram_{tsv_file}_fft.png")
        self.fig.savefig(output_image_path, dpi=300)

        output_csv_path = os.path.join(self.folder_path, f"Frequency_{tsv_file}_fft.csv")
        text_content = self.csv_textbox.get("1.0", "end").strip()
        with open(output_csv_path, "w", encoding="utf-8-sig") as f:
            f.write(text_content)

    def append_summary(self, tsv_file):
        entry = {
            '檔名': tsv_file,
            '檔案日期': self.file_date_str,
            '分析結果': self.analysis_result,
            '每天的rms': getattr(self, 'rms_value', None)
        }

        for i in range(5):
            entry[f'Top{i+1}_頻率_Hz'] = self.top_frequencies[i] if i < len(self.top_frequencies) else None
            entry[f'Top{i+1}_振幅'] = self.top_magnitudes[i] if i < len(self.top_magnitudes) else None

        entry['基頻_Hz'] = getattr(self, 'base_freq', None)
        entry['基頻振幅'] = getattr(self, 'base_amp', None)
        entry['最大頻率_Hz'] = getattr(self, 'max_freq', None)
        entry['最大振幅'] = getattr(self, 'max_amp', None)
        entry['最大與基頻振幅差異_%'] = getattr(self, 'percent_diff', None)      

        self.summary_data.append(entry)

    def process_next_file(self):
        if self.is_end_of_batch():
            summary_df = pd.DataFrame(self.summary_data)
            summary_path = os.path.join(self.folder_path, "FFT_批次總結分析.xlsx")
            try:
                summary_df.to_excel(summary_path, index=False)
                messagebox.showinfo("處理完成", f"FFT 總結已儲存為:\n{summary_path}")
            except Exception as e:
                messagebox.showerror("匯出錯誤", f"無法匯出 Excel:\n{e}")
            return
        self.csv_textbox.delete(1.0, ctk.END)
        tsv_file = self.tsv_files[self.current_index]
        file_path = os.path.join(self.folder_path, tsv_file)
        self.filename_label.configure(
            text=f"處理檔案: {tsv_file} ({self.current_index + 1}/{self.total_files_length})"
        )

        try:
            df = self.load_tsv_file(file_path)
            self.file_date_str = "_".join(tsv_file.split("_")[2:5])
            if not self.validate_axes_columns(df, filename=tsv_file):
                self.current_index += 1
                self.after(1000, self.process_next_file)
                return

            self.df = df
            self.prepare_rms_from_df(df)
            
            self.plot_time_domain()

            self.compute_and_plot_fft()
            self.show_fft_top()

            self.save_fft_results(tsv_file)
            self.append_summary(tsv_file)

            self.progress.set((self.current_index + 1) / self.total_files_length)

        except Exception as e:
            messagebox.showerror("錯誤", f"處理檔案 {tsv_file} 時出錯: {e}")

        self.current_index += 1
        self.after(1000, self.process_next_file)

        

    def select_file(self):
        return filedialog.askopenfilename(filetypes=[("CSV/TSV files", "*.csv *.tsv")])

    def read_data(self, file_path):
        try:
            if file_path.lower().endswith('.tsv'):
                df = pd.read_csv(file_path, delimiter='\t', encoding='utf-8', header=3)
            else:
                df = pd.read_csv(file_path, encoding='big5', header=3)
        except UnicodeDecodeError:
            try:
                if file_path.lower().endswith('.tsv'):
                    df = pd.read_csv(file_path, delimiter='\t', encoding='utf-8-sig', header=3)
                else:
                    df = pd.read_csv(file_path, encoding='utf-8-sig', header=3)
            except Exception as e:
                raise ValueError(f"讀取檔案失敗: {e}")
        return df

    def validate_columns(self, df):
        required_cols = ['Xaxis', 'Yaxis', 'Zaxis']
        df.columns = df.columns.str.strip()
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"缺少必要欄位: {col}")

    def prepare_data(self, df):
        df = df.iloc[0:85937]  # 固定範圍
        df['Xaxis'] = pd.to_numeric(df['Xaxis'], errors='coerce')
        df['Yaxis'] = pd.to_numeric(df['Yaxis'], errors='coerce')
        df['Zaxis'] = pd.to_numeric(df['Zaxis'], errors='coerce')
        df = df.dropna(subset=['Xaxis', 'Yaxis', 'Zaxis'])
        return df

    def compute_acceleration_magnitude(self, df):
        return np.sqrt(df['Xaxis']**2 + df['Yaxis']**2 + df['Zaxis']**2)

    def compute_rms(self, data_array):
        return np.sqrt(np.mean(data_array**2))

    def load_csv(self):
        self.progress.set(0)
        self.csv_textbox.delete(1.0, ctk.END)

        file_path = self.select_file()
        if not file_path:
            return

        try:
            filename = os.path.basename(file_path)
            self.filename_label.configure(text=f"讀取檔案: {filename}")
            self.filename = filename
            self.file_date_str = "_".join(filename.split("_")[2:5])

            df = self.read_data(file_path)
            self.validate_axes_columns(df, raise_error=True)
            #self.validate_columns(df)
            df = self.prepare_data(df)

            acc = self.compute_acceleration_magnitude(df)# 單筆資料的合成加速度
            self.y_data = acc.tolist()
            self.y_data_array = np.array(self.y_data)#85932筆資料

            self.rms_value = self.compute_rms(self.y_data_array)#一天只會有一筆資料
            self.csv_textbox.insert(ctk.END, f"RMS 值 :{self.rms_value}\n")

            sample_count = min(len(self.y_data), 85932)
            self.x_data = np.round(0.000128008 + 0.000128 * np.arange(sample_count), 9).tolist()
            self.y_data = self.y_data[:sample_count]

            self.plot_time_domain(self.x_data, self.y_data)
            self.compute_and_plot_fft()
            messagebox.showinfo("載入成功", f"成功讀取檔案:\n{filename}")
            self.show_fft_top()

        except ValueError as e:
            messagebox.showerror("錯誤", str(e))
            print("錯誤:", e)

    def compute_fft(self):
        signal_fft = np.fft.fft(self.y_data)
        dt = self.x_data[1] - self.x_data[0]
        frequencies_fft = np.fft.fftfreq(len(self.y_data), dt)
        magnitude = np.abs(signal_fft)

        # 取正頻率部分
        positive_frequencies = frequencies_fft[:len(frequencies_fft) // 2]
        positive_magnitude = magnitude[:len(magnitude) // 2]
        return positive_frequencies, positive_magnitude
    
    def extract_top_peaks(self, freqs, mags):
        peaks, _ = find_peaks(mags, height=0)
        peak_freqs = freqs[peaks]
        peak_mags = mags[peaks]

        sorted_indices = np.argsort(peak_mags)[-5:][::-1]
        self.top_frequencies = peak_freqs[sorted_indices]
        self.top_magnitudes = peak_mags[sorted_indices]

    def plot_fft(self, freqs, mags):
        self.ax_freq.clear()
        self.ax_freq.plot(freqs, mags, label="FFT 結果")
        self.ax_freq.scatter(self.top_frequencies, self.top_magnitudes, color='red', label="前 5 大峰值")

        colors = ['blue', 'green', 'orange', 'purple', 'brown']
        for i, (freq, mag) in enumerate(zip(self.top_frequencies, self.top_magnitudes)):
            label = f"第{i+1}峰值 {freq:.2f} Hz"
            x_offset = freq * 2 if freq * 3 < max(freqs) else 100
            y_offset = mag * 1
            self.ax_freq.annotate(
                label,
                xy=(freq, mag),
                xytext=(freq + x_offset, mag + y_offset),
                arrowprops=dict(facecolor=colors[i % len(colors)], arrowstyle='->'),
                fontsize=9,
                color=colors[i % len(colors)]
            )

        self.ax_freq.set_title("頻域(FFT)訊號")
        self.ax_freq.set_xlabel("頻率(Hz)")
        self.ax_freq.set_ylabel("振幅")
        self.ax_freq.set_xlim(0, max(freqs))
        self.ax_freq.set_ylim(0, 5e7)
        self.ax_freq.legend()
    
    def plot_energy(self):
        self.ax_energy.clear()
        instantaneous_energy = np.square(np.abs(self.y_data))#self.y_data 是85932筆合成加速度資料
        total_energy = np.cumsum(instantaneous_energy)

        self.ax_energy.plot(self.x_data, total_energy, label="總能量", color='purple')
        self.ax_energy.set_title("時域總能量圖")
        self.ax_energy.set_xlabel("時間(秒)")
        self.ax_energy.set_ylabel("累積能量")
        self.ax_energy.legend()
        self.ax_energy.set_ylim(0, 5e11)
        #正常情況下,total_energy 會是同一個斜率,左下右上的斜線
        #如果出現垂直線或是另一個斜率,就表示在那格個轉折點有異常發生
        ##
        #累積能量的斜率」就是瞬時能量的總和變化速度。
        #斜率平穩 ➜ 表示裝置運作正常，能量釋放穩定。
        # 斜率突然變大（變陡） ➜ 表示有瞬時能量明顯增加，可能有異常（例如撞擊、掉落、機械異音等）。
        #轉折點（斜率變化明顯的位置） ➜ 通常是異常開始發生的時間點。
    
    def analyze_frequency_difference(self):
        valid_indices = [i for i, f in enumerate(self.top_frequencies) if 30 < f < 62]

        if valid_indices:
            base_index = valid_indices[np.argmin([self.top_frequencies[i] for i in valid_indices])]
            base_freq = self.top_frequencies[base_index]
            base_amp = self.top_magnitudes[base_index]
            max_index = np.argmax(self.top_magnitudes)
            max_freq = self.top_frequencies[max_index]
            max_amp = self.top_magnitudes[max_index]
            if abs(max_freq - base_freq) < 2 or base_amp == 0:
                percent_diff = 0
            else:
                percent_diff = ((max_amp - base_amp) / base_amp) * 100
        else:
            self.analysis_result += "找不到大於 30 Hz 且小於62 Hz 的基頻\n"
            base_freq = -10000
            base_amp = 1e10
            max_index = np.argmax(self.top_magnitudes)
            max_freq = self.top_frequencies[max_index]
            max_amp = self.top_magnitudes[max_index]
            percent_diff = ((max_amp - base_amp) / base_amp) * 100

        self.base_freq = base_freq
        self.base_amp = base_amp
        self.max_freq = max_freq
        self.max_amp = max_amp
        self.percent_diff = percent_diff

        self.analysis_result = f"基頻: {base_freq:.2f} Hz，基頻振幅: {base_amp:.2f}\n"
        self.analysis_result += f"最大振幅: {max_amp:.2f}（頻率: {max_freq:.2f} Hz）\n"
        self.analysis_result += f"最大振幅與基頻差異: {percent_diff:.2f}%\n"
    
    def compute_and_plot_fft(self):
        if len(self.y_data) < 2:
            return

        freqs, mags = self.compute_fft()
        self.extract_top_peaks(freqs, mags)
        self.plot_fft(freqs, mags)
        self.plot_energy()
        self.analyze_frequency_difference()

        # 儲存 DataFrame
        self.fft_top_df = pd.DataFrame({
            'Peak_Rank': range(1, 6),
            'Frequency_Hz': self.top_frequencies,
            'Amplitude': self.top_magnitudes
        })
        self.fft_top_df['Peak_Rank'] = self.fft_top_df['Peak_Rank'].astype(int)

        # 顯示結果
        self.csv_textbox.insert(ctk.END, self.analysis_result)
        self.canvas.draw()



    def show_fft_top(self):
        if hasattr(self, 'fft_top_df') and not self.fft_top_df.empty:
            info = "FFT 前 5 大頻率與振幅：\n"
            self.topFiveFftFreqs = ""
            self.topFiveFftAmp = ""
            for idx, row in self.fft_top_df.iterrows():
                freq = row['Frequency_Hz']
                amp = row['Amplitude']
                rank = int(row['Peak_Rank'])
                note = ""
                #
                note=self.classify_frequency(freq)

                # 判斷是否為基頻或倍頻
                '''
                if abs(freq - 60) < 2:  # 接近 60 Hz 視為基頻
                    note = "(基頻)"
                elif abs(freq - 120) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(2x)"
                elif abs(freq - 180) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(3x)"
                elif abs(freq - 240) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(4x)"
                elif abs(freq - 300) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(5x)"
                elif abs(freq - 360) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(6x)"
                elif abs(freq - 420) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(7x)"
                elif abs(freq - 480) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(8x)"
                elif abs(freq - 540) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(9x)"
                elif abs(freq - 600) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(10x)"
                elif abs(freq - 660) < 2:  # 接近 120 Hz 視為2x倍頻
                    note = "(11x)"
                '''
                # 組合訊息
                info += f"第{rank}峰值==> 頻率 : {freq:.4f} Hz{note}，振幅 : {amp:.2f}\n"
                self.topFiveFftFreqs += f"{freq:.4f},"
                self.topFiveFftAmp += f"{amp:.2f},"
                #info += f"第{int(row['Peak_Rank'])}峰值==> 頻率 : {row['Frequency_Hz']:.4f} Hz，振幅 : {row['Amplitude']:.2f}\n"
                #self.topFiveFftFreqs += f"{row['Frequency_Hz']:.4f},"
                #self.topFiveFftAmp += f"{row['Amplitude']:.2f},"
            #self.csv_textbox.delete(1.0, ctk.END)

            self.csv_textbox.insert(ctk.END, info)
        else:
            messagebox.showinfo("資訊", "目前尚未計算 FFT 或資料不足")
    '''
    def classify_frequency(freq):
        for i in range(1, 12):
            if abs(freq - 60 * i) < 2:
                return f"({i}x)"
        return ""
    '''
    def classify_frequency(self, freq, base_freq=60, max_harmonic=11, tolerance=2):
        for i in range(1, max_harmonic + 1):
            if abs(freq - base_freq * i) < tolerance:
                return f"({i}x)"
        return ""

    def start_update(self):
        self.update_running = True
        self.index = 0
        self.update_data()

    def stop_update(self):
        self.update_running = False

    def update_data(self):
        if self.update_running and self.index < len(self.y_data):
            self.index += 1
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

    def clear_data(self):
        self.x_data = []
        self.y_data = []
        self.ax_time.clear()
        self.ax_freq.clear()
        self.ax_energy.clear()
        self.canvas.draw()
        self.csv_textbox.delete(1.0, ctk.END)
        # 清空 analysis_result
        self.analysis_result = ""
        self.fft_top_df = pd.DataFrame()
        self.top_frequencies = []
        self.top_magnitudes = []

    def print_all_data(self):
        self.csv_textbox.delete(1.0, ctk.END)
        self.csv_textbox.insert(ctk.END, self.df.to_string(index=False))


    def save_chart_as_png(self):
        print("輸出圖表")
        if hasattr(self, 'fig') and self.fig is not None:
            original_filename = self.filename_label.cget("text").replace("讀取檔案: ", "").strip()
            base_name = os.path.splitext(original_filename)[0]  # 去掉副檔名
            auto_name = f"Diagram_RMS_XYZaxis_1號機_85932筆資料_{base_name}.png"
            print(f"auto_name:{auto_name}")
            # 顯示保存檔案對話框，設定預設檔案名為 auto_name
            save_path = filedialog.asksaveasfilename(
                initialfile=auto_name,
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")]
            )
            if save_path:
                # 儲存圖表為 PNG 影像檔
                print(f"save_path:{save_path}")
                try:
                    self.fig.savefig(save_path, dpi=300)  # 300 dpi 可提供高解析度
                    messagebox.showinfo("圖表已儲存", f"圖表已儲存至:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("錯誤", f"儲存圖表時發生錯誤: {str(e)}")
            else:
                messagebox.showwarning("儲存取消", "您已取消儲存操作。")
        else:
            messagebox.showwarning("錯誤", "圖表尚未繪製，無法儲存！")

    def export_data_to_csv(self):
        print("輸出檔案")
        if hasattr(self, 'fft_top_df') and not self.fft_top_df.empty:
            original_filename = self.filename_label.cget("text").replace("讀取檔案: ", "").strip()
            base_name = os.path.splitext(original_filename)[0]  # 去掉副檔名
            auto_name = f"Frequency_Amplitude_RMS_XYZaxis_1號機_85932筆資料_{base_name}.csv"

            save_path = filedialog.asksaveasfilename(
                initialfile=auto_name,
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv")]
            )
            if save_path:
                # 讀取文字框的所有文字（從 1.0 到結尾）
                text_content = self.csv_textbox.get("1.0", "end").strip()
                print(f"text_content:{text_content}")
                # 檢查是否有內容
                if not text_content:
                    messagebox.showwarning("儲存失敗", "沒有資料可儲存！")
                    return
                try:
                    # 寫入文字到檔案
                    with open(save_path, "w", encoding="utf-8-sig") as f:
                        f.write(text_content)
                        print(f"檔案已儲存至: {save_path}")
                    #messagebox.showinfo("儲存成功", "檔案已成功儲存")
                    messagebox.showinfo("匯出成功", f"FFT 頻率資料已匯出至:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("儲存錯誤", f"儲存檔案時發生錯誤: {e}")
            else:
                print("eeee")
                messagebox.showwarning("儲存取消", "無儲存路徑!")   
                ###########
            
        else:
            messagebox.showwarning("資料不足", "尚未產生 FFT 頻率資料，無法匯出。")

    

if __name__ == "__main__":
    app = RealtimePlotApp()
    app.mainloop()
