import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Microsoft JhengHei'  # 設定中文字型
# 參數設定
fs = 1000  # 取樣頻率 1000 Hz
t = np.linspace(0, 1, fs, endpoint=False)  # 1 秒時間向量

# 產生訊號：5 Hz 與 50 Hz 正弦波
signal_5hz =2* np.sin(2 * np.pi * 5 * t)
signal_50hz = 10 * np.sin(2 * np.pi * 170 * t)  # 50 Hz 振幅放大為 5 倍

# 合成訊號
combined_signal = signal_5hz + signal_50hz

# FFT 計算
N = len(combined_signal)
fft_values = np.fft.fft(combined_signal)
fft_magnitude = np.abs(fft_values) / N * 2  # 振幅歸一化（乘2因只取正頻率）
freq = np.fft.fftfreq(N, d=1/fs)

# 只取正頻率範圍
pos_mask = freq >= 0
freq = freq[pos_mask]
fft_magnitude = fft_magnitude[pos_mask]

# 繪圖
plt.figure(figsize=(12, 5))

# 時域圖
plt.subplot(1, 2, 1)
plt.plot(t, combined_signal, label='合成訊號 (5 Hz + 50 Hz)')
#plt.plot(t, signal_5hz, linestyle='--', label='5 Hz 信號')
#plt.plot(t, signal_50hz, linestyle='--', label='50 Hz 信號 (振幅較大)')
plt.xlabel('時間 (秒)')
plt.ylabel('振幅')
plt.title('時域波形')
plt.legend()
plt.grid(True)

# 頻域圖
plt.subplot(1, 2, 2)
plt.stem(freq, fft_magnitude, basefmt=" ")
plt.xlim(0, 100)
plt.xlabel('頻率 (Hz)')
plt.ylabel('振幅')
plt.title('頻譜圖')
plt.grid(True)

plt.tight_layout()
plt.show()
