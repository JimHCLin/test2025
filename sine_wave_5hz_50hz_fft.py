import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Microsoft JhengHei'  # 設定中文字型

fs = 1000
t = np.linspace(0, 1, fs, endpoint=False)

signal = np.sin(2 * np.pi * 5 * t) + 5 * np.sin(2 * np.pi * 50 * t)

plt.figure(figsize=(12, 4))
plt.plot(t, signal)
plt.title("時域訊號")
plt.xlabel("時間 (秒)")
plt.ylabel("振幅")
plt.grid(True)
plt.tight_layout()
plt.show()

N = len(signal)
fft_result = np.fft.fft(signal)
freq = np.fft.fftfreq(N, 1/fs)

mask = freq >= 0
freq = freq[mask]
fft_magnitude = np.abs(fft_result[mask]) * 2 / N

plt.figure(figsize=(12, 4))
plt.stem(freq, fft_magnitude, basefmt=" ")  # 移除 use_line_collection
plt.xlim(0, 100)
plt.title("頻域訊號 (FFT 頻譜)")
plt.xlabel("頻率 (Hz)")
plt.ylabel("振幅")
plt.grid(True)
plt.tight_layout()
plt.show()
