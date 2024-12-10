# -*- coding: utf-8 -*-
# -*- 风光资源图谱 -*-
import os

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
from cartopy.feature import ShapelyFeature
from shapely.geometry import Point

from XinJiangData import xin

# from mpl_toolkits.basemap import Basemap

plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 修复保存图像是负号'-'显示为方块的问题


def switch_case(value):
    switcher = {
        "mean_wind_speed_120": {
            "name": "平均风速",
            "clevs": [0.0, 2.0, 2.5, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10, 100],
            "cdict": [
                [225, 224, 225], [192, 254, 231], [189, 232, 255], [188, 211, 253], [160, 196, 255],
                [119, 176, 251], [2, 119, 254], [161, 254, 116], [118, 254, 5], [255, 255, 0], [252, 220, 0],
                [253, 170, 0], [255, 142, 1], [255, 128, 124], [254, 91, 128], [253, 0, 0], [228, 1, 1], [168, 0, 0]
            ],
            'unit': "m/s"
        },
        "mean_wind_direction_120": {
            "name": "风向",
            "clevs": [30.0, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360],
            "cdict": [
                [0, 60, 248], [1, 96, 218], [2, 185, 186], [0, 139, 97], [0, 187, 109],
                [120, 217, 0], [254, 247, 72], [255, 189, 85], [254, 143, 89],
                [251, 57, 47], [199, 0, 165], [153, 0, 192]
            ],
            'unit': "°"
        },
        "wind_weighted_avg_120": {
            "name": "平均风功率密度",
            # "clevs": [100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600,2000],
            "clevs": [5, 231, 458, 685, 912, 1139, 1365, 1592, 1819, 2046, 2273, 2500],
            "cdict": [
                [50, 171, 3], [85, 184, 1], [116, 196, 5], [148, 215, 8], [189, 231, 7],
                [225, 238, 28], [254, 235, 11], [251, 186, 2], [243, 142, 9], [247, 97, 8],
                [247, 48, 8], [245, 7, 6]
            ],
            'unit': "W/m2"
        },
        "weibull_k_120": {
            "name": "Weibull分布参数K值",
            "clevs": [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1],
            "cdict": [
                [197, 167, 214], [94, 21, 132], [34, 0, 169], [0, 3, 212], [0, 103, 88], [47, 187, 4],
                [183, 234, 0], [255, 228, 0], [255, 178, 0], [255, 86, 0], [255, 0, 0]
            ],
            'unit': ""
        },
        "weibull_c_120": {
            "name": "Weibull分布参数C值",
            "clevs": [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1],
            "cdict": [
                [197, 167, 214], [94, 21, 132], [34, 0, 169], [0, 3, 212], [0, 103, 88], [47, 187, 4],
                [183, 234, 0], [255, 228, 0], [255, 178, 0], [255, 86, 0], [255, 0, 0]
            ],
            'unit': ""
        },
        "air_density_120": {
            "name": "空气密度",
            "clevs": [1.80, 1.805, 1.81, 1.815, 1.82, 1.825, 1.83, 1.835, 1.84, 1.845, 1.85, 1.855, 1.86, 1.865, 1.87,
                      1.89],
            # "clevs": [0.9,0.95,1,1.05,1.1,1.15,1.2,1.25,1.3,1.35,1.4,1.45,1.5,1.55,1.6,1.65],
            "cdict": [
                [16, 40, 104], [19, 86, 129], [26, 121, 139], [30, 154, 135], [25, 170, 115], [14, 195, 66],
                [1, 218, 5], [79, 224, 3], [164, 240, 7], [250, 251, 5], [242, 214, 6], [238, 187, 13],
                [236, 160, 20], [221, 125, 34], [203, 100, 46], [190, 87, 58]
            ],
            'unit': "kg/m3"

        },
        "relative_humidity_120": {
            "name": "相对湿度",
            # "clevs": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "clevs": [10, 25, 41, 56, 72, 87, 103, 118, 134, 150],
            "cdict": [
                [151, 232, 173], [153, 210, 202], [155, 188, 232], [107, 157, 225], [59, 126, 219],
                [43, 92, 194], [28, 59, 169], [17, 44, 144], [7, 30, 120], [0, 15, 80],
            ],
            'unit': ""
        }, "mean_wind_speed_80": {
            "name": "平均风速",
            "clevs": [0.0, 2.0, 2.5, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10, 100],
            "cdict": [
                [225, 224, 225], [192, 254, 231], [189, 232, 255], [188, 211, 253], [160, 196, 255],
                [119, 176, 251], [2, 119, 254], [161, 254, 116], [118, 254, 5], [255, 255, 0], [252, 220, 0],
                [253, 170, 0], [255, 142, 1], [255, 128, 124], [254, 91, 128], [253, 0, 0], [228, 1, 1], [168, 0, 0]
            ],
            'unit': "m/s"
        },
        "mean_wind_direction_80": {
            "name": "风向",
            "clevs": [30.0, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360],
            "cdict": [
                [0, 60, 248], [1, 96, 218], [2, 185, 186], [0, 139, 97], [0, 187, 109],
                [120, 217, 0], [254, 247, 72], [255, 189, 85], [254, 143, 89],
                [251, 57, 47], [199, 0, 165], [153, 0, 192]
            ],
            'unit': "°"
        },
        "wind_weighted_avg_80": {
            "name": "平均风功率密度",
            "clevs": [5, 231, 458, 685, 912, 1139, 1365, 1592, 1819, 2046, 2273, 2500],
            "cdict": [
                [50, 171, 3], [85, 184, 1], [116, 196, 5], [148, 215, 8], [189, 231, 7],
                [225, 238, 28], [254, 235, 11], [251, 186, 2], [243, 142, 9], [247, 97, 8],
                [247, 48, 8], [245, 7, 6]
            ],
            'unit': "W/m2"
        },
        "weibull_k_80": {
            "name": "Weibull分布参数K值",
            "clevs": [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1],
            "cdict": [
                [197, 167, 214], [94, 21, 132], [34, 0, 169], [0, 3, 212], [0, 103, 88], [47, 187, 4],
                [183, 234, 0], [255, 228, 0], [255, 178, 0], [255, 86, 0], [255, 0, 0]
            ],
            'unit': ""
        },
        "weibull_c_80": {
            "name": "Weibull分布参数C值",
            "clevs": [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1],
            "cdict": [
                [197, 167, 214], [94, 21, 132], [34, 0, 169], [0, 3, 212], [0, 103, 88], [47, 187, 4],
                [183, 234, 0], [255, 228, 0], [255, 178, 0], [255, 86, 0], [255, 0, 0]
            ],
            'unit': ""
        },
        "air_density_80": {
            "name": "空气密度-80",
            "clevs": [1.80, 1.805, 1.81, 1.815, 1.82, 1.825, 1.83, 1.835, 1.84, 1.845, 1.85, 1.855, 1.86, 1.865, 1.87,
                      1.89],
            # "clevs": [0.9,0.95,1,1.05,1.1,1.15,1.2,1.25,1.3,1.35,1.4,1.45,1.5,1.55,1.6,1.65],
            "cdict": [
                [16, 40, 104], [19, 86, 129], [26, 121, 139], [30, 154, 135], [25, 170, 115], [14, 195, 66],
                [1, 218, 5], [79, 224, 3], [164, 240, 7], [250, 251, 5], [242, 214, 6], [238, 187, 13],
                [236, 160, 20], [221, 125, 34], [203, 100, 46], [190, 87, 58]
            ],
            'unit': ""
        },
        "relative_humidity_80": {
            "name": "相对湿度",
            "clevs": [10, 25, 41, 56, 72, 87, 103, 118, 134, 150],
            "cdict": [
                [151, 232, 173], [153, 210, 202], [155, 188, 232], [107, 157, 225], [59, 126, 219],
                [43, 92, 194], [28, 59, 169], [17, 44, 144], [7, 30, 120], [0, 15, 80],
            ],
            'unit': ""
        },
        "wind_rose": "风玫瑰",
        "prevailing_wind_direction": "主风向",
    }
    return switcher.get(value, 'wrong value')


