import numpy as np
import matplotlib.pyplot as plt
import control
# 設定中文字型（Windows 範例）
plt.rcParams["font.family"] = "Microsoft JhengHei"  # 微軟正黑體

def settling_time(t, y, threshold=0.02):
    """
    計算穩態時間（settling time）
    threshold: 允許誤差範圍，預設 2%
    """
    steady_state_value = y[-1]
    lower_bound = steady_state_value * (1 - threshold)
    upper_bound = steady_state_value * (1 + threshold)

    # 找出最後一次出界的時間索引
    outside_indices = np.where((y < lower_bound) | (y > upper_bound))[0]

    if len(outside_indices) == 0:
        return t[0]  # 一開始就穩定
    else:
        last_outside = outside_indices[-1]
        if last_outside == len(t) - 1:
            return np.nan  # 未穩定
        else:
            return t[last_outside + 1]

# 被控系統 (plant): 一階系統例子
num = [1]
den = [1, 10, 20]  # 二階系統示例
plant = control.TransferFunction(num, den)

# 時間範圍
t = np.linspace(0, 5, 500)

# PI 控制器參數
Kp_pi = 30
Ki_pi = 70
C_pi = control.TransferFunction([Kp_pi, Ki_pi], [1, 0])  # Kp + Ki/s

# PID 控制器參數
Kp_pid = 350
Ki_pid = 300
Kd_pid = 50
C_pid = control.TransferFunction([Kd_pid, Kp_pid, Ki_pid], [1, 0])  # Kd*s + Kp + Ki/s

# 閉環系統
sys_pi = control.feedback(C_pi*plant, 1)
sys_pid = control.feedback(C_pid*plant, 1)

# 系統響應
t_pi, y_pi = control.step_response(sys_pi, t)
t_pid, y_pid = control.step_response(sys_pid, t)

# 計算穩態時間
ts_pi = settling_time(t_pi, y_pi)
ts_pid = settling_time(t_pid, y_pid)

print(f"PI 控制穩態時間 (2%範圍): {ts_pi:.3f} 秒")
print(f"PID 控制穩態時間 (2%範圍): {ts_pid:.3f} 秒")

# 畫圖
plt.figure(figsize=(10,6))
plt.plot(t_pi, y_pi, label='PI 控制')
plt.plot(t_pid, y_pid, label='PID 控制')
plt.axhline(1, color='k', linestyle='--', label='目標值=1')
plt.xlabel('時間 (秒)')
plt.ylabel('系統輸出')
plt.title('PI 與 PID 控制系統響應')
plt.legend()
plt.grid(True)
plt.show()
