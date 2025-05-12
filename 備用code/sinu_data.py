import numpy as np
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
# 設定中文字型
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
matplotlib.rcParams['axes.unicode_minus'] = False

# 參數設定
sampling_rate = 1000  # 采樣率，1000 Hz
duration = 1  # 信號時長，1 秒
frequencies = [50, 150, 300]  # 三個頻率成分，50 Hz, 150 Hz, 300 Hz

# 生成時間軸
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# 生成時域信號 (由多個正弦波組成)
signal = np.sum([np.sin(2 * np.pi * f * t) for f in frequencies], axis=0)

# 創建 DataFrame 並保存為 CSV
df = pd.DataFrame({'時間': t, '數值': signal})
df.to_csv('signal.csv', index=False)

# 進行傅立葉轉換（FFT）
signal_fft = np.fft.fft(signal)
frequencies_fft = np.fft.fftfreq(len(signal), 1/sampling_rate)

# 計算頻域的幅度
magnitude = np.abs(signal_fft)

# 只顯示正頻率部分
positive_frequencies = frequencies_fft[:len(frequencies_fft)//2]
positive_magnitude = magnitude[:len(magnitude)//2]

# 繪製時域信號和頻域圖
plt.figure(figsize=(12, 6))

# 時域信號
plt.subplot(2, 1, 1)
plt.plot(t, signal)
plt.title("時域信號")
plt.xlabel("時間 (秒)")
plt.ylabel("數值")

# 頻域信號 (FFT)
plt.subplot(2, 1, 2)
plt.plot(positive_frequencies, positive_magnitude)
plt.title("頻域 (FFT) 結果")
plt.xlabel("頻率 (Hz)")
plt.ylabel("幅度")
plt.xlim(0, 400)  # 限制頻率範圍，以便更清楚查看峰值

plt.tight_layout()
plt.show()
