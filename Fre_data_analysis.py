import matplotlib.pyplot as plt
# 設定中文字型
import matplotlib
matplotlib.rcParams['font.family'] = 'Microsoft JhengHei'
matplotlib.rcParams['axes.unicode_minus'] = False

# 頻率資料（Hz）以時間（天）為橫軸
days = [1, 2, 100]
# 取最接近 1X（主頻） 的頻率做主軸追蹤
main_freqs = [60.18, 59.91, 60.09]
harmonic_2x = [120.09, 119.82, 119.73]
harmonic_3x = [None, 179.82, 179.82]
harmonic_4x = [239.82, None, 239.91]
high_freq = [None, None, 1619.8]

plt.figure(figsize=(10, 6))
plt.plot(days, main_freqs, marker='o', label="1X 主頻 約60Hz")
plt.plot(days, harmonic_2x, marker='s', label="2X 諧波 約120Hz")
plt.plot(days, harmonic_3x, marker='^', label="3X 諧波 約180Hz")
plt.plot(days, harmonic_4x, marker='v', label="4X 諧波 約240Hz")
plt.plot(days, high_freq, marker='x', linestyle='--', color='red', label="高頻異常")

plt.title("馬達振動頻率趨勢圖")
plt.xlabel("天數")
plt.ylabel("頻率 (Hz)")
plt.xticks(days)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
