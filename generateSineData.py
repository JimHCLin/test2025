import numpy as np
import pandas as pd

# 設定參數
sampling_rate = 2000  # 采樣率
duration = 1  # 信號時長
frequencies = [50, 800]  # 50Hz, 120Hz, 300Hz 正弦波

# 時間軸
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# 生成時域信號（三個頻率的合成信號）
signal = np.sum([np.sin(2 * np.pi * f * t) for f in frequencies], axis=0)

# 創建 DataFrame
df = pd.DataFrame({'時間': t, '數值': signal})

# 生成檔名，將頻率列表轉換為字串
frequency_str = "_".join([str(f) for f in frequencies])
file_name = f'sine_wave_data_{frequency_str}Hz.csv'

# 儲存為 CSV
df.to_csv(file_name, index=False)

print(f"CSV 檔案已經生成，檔名：{file_name}")
