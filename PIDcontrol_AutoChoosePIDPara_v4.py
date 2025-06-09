import numpy as np
import matplotlib.pyplot as plt
import control

# 設定中文字型（Windows）
plt.rcParams["font.family"] = "Microsoft JhengHei"

def settling_time(t, y, target=1.0, threshold=0.02):
    """計算穩態時間 (±threshold 範圍內視為穩定)"""
    lower_bound = target * (1 - threshold)
    upper_bound = target * (1 + threshold)
    outside_indices = np.where((y < lower_bound) | (y > upper_bound))[0]

    if len(outside_indices) == 0:
        return t[0]
    last_outside = outside_indices[-1]
    if last_outside == len(t) - 1:
        return np.nan
    else:
        return t[last_outside + 1]

# 被控二階系統
num = [1]
den = [1, 10, 20]
plant = control.TransferFunction(num, den)

# 時間軸
t = np.linspace(0, 15, 1500)

# 參數範圍（你可自由調整）
Kp_list = [100]
Ki_list = [180]
Kd_list = [10]

# 各控制器的 TransferFunction 定義
controllers = {
    'P 控制':  lambda Kp, Ki, Kd: control.TransferFunction([Kp], [1]),
    'I 控制':  lambda Kp, Ki, Kd: control.TransferFunction([Ki], [1, 0]),
    'D 控制':  lambda Kp, Ki, Kd: control.TransferFunction([Kd, 0], [1]),
    'PI 控制': lambda Kp, Ki, Kd: control.TransferFunction([Kp, Ki], [1, 0]),
    'PD 控制': lambda Kp, Ki, Kd: control.TransferFunction([Kd, Kp], [1]),
    'ID 控制': lambda Kp, Ki, Kd: control.TransferFunction([Kd, 0, Ki], [1, 0]),
    'PID 控制':lambda Kp, Ki, Kd: control.TransferFunction([Kd, Kp, Ki], [1, 0])
}

# 繪圖初始化
plt.figure(figsize=(12, 8))
best_results = {}

for label, create_controller in controllers.items():
    best_time = np.inf
    best_params = (0, 0, 0)
    best_response = None
    best_t = None

    for Kp in Kp_list:
        for Ki in Ki_list:
            for Kd in Kd_list:
                C = create_controller(Kp, Ki, Kd)
                sys_cl = control.feedback(C * plant, 1)
                t_resp, y_resp = control.step_response(sys_cl, t)
                ts = settling_time(t_resp, y_resp)

                if not np.isnan(ts) and ts < best_time:
                    best_time = ts
                    best_params = (Kp, Ki, Kd)
                    best_response = y_resp
                    best_t = t_resp

    best_results[label] = (best_time, best_params)

    # 根據控制器類型只顯示必要參數
    if "I" in label and "P" not in label and "D" not in label:
        param_str = f"Ki={best_params[1]}"
    elif "P" in label and "I" not in label and "D" not in label:
        param_str = f"Kp={best_params[0]}"
    elif "D" in label and "P" not in label and "I" not in label:
        param_str = f"Kd={best_params[2]}"
    elif label == "PI 控制":
        param_str = f"Kp={best_params[0]}, Ki={best_params[1]}"
    elif label == "PD 控制":
        param_str = f"Kp={best_params[0]}, Kd={best_params[2]}"
    elif label == "ID 控制":
        param_str = f"Ki={best_params[1]}, Kd={best_params[2]}"
    elif label == "PID 控制":
        param_str = f"Kp={best_params[0]}, Ki={best_params[1]}, Kd={best_params[2]}"
    else:
        param_str = ""

    if best_t is not None and best_response is not None:
        plt.plot(best_t, best_response,
                 label=f'{label} (Ts={best_time:.3f}s, {param_str})')
    else:
        print(f"{label} 無法穩定，略過。")

# 畫圖設定
plt.axhline(1, color='gray', linestyle='--', label='目標值 = 1')
plt.title('七種控制器響應比較（各自最佳參數）')
plt.xlabel('時間 (秒)')
plt.ylabel('系統輸出')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# 印出結果
print("\n最佳參數與穩態時間：")
for label, (ts, (Kp, Ki, Kd)) in best_results.items():
    print(f"{label:<6s}：Ts = {ts:.3f}s，Kp={Kp}, Ki={Ki}, Kd={Kd}")