# 要素
# 'lat' 'lon' 'weibull_k' 'weibull_c' 'mean_wind_speed'
# 'air_density' 'wind_weighted_avg' 'relative_humidity'
# 'mean_wind_direction' 'wind_rose' 'prevailing_wind_direction'
# 'horizontal_radiation' 'direct_radiation' 'scattered_radiation'

# data = nc.Dataset(r'D:\Code\result_post_interpolation.nc', 'r')
path = r'F:\xjData\XNYPoint\yearAvg\wind\yearly\xj_3km_80-120_2022.nc'

# data = nc.Dataset(r'D:\shadowData\xj\nc\result_post_interpolation.nc', 'r')
# shp_path = 'E:\区域shp\中华人民共和国 (1)中华人民共和国\中华人民共和国 (1).shp'

variableArray = [
    "mean_wind_speed_120", "mean_wind_direction_120", "wind_weighted_avg_120",
    "weibull_k_120", "weibull_c_120", "air_density_120", "relative_humidity_120",
    "mean_wind_speed_80", "mean_wind_direction_80", "wind_weighted_avg_80",
    "weibull_k_80", "weibull_c_80", "air_density_80", "relative_humidity_80",
]


def processWind(path, file_name):
    for variable_name in variableArray:
        data = nc.Dataset(path, 'r')
        # 去掉后缀 .nc
        file_name_no_ext = file_name.rstrip('.nc')
        # 如果还需要处理其他部分，比如获取日期
        date = file_name_no_ext.split('_')[3]
        variable_data = data.variables[variable_name][:]

        if (variable_name == 'mean_wind_direction_120' or variable_name == 'mean_wind_direction_80'):
            wind_direction = data.variables[variable_name][:]
            # 计算风向频率
            wind_frequencies = xin.calculate_wind_frequencies(wind_direction)

            # 绘制风玫瑰图
            xin.plot_wind_rose(date, variable_name, wind_frequencies)
        else:
            # 获取数据相关信息
            lat = data.variables['lat'][:]
            lon = data.variables['lon'][:]
            latmax = lat.max()
            latmin = lat.min()
            lonmax = lon.max()
            lonmin = lon.min()
            # 输出经纬度的范围
            print(f"Latitude range: {latmin} to {latmax}")
            print(f"Longitude range: {lonmin} to {lonmax}")

            parmObj = switch_case(variable_name)
            clevs = parmObj['clevs']
            cdict = np.asarray(parmObj['cdict']) / 255.0
            cmap = colors.ListedColormap(cdict)
            norm = mpl.colors.BoundaryNorm(clevs, cmap.N)
            # 颜色映射的规范化
            # cmap = plt.get_cmap('seismic')  # 选择 'viridis' 或其他内置渐变色表
            # norm = plt.Normalize(vmin=variable_data.min(), vmax=variable_data.max())
            # 添加省界
            # china = cfeature.ShapelyFeature(Reader(r'E:\区域shp\中华人民共和国 (1)\中华人民共和国 (1).shp').geometries(), ccrs.PlateCarree(),
            #                                 linewidth=0.5, facecolor='none', edgecolor='yellow', alpha=0.7)
            fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
            #
            # # ax.add_feature(china)
            # 绘制数据，使用平滑过渡的颜色映射
            ax.contourf(lon, lat, variable_data, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
            plt.axis('off')
            pngPath = 'D:\\shadowData\\xj\\ncPng\\wind\\' + date + '\\'
            if not os.path.exists(pngPath):  # 如果路径不存在
                os.makedirs(pngPath)  # 则创建该目录
            else:
                print("路径已经存在")
            plt.savefig(pngPath + variable_name + '.png', dpi=600, bbox_inches='tight', transparent=True, pad_inches=0)


def processWindByBounds(path, file_name, polygon, bounds, savePath, name):
    for variable_name in variableArray:
        data = nc.Dataset(path, 'r')
        # 去掉后缀 .nc
        file_name_no_ext = file_name.rstrip('.nc')
        # 如果还需要处理其他部分，比如获取日期
        date = file_name_no_ext.split('_')[3]
        variable_data = data.variables[variable_name][:]

        if (variable_name == 'mean_wind_direction_120' or variable_name == 'mean_wind_direction_80'):
            continue
        else:
            # 获取数据相关信息
            lat = data.variables['lat'][:]
            lon = data.variables['lon'][:]

            pngPath = savePath + date + '\\'
            if not os.path.exists(pngPath):  # 如果路径不存在
                os.makedirs(pngPath)  # 则创建该目录
            else:
                print('路径已存在')

            parmObj = switch_case(variable_name)
            clevs = parmObj['clevs']
            cdict = np.asarray(parmObj['cdict']) / 255.0
            cmap = colors.ListedColormap(cdict)
            norm = mpl.colors.BoundaryNorm(clevs, cmap.N)
            masked_data, latmax, latmin, lonmax, lonmin, lon_cropped, lat_cropped = makeYM(lat, lon, variable_data,
                                                                                           bounds, polygon)
            # 绘图
            fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
            ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

            # 绘制掩膜后的数据
            c = ax.contourf(lon_cropped, lat_cropped, masked_data, clevs, cmap=cmap, norm=norm,
                            transform=ccrs.PlateCarree())

            plt.axis('off')
            plt.savefig(pngPath + name + '-' + variable_name + '.png', dpi=600, bbox_inches='tight', transparent=True,
                        pad_inches=0)


def processWindByPolygon(path, file_name, polygon, bounds, savePath, name):
    for variable_name in variableArray:
        data = nc.Dataset(path, 'r')
        # 去掉后缀 .nc
        file_name_no_ext = file_name.rstrip('.nc')
        # 如果还需要处理其他部分，比如获取日期
        date = file_name_no_ext.split('_')[3]
        variable_data = data.variables[variable_name][:]
        if (variable_name == 'mean_wind_direction_120' or variable_name == 'mean_wind_direction_80'):
            wind_direction = data.variables[variable_name][:]
            masked_data, latmax, latmin, lonmax, lonmin, lon_cropped, lat_cropped = makeYM(lat, lon, wind_direction,
                                                                                           bounds, polygon)
            # 计算风向频率
            wind_frequencies = xin.calculate_wind_frequencies(masked_data)

            # 绘制风玫瑰图
            xin.plot_wind_rose(savePath, date, name, variable_name, wind_frequencies)
        else:
            # 获取数据相关信息
            lat = data.variables['lat'][:]
            lon = data.variables['lon'][:]
            latmax = bounds[3]
            latmin = bounds[1]
            lonmax = bounds[2]
            lonmin = bounds[0]
            # 设置扩大范围的比例
            margin_ratio = 0.2  # 比如扩大 10%
            pngPath = savePath + date + '\\'
            if not os.path.exists(pngPath):  # 如果路径不存在
                os.makedirs(pngPath)  # 则创建该目录
            else:
                print('路径已存在')

            parmObj = switch_case(variable_name)
            clevs = parmObj['clevs']
            unit = parmObj['unit']
            cdict = np.asarray(parmObj['cdict']) / 255.0
            cmap = colors.ListedColormap(cdict)
            norm = mpl.colors.BoundaryNorm(clevs, cmap.N)
            # 绘图
            fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
            # 计算扩展范围
            lon_margin = (lonmax - lonmin) * margin_ratio
            lat_margin = (latmax - latmin) * margin_ratio

            # 设置新的范围
            ax.set_extent([lonmin - lon_margin, lonmax + lon_margin, latmin - lat_margin, latmax + lat_margin],
                          crs=ccrs.PlateCarree())

            # 绘制掩膜后的数据
            c = ax.contourf(lon, lat, variable_data, clevs, cmap=cmap, norm=norm,
                            transform=ccrs.PlateCarree())

            # 将边界信息以线的形式画到图片上
            # 使用 cartopy 绘制 MultiPolygon
            if polygon:
                # 转换 shapely 的 MultiPolygon 到 cartopy 的 feature
                feature = ShapelyFeature(polygon, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=1)
                ax.add_feature(feature)

            # 添加图例
            cb = plt.colorbar(c, ax=ax, orientation='vertical', pad=0.02, shrink=0.75)  # 调整 pad 和 shrink 以适配图例位置
            if (unit != ""):
                cb.set_label(variable_name + "单位: " + unit)  # 图例标题，例如温度、降水量等
            else:
                cb.set_label(variable_name)  # 图例标题，例如温度、降水量等
            cb.ax.tick_params(labelsize=8)  # 可调节刻度字体大小
            plt.axis('off')
            plt.savefig(pngPath + name + '-' + variable_name + '.png', dpi=600, bbox_inches='tight', facecolor='white',
                        pad_inches=0)
            plt.close()


def makeYM(lat, lon, variable_data, bounds, polygon):
    latmax = bounds[3]
    latmin = bounds[1]
    lonmax = bounds[2]
    lonmin = bounds[0]
    lat_idx = (lat >= latmin) & (lat <= latmax)
    lon_idx = (lon >= lonmin) & (lon <= lonmax)

    variable_data_cropped = variable_data[np.ix_(lat_idx, lon_idx)]
    lon_cropped = lon[lon_idx]
    lat_cropped = lat[lat_idx]

    # 创建掩膜
    mask = np.zeros_like(variable_data_cropped, dtype=bool)

    # 遍历所有裁剪后的点
    for i, lat_val in enumerate(lat_cropped):
        for j, lon_val in enumerate(lon_cropped):
            point = Point(lon_val, lat_val)
            if not polygon.contains(point):  # 判断点是否在多边形内
                mask[i, j] = True

    # 应用掩膜
    masked_data = np.ma.masked_array(variable_data_cropped, mask)
    return masked_data, latmax, latmin, lonmax, lonmin, lon_cropped, lat_cropped


if __name__ == '__main__':
    path = 'F:\\xjData\\XNYPoint\\yearAvg\\wind\\yearly\\'
    file_list = os.listdir(path)
    # 遍历每个文件
    for file_name in file_list:
        ffile_type = os.path.splitext(file_name)[1].lstrip('.')
        type = file_name.split('.')[1]
        if ffile_type == 'nc':
            # 拼接文件的完整路径
            file_path = os.path.join(path, file_name)
            processWind(file_path, file_name)
        else:
            continue
