import os

import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np


# 1. 读取 NetCDF 文件中的风向和经纬度数据
def read_nc_file(file_path):
    dataset = nc.Dataset(file_path)

    # 假设风向存储在 'wind_direction' 变量中，经度和纬度分别存储在 'lon' 和 'lat' 中
    wind_direction = dataset.variables['mean_wind_direction_80'][:]  # 风向数据 (风向, 经度, 纬度)
    lat = dataset.variables['lat'][:]  # 纬度
    lon = dataset.variables['lon'][:]  # 经度

    return wind_direction, lat, lon


# 2. 计算风向频率
def calculate_wind_frequencies(wind_direction, n_directions=16):
    # 定义 16 个风向区间
    direction_bins = np.linspace(0, 360, n_directions + 1)

    # 初始化频率计数
    direction_counts = np.zeros(n_directions)

    # 将风向数据从 (风向, 经度, 纬度) 展平成一维数组
    wind_direction_flat = wind_direction.flatten()

    # 计算每个风向区间的出现次数
    for i in range(n_directions):
        direction_counts[i] = np.sum((wind_direction_flat >= direction_bins[i]) &
                                     (wind_direction_flat < direction_bins[i + 1]))

    # 将次数转换为频率（百分比）
    total_count = np.sum(direction_counts)
    direction_frequencies = (direction_counts / total_count) * 100

    return direction_frequencies


# 3. 绘制风玫瑰图
def plot_wind_rose(savePath, date, name, variable_name, frequencies, n_directions=16):
    # 定义 16 个风向的标签
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

    # 计算极坐标角度
    theta = np.linspace(0.0, 2 * np.pi, n_directions, endpoint=False)

    # 为了让图闭合，需要再重复第一个方向的频率
    frequencies = np.append(frequencies, frequencies[0])
    theta = np.append(theta, theta[0])

    # 创建极坐标图
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

    # 设置北为图的正上方，角度顺时针
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)

    # 绘制风玫瑰图
    ax.plot(theta, frequencies, 'r-', linewidth=2)

    # 填充颜色
    ax.fill(theta, frequencies, alpha=0.3)

    # 设置风向标签
    ax.set_xticks(np.linspace(0, 2 * np.pi, n_directions, endpoint=False))
    ax.set_xticklabels(directions)
    # plt.axis('off')
    pngPath = savePath + date + '\\'
    if not os.path.exists(pngPath):  # 如果路径不存在
        os.makedirs(pngPath)  # 则创建该目录
    else:
        print("路径已经存在")
    plt.savefig(pngPath + name + '-' + variable_name + '.png', dpi=600, bbox_inches='tight',facecolor='white',
                pad_inches=0)
    plt.close()

# 4. 主函数
def main():
    # 替换为你的 NetCDF 文件路径
    # file_path = r'D:\shadowData\xj\nc\result_post_interpolation.nc'
    file_path = r'D:\shadowData\xj\nc\xj_3km_80-120_2022100101.nc'
    file_path = r'D:\shadowData\xj\nc\xj_3km_80-120_201301.nc'

    # 读取 NetCDF 文件中的风向数据
    wind_direction, lat, lon = read_nc_file(file_path)

    # 计算风向频率
    wind_frequencies = calculate_wind_frequencies(wind_direction)

    # 绘制风玫瑰图
    plot_wind_rose(wind_frequencies)


# 运行主函数
if __name__ == '__main__':
    main()
