import numpy as np
import matplotlib.pyplot as plt
import pywt

# 生成示例信號
fs = 1000  # 采樣頻率
t = np.linspace(0, 5, 5 * fs)  # 時間向量
#signal = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 50 * t)
signal = np.sin(2 * np.pi * 5 * t) 
# 模擬50 Hz成分在第2到第3秒間突變
#signal[int(2 * fs):int(3 * fs)] += 2 * np.sin(2 * np.pi * 50 * t[int(2 * fs):int(3 * fs)])

# 只顯示0到2秒的數據
t_range = t[:4 * fs]  # 0 到 2 秒的時間範圍  2
signal_range = signal[:4 * fs]  # 0 到 2 秒的信號範圍   2

# FFT分析
#fft_signal = np.fft.fft(signal_range)
fft_signal = np.fft.fft(signal) / len(signal)

#fft_signal = np.fft.fft(signal_range) / len(signal_range)
frequencies = np.fft.fftfreq(len(t_range), 1/fs)

# 小波變換分析
scales = np.arange(1, 1024)  # 設定尺度範圍128
#小波變換的尺度和頻率是反比的：小的尺度對應高頻，而大的尺度對應低頻。
#這樣設定能夠涵蓋大範圍的頻率分量，從高頻到低頻。
#
coeffs, freqs = pywt.cwt(signal, scales, 'cmor', 1 / fs)

# 顯示結果
plt.figure(figsize=(12, 8))

# 原始信號（時域圖）
plt.subplot(2, 2, 1)
plt.plot(t_range, signal_range, label='Signal in Time Domain')
plt.title("Original Signal (0-2 seconds)")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()

# 設置X軸範圍，讓0秒緊貼Y軸
plt.xlim([0, max(t_range)])  # 設置 X 軸範圍
plt.subplots_adjust(left=0.1)  # 使X軸的0秒靠近Y軸
# FFT頻譜圖
plt.subplot(2, 2, 2)
plt.plot(frequencies[:len(frequencies)//2], np.abs(fft_signal)[:len(frequencies)//2])
plt.title("FFT Spectrum")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Magnitude")
plt.grid(True)

# 小波變換圖
#顏色代表了信號在不同時間和頻率上的 強度（Magnitude）
#藍色（Blue）：表示信號強度最小或接近零。也就是說，在這些區域，信號的強度較弱或幾乎不存在。
#綠色、黃色（Green, Yellow）：信號強度逐漸增強，顯示了中等強度的信號。
#紅色（Red）：表示信號強度最大。這些區域的信號強度非常高，可能表示頻率和時間區域內信號的主要成分或突變。
plt.subplot(2, 2, 3)
plt.imshow(np.abs(coeffs), extent=[0, 4, 1, 128], aspect='auto', cmap='jet')
plt.title("Wavelet Transform")
plt.xlabel("Time [s]")
plt.ylabel("Frequency [Hz]")

# 留出空白區域（不需要的話可移除）
plt.subplot(2, 2, 4)
plt.axis('off')

plt.tight_layout()
plt.show()
