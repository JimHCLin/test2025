import numpy as np
import matplotlib.pyplot as plt
import pywt

# 基本設定
fs = 1000  # 采樣頻率 (Hz)
t = np.linspace(0, 1000, 1000 * fs)  # 時間向量 (0-1000 秒)
signal = np.sin(2 * np.pi * 5 * t)  # 基本信號：5 Hz

# 只顯示0到1000秒的數據
t_range = t  # 0 到 1000 秒的時間範圍
signal_range = signal  # 0 到 1000 秒的信號範圍

# FFT分析
fft_signal = np.fft.fft(signal_range) / len(signal_range)
frequencies = np.fft.fftfreq(len(t_range), 1 / fs)

# 小波變換分析
scales = np.arange(1, 1024)#128  # 設定尺度範圍
coeffs, freqs = pywt.cwt(signal_range, scales, 'cmor', 1 / fs)

# 顯示結果
plt.figure(figsize=(12, 8))

# 原始信號（時域圖）
plt.subplot(2, 2, 1)
plt.plot(t_range, signal_range, label='Signal in Time Domain')
plt.title("Original Signal (0-1000 seconds)")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()

# FFT頻譜圖
plt.subplot(2, 2, 2)
plt.plot(frequencies[:len(frequencies) // 2], np.abs(fft_signal)[:len(frequencies) // 2])
plt.title("FFT Spectrum")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude")
plt.grid(True)

# 小波變換圖
plt.subplot(2, 2, 3)
plt.imshow(np.abs(coeffs), extent=[0, 1000, 1, 128], aspect='auto', cmap='jet')
plt.title("Wavelet Transform")
plt.xlabel("Time [s]")
plt.ylabel("Frequency [Hz]")

# 留出空白區域（不需要的話可移除）
plt.subplot(2, 2, 4)
plt.axis('off')

plt.tight_layout()
plt.show()
