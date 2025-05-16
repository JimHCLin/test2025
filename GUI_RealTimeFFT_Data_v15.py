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
        self.ax_energy.set_title("第三張圖")
        self.ax_energy.set_xlabel("X軸標籤")
        self.ax_energy.set_ylabel("Y軸標籤")

        ###
        

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

        self.export_button = ctk.CTkButton(self.left_frame, text="匯出FFT前五大頻率資料", command=self.export_data_to_csv)
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
        self._process_next_file()  # 啟動第一個檔案處理
        #
        
        ##


    def _process_next_file(self):
        if self.current_index >= self.total_files_length:
            messagebox.showinfo("處理完成", "所有檔案處理完成！")

            ###
            print(f"self.summary_data.append:{self.summary_data}")
            # 儲存總結分析成 Excel
            summary_df = pd.DataFrame(self.summary_data)
            summary_path = os.path.join(self.folder_path, "FFT_批次總結分析.xlsx")
            try:
                summary_df.to_excel(summary_path, index=False)
                messagebox.showinfo("匯出成功", f"FFT 總結已儲存為 Excel:\n{summary_path}")
            except Exception as e:
                messagebox.showerror("匯出錯誤", f"無法匯出 Excel 檔案:\n{e}")
            return
            ###
            #return

        tsv_file = self.tsv_files[self.current_index]
        file_path = os.path.join(self.folder_path, tsv_file)
        self.filename_label.configure(
            text=f"處理檔案: {tsv_file} ({self.current_index + 1}/{self.total_files_length})"
        )

        try:
            self.df = pd.read_csv(file_path, delimiter='\t', encoding='utf-8', header=3)
            self.df.columns = self.df.columns.str.strip()

            date_str = "_".join(tsv_file.split("_")[2:5])
            print(f"檔案日期: {date_str}")
            self.file_date_str= date_str
            #time.sleep(0.5)  # 模擬處理延遲

            if 'Xaxis' not in self.df.columns or 'Yaxis' not in self.df.columns or 'Zaxis' not in self.df.columns:
                messagebox.showerror("錯誤", f"{tsv_file} 檔案缺少必要欄位")
                self.current_index += 1
                self.after(1000, self._process_next_file)
                
                return
            
            print(f"BATCH csv_print(self.df['Xaxis']:{self.df['Xaxis'].head(10)}")
            print(f"BATCHcsv_print(self.df['yaxis']:{self.df['Yaxis'].head(10)}")
            print(f"BATCH  csv_print(self.df['zaxis']:{self.df['Zaxis'].head(10)}")

            # 計算 RMS 與 FFT（略過細節，保持原邏輯）
            rms = np.sqrt(self.df['Xaxis']**2 + self.df['Yaxis']**2 + self.df['Zaxis']**2)
            self.y_data = rms.tolist()
            sample_count = min(len(self.y_data), 85932)
            self.x_data = np.round(0.000128008 + 0.000128 * np.arange(sample_count), 9).tolist()
            self.y_data = self.y_data[:sample_count]
            print(f"BATCH  y_data  RMS :{self.y_data[0:10]}")


            self.ax_time.clear()
            self.ax_time.plot(self.x_data, self.y_data, label="數據")
            self.ax_time.set_title("時域訊號")
            self.ax_time.set_xlabel("時間(秒)")
            self.ax_time.set_ylabel("三軸RMS數值")
            self.ax_time.legend()
            self.ax_time.relim()
            self.ax_time.autoscale_view()

            #self.ax_freq.clear()
            self.compute_and_plot_fft()
            self.show_fft_top()

            # 儲存圖片
            output_image_path = os.path.join(self.folder_path, f"Diagram_{tsv_file}_fft.png")
            self.fig.savefig(output_image_path, dpi=300)

            # 儲存 CSV
            output_csv_path = os.path.join(self.folder_path, f"Frequency_{tsv_file}_fft.csv")
            text_content = self.csv_textbox.get("1.0", "end").strip()
            with open(output_csv_path, "w", encoding="utf-8-sig") as f:
                f.write(text_content)

            # 更新進度條
            self.progress.set((self.current_index + 1) / self.total_files_length)
            ###
            # 收集結果資訊（分析結果、頻率字串、振幅字串、日期字串）
            '''
            self.summary_data.append({
                '檔名': tsv_file,
                '檔案日期': self.file_date_str,
                '分析結果': self.analysis_result,
                'Top5 頻率 (Hz)': self.topFiveFftFreqs.rstrip(','),
                'Top5 振幅': self.topFiveFftAmp.rstrip(','),
            })
            '''
            ###
             # 整理欄位寫入 summary_data
            summary_entry = {
                '檔名': tsv_file,
                '檔案日期': self.file_date_str,
                '分析結果': self.analysis_result,
            }

            # 填入 Top5 頻率與振幅
            for i in range(5):
                freq = self.top_frequencies[i] if i < len(self.top_frequencies) else None
                amp = self.top_magnitudes[i] if i < len(self.top_magnitudes) else None
                summary_entry[f'Top{i+1}_頻率_Hz'] = freq
                summary_entry[f'Top{i+1}_振幅'] = amp

            # 填入基頻與最大振幅分析資料
            summary_entry['基頻_Hz'] = getattr(self, 'base_freq', None)
            summary_entry['基頻振幅'] = getattr(self, 'base_amp', None)
            summary_entry['最大頻率_Hz'] = getattr(self, 'max_freq', None)
            summary_entry['最大振幅'] = getattr(self, 'max_amp', None)
            summary_entry['最大與基頻振幅差異_%'] = getattr(self, 'percent_diff', None)
            summary_entry['每天的rms']= getattr(self, 'rms_value', None)
            

            self.summary_data.append(summary_entry)
            ###
            print(f"self.summary_data:{self.summary_data}")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"處理檔案 {tsv_file} 時出錯: {e}")

        # 准備處理下一個
        self.current_index += 1
        self.after(1000, self._process_next_file)

    

    def load_csv(self):
        self.progress.set(0)       # 重設進度條
        self.csv_textbox.delete(1.0, ctk.END)
        #file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        file_path = filedialog.askopenfilename(filetypes=[("CSV/TSV files", "*.csv *.tsv")])
        if file_path:
            filename = os.path.basename(file_path)
            self.filename_label.configure(text=f"讀取檔案: {filename}")
            self.filename=filename
            ##
            self.file_date_str = "_".join(filename.split("_")[2:5])
            print(f"load_csv檔案日期: {self.file_date_str}")
            ##
            try:
                #self.df = pd.read_csv(file_path, encoding='big5',header=3)  # 加入 encoding 解決中文亂碼/錯誤
                if file_path.lower().endswith('.tsv'):
                    self.df = pd.read_csv(file_path, delimiter='\t', encoding='utf-8', header=3)
                else:
                    self.df = pd.read_csv(file_path, encoding='big5', header=3)
            except UnicodeDecodeError:
                try:
                    #self.df = pd.read_csv(file_path, encoding='utf-8-sig')
                    if file_path.lower().endswith('.tsv'):
                        self.df = pd.read_csv(file_path, delimiter='\t', encoding='utf-8-sig', header=3)
                    else:
                        self.df = pd.read_csv(file_path, encoding='utf-8-sig', header=3)
                except Exception as e:
                    print(f"讀取失敗：{e}")
                    messagebox.showerror("讀取失敗", f"無法讀取檔案:\n{e}")
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

            #self.csv_textbox.delete(1.0, ctk.END)
            #self.csv_textbox.insert(ctk.END, self.df.to_string(index=False))

            # 只讀取 B6:D85937 的資料
            #self.df = self.df.iloc[5:85937]  # 取 B6~D85937 對應第6~85937列
            self.df = self.df.iloc[0:85937]  # 取 B6~D85937 對應第6~85937列

            # 移除欄位名稱空白
            self.df.columns = self.df.columns.str.strip()

            # 確保 Xaxis、Yaxis、Zaxis 欄位存在
            if 'Xaxis' not in self.df.columns or 'Yaxis' not in self.df.columns or 'Zaxis' not in self.df.columns:
                print("錯誤：CSV 檔案缺少 Xaxis、Yaxis 或 Zaxis 欄位")
                return
            ####
            #print(f"沒轉數值load csv_print(self.df['Xaxis']:{self.df['Xaxis'].head(10)}")
            #print(f"沒轉數值load csv_print(self.df['yaxis']:{self.df['Yaxis'].head(10)}")
            #print(f"沒轉數值load csv_print(self.df['zaxis']:{self.df['Zaxis'].head(10)}")
            ####
            # 將欄位轉為數值型態
            self.df['Xaxis'] = pd.to_numeric(self.df['Xaxis'], errors='coerce')
            self.df['Yaxis'] = pd.to_numeric(self.df['Yaxis'], errors='coerce')
            self.df['Zaxis'] = pd.to_numeric(self.df['Zaxis'], errors='coerce')
            self.df = self.df.dropna(subset=['Xaxis', 'Yaxis', 'Zaxis'])

            ###
            #print(f"load csv_print(self.df['Xaxis']:{self.df['Xaxis'].head(10)}")
            #print(f"load csv_print(self.df['yaxis']:{self.df['Yaxis'].head(10)}")
            #print(f"load csv_print(self.df['zaxis']:{self.df['Zaxis'].head(10)}")
            ###

            # 計算 RMS = sqrt(Xaxis² + Yaxis² + Zaxis²)
            rms = np.sqrt(self.df['Xaxis']**2 + self.df['Yaxis']**2 + self.df['Zaxis']**2)

            # 計算每個時間點的合成加速度大小
            acceleration_magnitude = np.sqrt(self.df['Xaxis']**2 + self.df['Yaxis']**2 + self.df['Zaxis']**2)
            print(f"acceleration_magnitude:{ acceleration_magnitude[0:10]}")
            #這段程式碼的確只是在每一個時間點上，將 X、Y、Z 三個軸的加速度分量平方並相加，再開根號。
            #這會給你每一個時間點的「合成加速度」，即一個向量的大小。但這並不是 RMS 的計算方法。
            #23:00:06:0001	654	243	-487   427716+59049+237169=723934 ==>開根號  rms=850.84
            self.y_data = acceleration_magnitude.tolist()#有85932多筆accTotal合成加速度
            print(f"length  self.y_data:{ len(self.y_data)}")#85932
            print(f"self.y_data:{ self.y_data[0:10]}")
            print(f"self.y_data list type:{type(self.y_data)}")
            #self.y_data = rms.tolist()#有85932多筆accTotal合成加速度 的資料
            #self.y_data=[1, 2, 3]
            self.y_data_array = np.array(self.y_data)
            # 計算 RMS 值
            self.rms_value = 0.0
            self.rms_value = np.sqrt(np.mean(self.y_data_array**2)) #把一天裡的85932筆合成加速度 算出來一個rms, 一天只會有一個rms

            # 輸出結果
            print("每個時間點的合成加速度頭十筆: ",acceleration_magnitude[0:10])
            rms_result=f"RMS 值 :{self.rms_value}\n"
            #RMS 持續升高 → 表示馬達振動強度變大 → 代表健康狀況可能正在惡化
            #self.analysis_result = f"基頻: {base_freq:.2f} Hz，基頻振幅: {base_amp:.2f}\n"
            print("RMS 值 : ", self.rms_value)
            self.csv_textbox.delete(1.0, ctk.END)
            self.csv_textbox.insert(ctk.END, rms_result)

            # 固定時間軸 X
            sample_count = min(len(self.y_data), 85932)
            self.x_data = np.round(0.000128008 + 0.000128 * np.arange(sample_count), 9).tolist()
            self.y_data = self.y_data[:sample_count]
            print(f"LOAD CSV y_data  合成加速度(不是RMS) :{self.y_data[0:10]}")

            self.ax_time.clear()
            self.ax_time.plot(self.x_data, self.y_data, label="數據")  #self.y_data裡面有85932筆accTotal合成加速度
            self.ax_time.set_title("時域訊號")
            self.ax_time.set_xlabel("時間(秒)")
            self.ax_time.set_ylabel("accTotal合成加速度數值")
            self.ax_time.legend()
            self.ax_time.relim()
            self.ax_time.autoscale_view()

            # self.ax_freq.clear()
            self.compute_and_plot_fft()

            #self.canvas.draw()
            messagebox.showinfo("載入成功", f"成功讀取檔案:\n{filename}")
            print("列出fft頻率")
            self.show_fft_top()

    def compute_and_plot_fft(self):
        self.ax_freq.clear()
        self.ax_energy.clear()
        if len(self.y_data) < 2:
            return

        # FFT計算
        ##self.y_data裡面有85932筆accTotal合成加速度
        signal_fft = np.fft.fft(self.y_data)  # 計算震幅
        print(f"signal_fft:{signal_fft}")# 有實數和虛數  1.27685987e+08      +0.j         1.31985116e+05 -358696.95646056j...
        print(f"length signal_fft:{len(signal_fft)}")#85932
        dt = self.x_data[1] - self.x_data[0]  # 時間間隔
        print(f"dt:{dt}")#0.000128
        frequencies_fft = np.fft.fftfreq(len(self.y_data), dt)
        #頻率解析度 Δf 是什麼？
        #Δf 是 FFT 頻率軸中每一個頻點之間的間距（單位是 Hz）
        #代表你能夠區分多細的頻率變化
        #Δf=fs/N
        print(f"frequencies_fft:{frequencies_fft}")# 0.          0.09091491  0.18182982    ==>Δf= fs/N,  Δf:頻率解析度(FFT 頻率軸每一階的差距),N:資料點數  ,fs:採樣頻率
        print(f"len frequencies_fft:{len(frequencies_fft)}") #85932
        magnitude = np.abs(signal_fft)
        print(f"magnitude:{magnitude}")#[1.27685987e+08 3.82208814e+05 9.11414374e+05...
        print(f"len magnitude:{len(magnitude)}") #85932

        # 只選擇正頻率
        positive_frequencies = frequencies_fft[:len(frequencies_fft) // 2]
        positive_magnitude = magnitude[:len(magnitude) // 2]

        # 找出峰值
        peaks, _ = find_peaks(positive_magnitude, height=0)
        peak_frequencies = positive_frequencies[peaks]
        peak_magnitudes = positive_magnitude[peaks]

        # 儲存前 5 大峰值頻率和幅度
        sorted_indices = np.argsort(peak_magnitudes)[-5:][::-1]
        self.top_frequencies = peak_frequencies[sorted_indices]
        self.top_magnitudes = peak_magnitudes[sorted_indices]

        # 繪製頻域圖（FFT）
        self.ax_freq.plot(positive_frequencies, positive_magnitude, label="FFT 結果")
        self.ax_freq.scatter(self.top_frequencies, self.top_magnitudes, color='red', label="前 5 大峰值")

        # 標註前 5 大峰值
        colors = ['blue', 'green', 'orange', 'purple', 'brown']
        for i in range(len(self.top_frequencies)):
            freq = self.top_frequencies[i]
            mag = self.top_magnitudes[i]
            label = f"第{i+1}峰值{freq:.2f} Hz"

            x_offset = freq * 2 if freq * 3 < max(positive_frequencies) else 100
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
        self.ax_freq.set_xlim(0, max(positive_frequencies))
        self.ax_freq.set_ylim(0, 5e7)
        self.ax_freq.legend()
        ###
        # 計算每個時間點的瞬時能量
        instantaneous_energy = np.square(np.abs(self.y_data))

        # 計算總能量（累加所有瞬時能量）
        total_energy = np.cumsum(instantaneous_energy)

        # 繪製總能量圖
        self.ax_energy.plot(self.x_data, total_energy, label="總能量", color='purple')
        self.ax_energy.set_title("時域總能量圖")
        self.ax_energy.set_xlabel("時間(秒)")
        self.ax_energy.set_ylabel("累積能量")
        self.ax_energy.legend()
        # 假設您知道最大累積能量範圍，您可以手動設定範圍
        self.ax_energy.set_ylim(0, 5e11)  # 這裡以 1e5 為例，根據您的數據調整

        # 如果您想自動調整 y 軸範圍，可以設置一些條件來確定範圍
        # 例如，設置 y 軸範圍為總能量的最大值的某個比例
        #max_total_energy = np.max(total_energy)
        #self.ax_energy.set_ylim(0, max_total_energy * 1.2)  # 設置最大值為最大總能量的 120%

        ###
        '''
        # 計算能量並繪製
        # 這裡假設能量等於振幅的平方
        energy = np.square(np.abs(self.y_data))  # 計算能量

        # 繪製能量圖
        self.ax_energy.plot(self.x_data, energy, label="信號能量", color='purple')
        self.ax_energy.set_title("時域能量圖")
        self.ax_energy.set_xlabel("時間(秒)")
        self.ax_energy.set_ylabel("能量")
        self.ax_energy.legend()
        '''
        # 顯示結果
        peak_info = "前 5 大頻率與幅度:\n"
        for f, m in zip(self.top_frequencies, self.top_magnitudes):
            peak_info += f"頻率 {f:.4f} Hz，振幅 {m:.2f}\n"

        self.fft_top_df = pd.DataFrame({
            'Peak_Rank': range(1, 6),
            'Frequency_Hz': self.top_frequencies,
            'Amplitude': self.top_magnitudes
        })

        self.fft_top_df['Peak_Rank'] = self.fft_top_df['Peak_Rank'].astype(int)

        # 計算最大振幅與基頻差異
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

        self.analysis_result = f"基頻: {base_freq:.2f} Hz，基頻振幅: {base_amp:.2f}\n"
        self.analysis_result += f"最大振幅: {max_amp:.2f}（頻率: {max_freq:.2f} Hz）\n"
        self.analysis_result += f"最大振幅與基頻差異: {percent_diff:.2f}%\n"

        # 儲存為實體變數供其他函數使用
        self.base_freq = base_freq
        self.base_amp = base_amp
        self.max_freq = max_freq
        self.max_amp = max_amp
        self.percent_diff = percent_diff
        # 顯示結果到文字框
        #self.csv_textbox.delete(1.0, ctk.END)
        self.csv_textbox.insert(ctk.END, self.analysis_result)
        
        # 更新畫布
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
