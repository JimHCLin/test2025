import numpy as np
import matplotlib.pyplot as plt
import control
plt.rcParams["font.family"] = "Microsoft JhengHei"  # 微軟正黑體

def settling_time(t, y, target=1.0, threshold=0.02):
    lower_bound = target * (1 - threshold)
    upper_bound = target * (1 + threshold)

    outside_indices = np.where((y < lower_bound) | (y > upper_bound))[0]
    if len(outside_indices) == 0:
        return t[0]
    else:
        last_outside = outside_indices[-1]
        if last_outside == len(t) - 1:
            return np.nan
        else:
            return t[last_outside + 1]

# 被控系統：二階系統
num = [1]
den = [1, 10, 20]
plant = control.TransferFunction(num, den)
t = np.linspace(0, 15, 1500)

# 控制器參數
Kp = 10
Ki = 10
Kd = 10

# 各控制器定義
controllers = {
    'P 控制': control.TransferFunction([Kp], [1]),
    'I 控制': control.TransferFunction([Ki], [1, 0]),
    'D 控制': control.TransferFunction([Kd, 0], [1]),
    'PI 控制': control.TransferFunction([Kp, Ki], [1, 0]),
    'PD 控制': control.TransferFunction([Kd, Kp], [1]),
    'ID 控制': control.TransferFunction([Kd, 0, Ki], [1, 0]),
    'PID 控制': control.TransferFunction([Kd, Kp, Ki], [1, 0])
}

# 顏色與線型（可自由調整）
styles = ['b-', 'g--', 'r-.', 'c-', 'm--', 'y-.', 'k-']
results = {}

# 模擬每個控制器
plt.figure(figsize=(12, 7))
for (label, C), style in zip(controllers.items(), styles):
    sys_cl = control.feedback(C * plant, 1)
    t_resp, y_resp = control.step_response(sys_cl, t)
    ts = settling_time(t_resp, y_resp, target=1.0)
    results[label] = ts
    plt.plot(t_resp, y_resp, style, label=f'{label}（Ts={ts:.3f}s）')

# 印出穩態時間結果
print("各控制器穩態時間 (±2% 範圍):")
for k, v in results.items():
    print(f"{k:6s}： {v:.3f} 秒")
# 畫圖設定
plt.axhline(1, color='gray', linestyle='--', label='目標值=1')
plt.title('各種控制器系統響應比較')
plt.xlabel('時間 (秒)')
plt.ylabel('系統輸出')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


