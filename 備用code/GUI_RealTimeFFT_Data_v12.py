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
        self.fft_top_df = pd.DataFrame()  # 用來儲存 FFT 前五大頻率與振幅
        self.filename=""
        self.analysis_result = ""
        self.topFiveFftFreqs = ""
        self.topFiveFftAmp = ""

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
        self.print_button.pack(side="top", padx=5, pady=5)

        self.export_button = ctk.CTkButton(self.left_frame, text="匯出FFT前五大頻率資料", command=self.export_data_to_csv)
        self.export_button.pack(side="top", padx=5, pady=5)
        
        self.save_button = ctk.CTkButton(self.left_frame, text="儲存圖表", command=self.save_chart_as_png)
        self.save_button.pack(side="top", padx=5, pady=5)

        self.show_fft_button = ctk.CTkButton(self.left_frame, text="顯示 FFT 前五大", command=self.show_fft_top)
        self.show_fft_button.pack(side="top", padx=5, pady=5)

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

        # 讀取資料夾中的所有TSV檔案
        tsv_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.tsv')]
        
        if not tsv_files:
            messagebox.showerror("錯誤", "資料夾內沒有TSV檔案")
            return
        
        # 依序讀取TSV檔案並處理
        for tsv_file in tsv_files:
            file_path = os.path.join(folder_path, tsv_file)
            self.filename_label.configure(text=f"處理檔案: {tsv_file}")
            try:
                self.df = pd.read_csv(file_path, delimiter='\t', encoding='utf-8', header=3)
                self.df.columns = self.df.columns.str.strip()
                ###
                date_str = "_".join(tsv_file.split("_")[2:5])
                print(f"檔案日期: {date_str}")
                ###

                # 確保欄位存在
                if 'Xaxis' not in self.df.columns or 'Yaxis' not in self.df.columns or 'Zaxis' not in self.df.columns:
                    messagebox.showerror("錯誤", f"{tsv_file} 檔案缺少必要欄位 (Xaxis, Yaxis, Zaxis)")
                    continue
                
                # 計算RMS
                rms = np.sqrt(self.df['Xaxis']**2 + self.df['Yaxis']**2 + self.df['Zaxis']**2)
                self.y_data = rms.tolist()
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
                self.show_fft_top()

                # 儲存圖表為PNG   
                output_image_path = os.path.join(folder_path, f"Diagram_RMS_XYZaxis_1號機_85932筆資料_{tsv_file}_fft.png")
                ########
                if output_image_path:
                    # 儲存圖表為 PNG 影像檔
                    print(f"save_path:{output_image_path}")
                    try:
                        self.fig.savefig(output_image_path, dpi=300)  # 300 dpi 可提供高解析度
                        #messagebox.showinfo("圖表已儲存", f"圖表已儲存至:\n{output_image_path}")
                    except Exception as e:
                        messagebox.showerror("錯誤", f"儲存圖表時發生錯誤: {str(e)}")
                else:
                    messagebox.showwarning("儲存取消", "您已取消儲存操作。")

                ######
                #self.fig.savefig(output_image_path)
                #print(f"圖表已儲存: {output_image_path}")

                # 儲存FFT資料為CSV
                output_csv_path = os.path.join(folder_path, f"Frequency_Amplitude_RMS_XYZaxis_1號機_85932筆資料_{tsv_file}_fft.csv")
                ##
                if output_csv_path:
                    # 讀取文字框的所有文字（從 1.0 到結尾）
                    text_content = self.csv_textbox.get("1.0", "end").strip()
                    # 寫入文字到檔案
                    with open(output_csv_path, "w", encoding="utf-8-sig") as f:
                        f.write(text_content)
                    #self.fft_top_df.to_csv(save_path, index=False, encoding='utf-8-sig')
                    #messagebox.showinfo("匯出成功", f"FFT 頻率資料已匯出至:\n{output_csv_path}")
                else:
                    messagebox.showwarning("儲存取消", "無儲存路徑!")      
                ###########

                ##
                #self.fft_top_df.to_csv(output_csv_path, index=False)
                #print(f"CSV資料已儲存: {output_csv_path}")

            except Exception as e:
                messagebox.showerror("錯誤", f"處理檔案 {tsv_file} 時出錯: {e}")
                continue

        messagebox.showinfo("處理完成", "所有檔案處理完成！")

    def load_csv(self):
        self.csv_textbox.delete(1.0, ctk.END)
        #file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        file_path = filedialog.askopenfilename(filetypes=[("CSV/TSV files", "*.csv *.tsv")])
        if file_path:
            filename = os.path.basename(file_path)
            self.filename_label.configure(text=f"讀取檔案: {filename}")
            self.filename=filename
            ##
            date_str = "_".join(filename.split("_")[2:5])
            print(f"load_csv檔案日期: {date_str}")
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

            #self.canvas.draw()
            messagebox.showinfo("載入成功", f"成功讀取檔案:\n{filename}")
            print("列出fft頻率")
            self.show_fft_top()

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
        ###
        # 加上標註前 5 大峰值
        colors = ['blue', 'green', 'orange', 'purple', 'brown']
        for i in range(len(self.top_frequencies)):
            freq = self.top_frequencies[i]
            mag = self.top_magnitudes[i]
            label = f"第{i+1}峰值{freq:.2f} Hz"
            #label = f"第{i+1}"
            
            # 根據頻率位置動態調整標註位置
            #x_offset = 500 if freq < max(positive_frequencies) - 20 else -30
            x_offset = freq*2 if freq*3< max(positive_frequencies)  else 100
            print(f"max(positive_frequencies) :{max(positive_frequencies) }")
            #y_offset = mag * 1.2 if mag < 5e7*5 else mag*1.1
            #y_offset = mag * 0.6 if mag < 5e7 else mag*0.1
            #y_offset = mag * 0.3+freq*50000 if freq*4 < max(positive_frequencies)  else mag * 0.3
            if freq * 3 < max(positive_frequencies):
                #y_offset = mag * 0.2+freq * 50000
                y_offset = mag *1
                print(f"頻率 y_offset = mag * 0.3 + freq * 50000")
            else:
                y_offset = mag * 1
                print(f"頻率 {freq:.2f} 超過界限，僅使用基本 y_offset={y_offset:.2f}")
            print(f"mag:{mag}")
            #y_offset = 5e7  # 避免重疊可微調此值
            
            self.ax_freq.annotate(
                label,
                xy=(freq, mag),
                xytext=(freq + x_offset, mag + y_offset),
                arrowprops=dict(facecolor=colors[i % len(colors)], arrowstyle='->'),
                fontsize=9,
                color=colors[i % len(colors)]
            )
        ###
        self.ax_freq.set_title("頻域(FFT)訊號")
        self.ax_freq.set_xlabel("頻率(Hz)")
        self.ax_freq.set_ylabel("振幅")
        self.ax_freq.set_xlim(0, max(positive_frequencies))
        #self.ax_freq.set_ylim(0,max(positive_magnitude))
        print(f"max(positive_magnitude):{max(positive_magnitude)}")
        self.ax_freq.set_ylim(0, 5e7)
        self.ax_freq.legend()

        peak_info = "前 5 大頻率與幅度:\n"
        for f, m in zip(self.top_frequencies, self.top_magnitudes):
            peak_info += f"頻率 {f:.4f} Hz，振幅 {m:.2f}\n"
        ###
        self.fft_top_df = pd.DataFrame({
            'Peak_Rank': range(1, 6),
            'Frequency_Hz': self.top_frequencies,
            'Amplitude': self.top_magnitudes
        })
        self.analysis_result = ""
        # 計算最大振幅與基頻差異
        valid_indices = [i for i, f in enumerate(self.top_frequencies) if f > 30 and f< 62 ]
        #analysis_result = ""

        if valid_indices:
            base_index = valid_indices[np.argmin([self.top_frequencies[i] for i in valid_indices])]
            base_freq = self.top_frequencies[base_index]
            base_amp = self.top_magnitudes[base_index]

            max_index = np.argmax(self.top_magnitudes)
            max_freq = self.top_frequencies[max_index]
            max_amp = self.top_magnitudes[max_index]

            percent_diff = ((max_amp - base_amp) / base_amp) * 100
            # 清空 analysis_result
            ###暫時註解掉
            '''
            self.analysis_result = ""
            self.analysis_result += f"\n基頻: {base_freq:.2f} Hz，基頻振幅: {base_amp:.2f}\n"
            self.analysis_result += f"最大振幅: {max_amp:.2f}（頻率: {max_freq:.2f} Hz）\n"
            self.analysis_result += f"最大振幅與基頻差異: {percent_diff:.2f}%\n"
            '''
            ###暫時註解掉
        else:
            self.analysis_result += "找不到大於 30 Hz 且小於62 Hz 的基頻\n"
            base_amp=1e10;
            base_freq=-10000;
            ##
            max_index = np.argmax(self.top_magnitudes)
            max_freq = self.top_frequencies[max_index]
            max_amp = self.top_magnitudes[max_index]
            percent_diff = ((max_amp - base_amp) / base_amp) * 100
            ##
        #self.analysis_result = ""
        self.analysis_result += f"基頻: {base_freq:.2f} Hz，基頻振幅: {base_amp:.2f}\n"
        self.analysis_result += f"最大振幅: {max_amp:.2f}（頻率: {max_freq:.2f} Hz）\n"
        self.analysis_result += f"最大振幅與基頻差異: {percent_diff:.2f}%\n"
        # 顯示到文字框
        self.csv_textbox.delete(1.0, ctk.END)
        self.csv_textbox.insert(ctk.END, self.analysis_result)
        self.canvas.draw()


    def show_fft_top(self):
        if hasattr(self, 'fft_top_df') and not self.fft_top_df.empty:
            info = "FFT 前 5 大頻率與振幅：\n"
            for idx, row in self.fft_top_df.iterrows():
                info += f"{row['Peak_Rank']}==> 頻率 : {row['Frequency_Hz']:.4f} Hz，振幅 : {row['Amplitude']:.2f}\n"
                self.topFiveFftFreqs += f"{row['Frequency_Hz']:.4f},"
                self.topFiveFftAmp += f"{row['Amplitude']:.2f},"
            #self.csv_textbox.delete(1.0, ctk.END)

            self.csv_textbox.insert(ctk.END, info)
        else:
            messagebox.showinfo("資訊", "目前尚未計算 FFT 或資料不足")

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
        self.canvas.draw()
        self.csv_textbox.delete(1.0, ctk.END)
        # 清空 analysis_result
        self.analysis_result = ""

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
