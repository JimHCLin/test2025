import numpy as np
import matplotlib.pyplot as plt

# 基本設定
fs = 1000  # 採樣率 (Hz)
t = np.linspace(0, 5, 5 * fs)  # 時間向量 (0-5 秒)
base_signal = np.sin(2 * np.pi * 5 * t)  # 基礎信號：5 Hz
full_50hz = np.sin(2 * np.pi * 50 * t)  # 全長的 50 Hz 正弦波
partial_50hz = np.zeros_like(t)
partial_50hz[int(2 * fs):int(3 * fs)] = np.sin(2 * np.pi * 50 * t[int(2 * fs):int(3 * fs)])

# 組合信號
signal_full = base_signal + full_50hz
signal_partial = base_signal + partial_50hz

# FFT 分析
fft_full = np.fft.fft(signal_full)
fft_partial = np.fft.fft(signal_partial)
frequencies = np.fft.fftfreq(len(t), 1 / fs)

# 取正頻率部分
half = len(frequencies) // 2
frequencies = frequencies[:half]
fft_full = np.abs(fft_full[:half])
fft_partial = np.abs(fft_partial[:half])

# 限制在 0~100 Hz 的頻率範圍
mask = frequencies <= 100
frequencies = frequencies[mask]
fft_full = fft_full[mask]
fft_partial = fft_partial[mask]

# 繪圖比較
plt.figure(figsize=(12, 6))
plt.plot(frequencies, fft_full, label='整段 50 Hz', linewidth=2)
plt.plot(frequencies, fft_partial, label='只在 2-3 秒加入 50 Hz', linestyle='--', linewidth=2)
plt.title("FFT 頻譜比較（限制至 100 Hz）")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
