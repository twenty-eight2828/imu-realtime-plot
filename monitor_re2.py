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
corr_az_data = deque([0.0]*max_len, maxlen=max_len)
log_rows = []

# データ格納用（追加）
accel_z_data = deque([0.0]*max_len, maxlen=max_len)

# グラフ初期化（左Y軸に2系列表示）
plt.ion()
fig, ax1 = plt.subplots()

# 補正前 Accel_Z（点線オレンジ）
line1, = ax1.plot(range(max_len), list(accel_z_data),
                  label="Accel_Z (g)", linestyle='--', color='orange')

# 補正後 Corr_AZ（実線グリーン）
line2, = ax1.plot(range(max_len), list(corr_az_data),
                  label="Corr_AZ (g)", color='green')

# 左Y軸の装飾
ax1.set_ylabel("Accel_Z [g]")
ax1.set_ylim(-2.5, 2.5)
ax1.set_xlabel("Sample Index")
ax1.grid(True)

# 右Y軸（温度）
ax2 = ax1.twinx()
line3, = ax2.plot(range(max_len), list(temp_data),
                  label="Temp_C (°C)", color='blue', linestyle='--')
ax2.set_ylabel("Temperature (°C)")
ax2.set_ylim(20, 100)

# 凡例
fig.legend(loc="upper right")
ax1.set_title("Real-time IMU Data with Temperature Drift Compensation")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line or line.startswith("Temp_C"):
            continue

        parts = line.split(',')
        if len(parts) == 8:
                temp = float(parts[0])
                az = float(parts[3])
                corr_az = float(parts[4])

                temp_data.append(temp)
                accel_z_data.append(az)
                corr_az_data.append(corr_az)

                # グラフ更新
                line1.set_ydata(accel_z_data)
                line2.set_ydata(corr_az_data)
                line3.set_ydata(temp_data)

                for line in [line1, line2, line3]:
                    line.set_xdata(range(max_len))

                ax1.relim(); ax1.autoscale_view()
                ax2.relim(); ax2.autoscale_view()
                plt.pause(0.05)

                # CSVログ行を保存
                log_rows.append(parts)

except KeyboardInterrupt:
    print("リアルタイム表示を終了しました。CSVに保存します...")
    df = pd.DataFrame(log_rows, columns=[
        "Temp_C", "Accel_X[g]", "Accel_Y[g]", "Accel_Z[g]",
        "Corr_AZ[g]", "Gyro_X[dps]", "Gyro_Y[dps]", "Gyro_Z[dps]"
    ])
    df.to_csv("imu_log_re2.csv", index=False)
    print("imu_log_re2.csv に保存しました。")
    ser.close()
