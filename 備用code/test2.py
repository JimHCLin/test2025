import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import random
# 設定中文字型
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
matplotlib.rcParams['axes.unicode_minus'] = False

class RealtimePlotApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("即時數據視覺化")
        self.geometry("600x400")
        ctk.set_appearance_mode("light")

        # 初始化資料
        self.x_data = list(range(50))
        self.y_data = [0] * 50

        # 建立圖表
        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.line, = self.ax.plot(self.x_data, self.y_data, label="數據", color='blue')  # 設定圖例標籤
        self.ax.set_ylim(0, 100)  # 設定 Y 軸範圍 0 到 100
        self.ax.set_xlim(0, 50)   # 設定 X 軸範圍 0 到 50
        self.ax.set_title("即時資料圖")
        
        # 設定 X 軸與 Y 軸標籤與單位
        self.ax.set_xlabel("時間 (秒)")  # X 軸標籤與單位
        self.ax.set_ylabel("數值 (°C)")  # Y 軸標籤與單位
        
        # 顯示圖例
        self.ax.legend()  # 加這一行來顯示圖例
        # 自動調整邊距，避免標籤被遮擋
        self.fig.tight_layout()

        # 將 matplotlib 圖表嵌入 customtkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=20)

        # 啟動定時更新
        self.update_plot()

    def update_plot(self):
        # 模擬即時資料（可改成讀取感測器或串列埠）
        new_value = random.randint(0, 100)
        self.y_data.append(new_value)
        self.y_data.pop(0)

        # 更新圖表
        self.line.set_ydata(self.y_data)
        self.canvas.draw()

        # 每 500 毫秒更新一次
        self.after(500, self.update_plot)

if __name__ == "__main__":
    app = RealtimePlotApp()
    app.mainloop()
