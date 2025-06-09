import numpy as np
import matplotlib.pyplot as plt
import control  # pip install control

# 一階受控系統 G(s) = 1 / (s + 1)
plant = control.tf([1], [1, 1])

# 控制器參數
Kp = 2.0
Ki = 1.0
Kd = 0.5

# 各種控制器 transfer function
P = control.tf([Kp], [1])
I = control.tf([Ki], [1, 0])
D = control.tf([Kd, 0], [1])  # 微分器加一階低通可更真實，這裡簡單處理

PD = control.tf([Kd, Kp], [1])
PI = control.tf([Kp, Ki], [1, 0])
PID = control.tf([Kd, Kp, Ki], [1, 0])

# 閉迴路系統
sys_P = control.feedback(P * plant, 1)
sys_I = control.feedback(I * plant, 1)
sys_D = control.feedback(D * plant, 1)
sys_PD = control.feedback(PD * plant, 1)
sys_PI = control.feedback(PI * plant, 1)
sys_PID = control.feedback(PID * plant, 1)

# 時間軸
t = np.linspace(0, 20, 1000)

# 模擬各系統的階躍響應
t, y_P = control.step_response(sys_P, t)
t, y_I = control.step_response(sys_I, t)
t, y_D = control.step_response(sys_D, t)
t, y_PD = control.step_response(sys_PD, t)
t, y_PI = control.step_response(sys_PI, t)
t, y_PID = control.step_response(sys_PID, t)

# 繪圖
plt.figure(figsize=(12, 8))
plt.plot(t, y_P, label='P only')
plt.plot(t, y_I, label='I only')
plt.plot(t, y_D, label='D only')
plt.plot(t, y_PD, label='PD')
plt.plot(t, y_PI, label='PI')
plt.plot(t, y_PID, label='PID')

plt.axhline(1, color='gray', linestyle='--', label='Setpoint = 1')
plt.title('Step Response Comparison for Various Controllers')
plt.xlabel('Time (s)')
plt.ylabel('Output')
plt.grid(True)
plt.legend()
plt.show()
