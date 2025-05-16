import numpy as np
import matplotlib.pyplot as plt

# 設定參數
fs = 1000  # 采樣頻率（1000 Hz）
t = np.linspace(0, 1, fs)  # 1秒鐘的時間向量

# 生成5 Hz和50 Hz的正弦波信號
signal_5hz = np.sin(2 * np.pi * 5 * t)
signal_50hz = np.sin(2 * np.pi * 50 * t)

# 疊加5 Hz和50 Hz的信號
combined_signal = signal_5hz + signal_50hz

# 繪製疊加信號
plt.figure(figsize=(10, 6))
plt.plot(t, combined_signal, label="Combined Signal (5 Hz + 50 Hz)", color='b')

# 標註 5 Hz 和 50 Hz 的波型
plt.plot(t, signal_5hz, label="5 Hz Signal", linestyle='--', color='r')
plt.plot(t, signal_50hz, label="50 Hz Signal", linestyle='--', color='g')

# 設定標題和標籤
plt.title("Combined Signal with 5 Hz and 50 Hz Components")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True)
plt.legend()

# 顯示圖形
plt.tight_layout()
plt.show()
