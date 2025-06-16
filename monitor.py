import serial
import matplotlib.pyplot as plt
import pandas as pd
import time
from collections import deque

# シリアル接続と初期化
ser = serial.Serial('/dev/tty.usbmodem11301', 9600, timeout=1)
time.sleep(2)

# データ格納と可視化準備
max_len = 50
temp_data = deque([0.0]*max_len, maxlen=max_len)
accel_z_data = deque([0.0]*max_len, maxlen=max_len)
log_rows = []

# グラフ初期化（ツインY軸）
plt.ion()
fig, ax1 = plt.subplots()

# 左Y軸（Accel_Z）
line1, = ax1.plot(range(max_len), list(accel_z_data), label="Accel_Z (g)", color='orange')
ax1.set_ylabel("Accel_Z (g)")
ax1.set_ylim(-2.5, 2.5)
ax1.set_xlabel("Sample Index")
ax1.grid(True)

# 右Y軸（Temp_C）
ax2 = ax1.twinx()
line2, = ax2.plot(range(max_len), list(temp_data), label="Temp_C (°C)", color='blue', linestyle='--')
ax2.set_ylabel("Temperature (°C)")
ax2.set_ylim(20, 40)  # 例：TMP102は常温で25〜35℃の範囲を想定

# 凡例
fig.legend(loc="upper right")
ax1.set_title("Real-time IMU Data")

# メインループ
try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line or line.startswith("Temp_C"):
            continue

        parts = line.split(',')
        if len(parts) == 7:
            temp = float(parts[0])
            accel_z = float(parts[3])

            temp_data.append(temp)
            accel_z_data.append(accel_z)

            line1.set_ydata(accel_z_data)
            line1.set_xdata(range(len(accel_z_data)))
            line2.set_ydata(temp_data)
            line2.set_xdata(range(len(temp_data)))

            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()

            plt.pause(0.05)

            # ログに保存
            log_rows.append(parts)

except KeyboardInterrupt:
    print("リアルタイム表示を終了しました。CSVに保存します...")
    df = pd.DataFrame(log_rows, columns=[
        "Temp_C", "Accel_X[g]", "Accel_Y[g]", "Accel_Z[g]",
        "Gyro_X[dps]", "Gyro_Y[dps]", "Gyro_Z[dps]"
    ])
    df.to_csv("imu_log.csv", index=False)
    print("imu_log.csv に保存しました。")
    ser.close()
