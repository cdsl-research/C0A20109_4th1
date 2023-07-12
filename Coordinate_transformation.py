from csv import reader
import math
from matplotlib import pyplot
import numpy as np

#csv読み込み
def csv_file(file):
    with open(file, 'r') as csv_file:
        csv_reader = reader(csv_file)
        data_header = next(csv_reader) #一行目を出力
        data = list(csv_reader)
    return data

# データ前処理
def data_preprocessing(data):
    data_accl_time, data_accl_x, data_accl_y, data_accl_z, data_accl = [], [], [], [], []
    data_mag_time, data_mag_x, data_mag_y, data_mag_z, data_mag = [], [], [], [], []
    for i in data:
        data_accl_time.append(float(i[0]))
        data_accl.append(np.sqrt(float(i[1])**2 + float(i[2])**2 + float(i[3])**2))
        data_mag_time.append(float(i[4]))
        data_mag.append(np.sqrt(float(i[5])**2 + float(i[6])**2 + float(i[7])**2))
    return data_accl_time, data_accl_x, data_accl_y, data_accl_z, data_accl, data_mag_time, data_mag_x, data_mag_y, data_mag_z, data_mag

# 歩数カウント
def count_steps(accel, threshold):
    steps = 0
    prev_acc = accel[0]
    stepList = []
    for acc in accel[1:]:
        if abs(acc - prev_acc) > threshold:
            steps += 1
            stepList.append(1)
        else:
            stepList.append(0)
        prev_acc = acc
    return steps, stepList

# 地磁気から方位角を算出
def azimuth(mag_x, mag_y):
    azimuths, azimuth_degrees = [], []
    for x, y in zip(mag_x, mag_y):
        az = math.atan2(y, x) # 方位角の計算
        azimuths.append(az)
        azimuth_degrees.append(math.degrees(az)) # ラジアンから度に変換
    return azimuths, azimuth_degrees

# 座標変換
def coordinate(stride_length, azimuth, steps):
    x = 0.0  # x初期値
    y = 0.0  # y初期値
    coordinates = [(x, y)]
    for i in range(len(steps)):
        if steps[i] == 1:
            x = x + stride_length * math.cos(azimuth[i])
            y = y + stride_length * math.sin(azimuth[i])
            coordinates.append((x, y))
        else:
        　　x = x + math.cos(azimuth[i])
        　  y = y + math.sin(azimuth[i])
        　　coordinates.append((x, y))
    return coordinates

file = './data.csv'
data = csv_file(file)
print(data)
data_accl_time, data_accl_x, data_accl_y, data_accl_z, data_accl, data_mag_time, data_mag_x, data_mag_y, data_mag_z, data_mag = data_preprocessing(data)
azimuths, azimuth_degrees = azimuth(data_mag_x, data_mag_y)
steps, stepList = count_steps(data_accl, 0.5)
print(stepList)
print(steps*68)
coordinates = coordinate(68.0, azimuths, stepList)

# 座標をグラフで表す
x_coordinates, y_coordinates = zip(*coordinates)
pyplot.figure(figsize=(6,6))
pyplot.plot(y_coordinates, x_coordinates, marker='o')
pyplot.grid(True)
pyplot.xlabel('X')
pyplot.ylabel('Y')
pyplot.show()



