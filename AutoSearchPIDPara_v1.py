import numpy as np
import control
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Microsoft JhengHei"  # 顯示中文字

# 時間軸
t = np.linspace(0, 15, 1500)

# 被控系統
num = [1]
den = [1, 10, 20]
plant = control.TransferFunction(num, den)

# 想要找到的目標穩態時間
target_best_time = 0.85  # 例如你想找 Ts ≈ 0.85 秒

# 不限制參數，用範圍 + 步長方式掃描
Kp_range = np.arange(0, 200 + 1, 10)   # 從 0 到 200，步長 10
Ki_range = np.arange(0, 200 + 1, 10)
Kd_range = np.arange(0, 100 + 1, 10)

# 計算穩態時間的函數
def settling_time(t, y, target=1.0, threshold=0.02):
    lower = target * (1 - threshold)
    upper = target * (1 + threshold)
    outside_idx = np.where((y < lower) | (y > upper))[0]
    if len(outside_idx) == 0:
        return t[0]
    last = outside_idx[-1]
    return np.nan if last == len(t) - 1 else t[last + 1]

# 搜尋符合條件的參數
matched_params = []

for Kp in Kp_range:
    for Ki in Ki_range:
        for Kd in Kd_range:
            C = control.TransferFunction([Kd, Kp, Ki], [1, 0])
            sys_cl = control.feedback(C * plant, 1)
            t_resp, y_resp = control.step_response(sys_cl, t)
            ts = settling_time(t_resp, y_resp)

            # 比對誤差是否在 ±0.01 秒內
            if not np.isnan(ts) and abs(ts - target_best_time) < 0.01:
                matched_params.append((Kp, Ki, Kd, ts))

# 結果輸出
if matched_params:
    print("找到匹配的 PID 參數組合：")
    for Kp, Ki, Kd, ts in matched_params:
        print(f"Kp={Kp}, Ki={Ki}, Kd={Kd}, 穩態時間={ts:.3f} 秒")
else:
    print("❌ 沒找到符合目標穩態時間的參數，請擴大範圍或放寬誤差條件")
