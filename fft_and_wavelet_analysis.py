import numpy as np
import matplotlib.pyplot as plt
import pywt

# 生成示例信號
fs = 1000  # 采樣頻率
t = np.linspace(0, 2, 5 * fs)  # 時間向量
signal = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 50 * t)

# 模擬50 Hz成分在第2到第3秒間突變
signal[int(2 * fs):int(3 * fs)] += 2 * np.sin(2 * np.pi * 50 * t[int(2 * fs):int(3 * fs)])

# FFT分析
fft_signal = np.fft.fft(signal)
frequencies = np.fft.fftfreq(len(t), 1/fs)

# 小波變換分析
coeffs, freqs = pywt.cwt(signal, np.arange(1, 128), 'cmor', 1/fs)

# 顯示結果
plt.figure(figsize=(12, 8))

# 原始信號（時域圖）
plt.subplot(2, 2, 1)
plt.plot(t, signal, label='Signal in Time Domain')
plt.title("Original Signal")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()

# FFT頻譜圖
plt.subplot(2, 2, 2)
plt.plot(frequencies[:len(frequencies)//2], np.abs(fft_signal)[:len(frequencies)//2])
plt.title("FFT Spectrum")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude")
plt.grid(True)

# 小波變換圖
plt.subplot(2, 2, 3)
plt.imshow(np.abs(coeffs), extent=[0, 5, 1, 128], aspect='auto', cmap='jet')
plt.title("Wavelet Transform")
plt.xlabel("Time [s]")
plt.ylabel("Frequency [Hz]")

# 留出空白區域（不需要的話可移除）
plt.subplot(2, 2, 4)
plt.axis('off')

plt.tight_layout()
plt.show()
