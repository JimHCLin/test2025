import numpy as np
import control
import matplotlib.pyplot as plt
import time
from itertools import product
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

plt.rcParams["font.family"] = "Microsoft JhengHei"

t = np.linspace(0, 15, 1500)
num = [1]
den = [1, 10, 20]
plant = control.TransferFunction(num, den)

target_best_time = 0.5

Kp_range = np.arange(0, 300 + 1, 10)
Ki_range = np.arange(0, 300 + 1, 10)
Kd_range = np.arange(0, 300 + 1, 10)

def settling_time(t, y, target=1.0, threshold=0.02):
    lower = target * (1 - threshold)
    upper = target * (1 + threshold)
    outside_idx = np.where((y < lower) | (y > upper))[0]
    if len(outside_idx) == 0:
        return t[0]
    last = outside_idx[-1]
    return np.nan if last == len(t) - 1 else t[last + 1]

# 單一子進程處理一批參數的函式
def evaluate_pid_batch(param_batch):
    results = []
    for params in param_batch:
        Kp, Ki, Kd = params
        C = control.TransferFunction([Kd, Kp, Ki], [1, 0])
        sys_cl = control.feedback(C * plant, 1)
        t_resp, y_resp = control.step_response(sys_cl, t)
        ts = settling_time(t_resp, y_resp)
        if not np.isnan(ts) and abs(ts - target_best_time) < 0.01:
            results.append((Kp, Ki, Kd, ts))
    return results

if __name__ == "__main__":
    start_time = time.time()

    param_list = list(product(Kp_range, Ki_range, Kd_range))
    batch_size = 100 # 一批丟20組
    # 分割參數清單成多批
    param_batches = [param_list[i:i+batch_size] for i in range(0, len(param_list), batch_size)]

    matched_params = []
    with Pool(processes=cpu_count()) as pool:
        # tqdm包裝map顯示進度
        for batch_result in tqdm(pool.imap_unordered(evaluate_pid_batch, param_batches), total=len(param_batches)):
            matched_params.extend(batch_result)

    end_time = time.time()
    print(f"總花費時間: {end_time - start_time:.2f} 秒")
    print(f"使用核心數: {cpu_count()}")

    if matched_params:
        print("找到匹配的 PID 參數組合：")
        for Kp, Ki, Kd, ts in matched_params:
            print(f"Kp={Kp}, Ki={Ki}, Kd={Kd}, 穩態時間={ts:.3f} 秒")
    else:
        print("❌ 沒找到符合目標穩態時間的參數，請擴大範圍或放寬誤差條件")
