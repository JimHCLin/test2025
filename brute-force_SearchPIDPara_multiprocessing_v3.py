import numpy as np
import control
import matplotlib.pyplot as plt
import time
from itertools import product
from multiprocessing import Pool, cpu_count
from tqdm import tqdm  # 新增 tqdm

plt.rcParams["font.family"] = "Microsoft JhengHei"  # 中文字型設定

# 時間軸
t = np.linspace(0, 15, 1500)

# 被控系統
num = [1]
den = [1, 10, 20]
plant = control.TransferFunction(num, den)

# 目標穩態時間
target_best_time = 0.8  # 例如想找 Ts ≈ 0.1 秒

# PID參數掃描範圍
Kp_range = np.arange(0, 10 + 1, 5)
Ki_range = np.arange(0, 10 + 1, 5)
Kd_range = np.arange(0, 10 + 1, 5)

def settling_time(t, y, target=1.0, threshold=0.02):
    lower = target * (1 - threshold)
    upper = target * (1 + threshold)
    outside_idx = np.where((y < lower) | (y > upper))[0]
    if len(outside_idx) == 0:
        return t[0]
    last = outside_idx[-1]
    return np.nan if last == len(t) - 1 else t[last + 1]

def evaluate_pid(params):
    Kp, Ki, Kd = params
    C = control.TransferFunction([Kd, Kp, Ki], [1, 0])
    sys_cl = control.feedback(C * plant, 1)
    t_resp, y_resp = control.step_response(sys_cl, t)
    ts = settling_time(t_resp, y_resp)
    if not np.isnan(ts) and abs(ts - target_best_time) < 0.01:
        return (Kp, Ki, Kd, ts)
    else:
        return None

if __name__ == "__main__":
    start_time = time.time()
    param_list = list(product(Kp_range, Ki_range, Kd_range))
    print(f"總組合數量：{len(param_list)}")

    matched_params = []
    with Pool(processes=cpu_count()) as pool:
    #with Pool(processes=8) as pool:
        # 用 imap_unordered 並搭配 tqdm 顯示進度條
        for result in tqdm(pool.imap_unordered(evaluate_pid, param_list), total=len(param_list)):
            if result is not None:
                matched_params.append(result)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"總花費時間: {elapsed_time:.2f} 秒")
    print(f"使用核心數: {cpu_count()}")

    if matched_params:
        print("找到匹配的 PID 參數組合：")
        for Kp, Ki, Kd, ts in matched_params:
            print(f"Kp={Kp}, Ki={Ki}, Kd={Kd}, 穩態時間={ts:.3f} 秒")
    else:
        print("❌ 沒找到符合目標穩態時間的參數，請擴大範圍或放寬誤差條件")
