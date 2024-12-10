# -*- encoding: utf-8 -*-
# -*- 土地利用 -*-

import gc
import json
import os

import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.colors import Normalize
from rasterio.mask import mask

from XinJiangData import colorMap


def cm2inch(value):
    return value / 2.54


def px_to_size(px, mydpi):
    return px / mydpi


class CustomNormalize(Normalize):
    def __call__(self, value, clip=None):
        # 将小于 -200 的值映射为 0（透明）
        # 其他值按比例映射到 1 到 256 之间
        normalized = np.ma.masked_where(value < -200, value)
        return super().__call__(normalized, clip)


def drawWind(tif_path, file_name, pngPath):
    try:
        with open('Data/quhua/xj.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        # 遍历 FeatureCollection 的 features
        for feature in geojson_data.get("features", []):
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            adcode = properties.get("adcode")
            name = properties.get("name")
            level = properties.get("level")
            print(f"行政区划: {name}, 编码: {adcode}, 等级: {level}")
            print(f"边界信息: {geometry}")
            with rasterio.open(tif_path) as src:
                # 使用 GeoJSON 边界掩膜裁剪
                out_image, out_transform = mask(src, [geometry], crop=True)

            data = out_image[0]
            # 获取最大值和最小值
            # 使用 np.nanmax 和 np.nanmin 来忽略 NaN 值
            data_max = np.nanmax(data)  # 忽略 NaN 值计算最大值
            data_min = np.nanmin(data)  # 忽略 NaN 值计算最小值
            # 替换 NaN 为一个特定的值，例如 0 或者数据中的最小值
           # data = np.nan_to_num(data, nan=0)
            # x = data['x']
            # 创建一个图形和坐标轴对象
            fig, ax = plt.subplots(figsize=(12, 12))

            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.rcParams['axes.unicode_minus'] = False
            rainbow_cmap = plt.cm.rainbow
            if ('CHN_air-density_100m' in file_name):
                parmObj = colorMap.switch_case('air_density_120')
                clevs = parmObj['clevs']
                cdict = np.asarray(parmObj['cdict']) / 255.0
                my_cmap = colors.ListedColormap(cdict)
                num_intervals = len(cdict) - 1
                # 动态生成均匀的分隔点
                bounds = np.linspace(data_min, data_max, num_intervals + 1)
                # 使用生成的分隔点来创建 BoundaryNorm
                norm = mpl.colors.BoundaryNorm(bounds, my_cmap.N)
                # norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
                #norm = CustomNormalize(vmin=data_min, vmax=data_max)
            elif ('CHN_combined-Weibull-A_100m' in file_name):
                parmObj = colorMap.switch_case('weibull_c_120')
                clevs = parmObj['clevs']
                cdict = np.asarray(parmObj['cdict']) / 255.0
                my_cmap = colors.ListedColormap(cdict)
                num_intervals = len(cdict) - 1
                # 动态生成均匀的分隔点
                bounds = np.linspace(data_min, data_max, num_intervals + 1)
                # 使用生成的分隔点来创建 BoundaryNorm
                norm = mpl.colors.BoundaryNorm(bounds, my_cmap.N)
                # 设置 num_intervals 为 cdict 数组的长度减去 1
            elif ('CHN_combined-Weibull-k_100m' in file_name):
                parmObj = colorMap.switch_case('weibull_k_120')
                clevs = parmObj['clevs']
                cdict = np.asarray(parmObj['cdict']) / 255.0
                my_cmap = colors.ListedColormap(cdict)
                num_intervals = len(cdict) - 1
                # 动态生成均匀的分隔点
                bounds = np.linspace(data_min, data_max, num_intervals + 1)
                # 使用生成的分隔点来创建 BoundaryNorm
                norm = mpl.colors.BoundaryNorm(bounds, my_cmap.N)
                # 设置 num_intervals 为 cdict 数组的长度减去 1
                # norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
            # norm = CustomNormalize(vmin=data_min, vmax=data_max)
            elif ('CHN_power-density_100m' in file_name):
                parmObj = colorMap.switch_case('wind_weighted_avg_120')
                clevs = parmObj['clevs']
                cdict = np.asarray(parmObj['cdict']) / 255.0
                my_cmap = colors.ListedColormap(cdict)
                norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
                # 设置 num_intervals 为 cdict 数组的长度减去 1
                # norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
            # norm = CustomNormalize(vmin=data_min, vmax=data_max)
            elif ('CHN_wind-speed_100m' in file_name):
                parmObj = colorMap.switch_case('mean_wind_speed_120')
                clevs = parmObj['clevs']
                cdict = np.asarray(parmObj['cdict']) / 255.0
                my_cmap = colors.ListedColormap(cdict)
                # 设置 num_intervals 为 cdict 数组的长度减去 1
                norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)

            # norm = CustomNormalize(vmin=data_min, vmax=data_max)

            # 绘制地图并裁剪到指定区域
            # 绘制地图
            c = ax.imshow(data, cmap=my_cmap, norm=norm, interpolation='nearest')
            #
            # cbar = plt.colorbar(c, ax=ax, orientation='vertical', pad=0.02)
            # cbar.set_label(file_name + "图例")
            # cbar.ax.tick_params(labelsize=9)

            # plt.imshow(data, extent=[lonmin, lonmax, latmin, latmax], origin='lower', cmap=my_cmap, norm=norm)
            save_path = pngPath + "/image/";
            if not os.path.exists(save_path):  # 如果路径不存在
                os.makedirs(save_path)  # 则创建该目录
            plt.axis('off')
            name = file_name.split('.')[0]
            plt.savefig(save_path + name + '.png', facecolor='white', transparent=True, bbox_inches='tight',
                        pad_inches=0.0)

            print(file_name + " 绘制完成！")
            # plt.show()

            # del cf
            plt.close()
            gc.collect()
    except Exception as e:
        # 记录异常信息
        print(e)


def drawLight(tif_path, file_name, pngPath):
    try:
        with open('Data/quhua/xj.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        # 遍历 FeatureCollection 的 features
        for feature in geojson_data.get("features", []):
            properties = feature.get("properties", {})
            geometry = feature.get("geometry", {})
            adcode = properties.get("adcode")
            name = properties.get("name")
            level = properties.get("level")
            print(f"行政区划: {name}, 编码: {adcode}, 等级: {level}")
            print(f"边界信息: {geometry}")
            with rasterio.open(tif_path) as src:
                # 使用 GeoJSON 边界掩膜裁剪
                out_image, out_transform = mask(src, [geometry], crop=True)

            data = out_image[0]
            # 获取最大值和最小值
            # 使用 np.nanmax 和 np.nanmin 来忽略 NaN 值
            data_max = np.nanmax(data)  # 忽略 NaN 值计算最大值
            data_min = np.nanmin(data)  # 忽略 NaN 值计算最小值
            # 替换 NaN 为一个特定的值，例如 0 或者数据中的最小值
            #data = np.nan_to_num(data, nan=0)
            # x = data['x']
            # 创建一个图形和坐标轴对象
            fig, ax = plt.subplots(figsize=(12, 12))

            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.rcParams['axes.unicode_minus'] = False
            rainbow_cmap = plt.cm.rainbow
            if ('DNI' in file_name):
                parmObj = colorMap.switch_case('direct_radiation')
                clevs = parmObj['clevs']
                cdict = np.asarray(parmObj['cdict']) / 255.0
                my_cmap = colors.ListedColormap(cdict)
                num_intervals = len(cdict) - 1
                # 动态生成均匀的分隔点
                bounds = np.linspace(data_min, data_max, num_intervals + 1)
                # 使用生成的分隔点来创建 BoundaryNorm
                norm = mpl.colors.BoundaryNorm(bounds, my_cmap.N)
            elif ('DIF' in file_name):
                parmObj = colorMap.switch_case('scattered_radiation')
                clevs = parmObj['clevs']
                cdict = np.asarray(parmObj['cdict']) / 255.0
                my_cmap = colors.ListedColormap(cdict)
                num_intervals = len(cdict) - 1
                # 动态生成均匀的分隔点
                bounds = np.linspace(data_min, data_max, num_intervals + 1)
                # 使用生成的分隔点来创建 BoundaryNorm
                norm = mpl.colors.BoundaryNorm(bounds, my_cmap.N)
                # 设置 num_intervals 为 cdict 数组的长度减去 1
            elif ('GHI' in file_name):
                parmObj = colorMap.switch_case('horizontal_radiation')
                clevs = parmObj['clevs']
                cdict = np.asarray(parmObj['cdict']) / 255.0
                my_cmap = colors.ListedColormap(cdict)
                num_intervals = len(cdict) - 1
                # 动态生成均匀的分隔点
                bounds = np.linspace(data_min, data_max, num_intervals + 1)
                # 使用生成的分隔点来创建 BoundaryNorm
                norm = mpl.colors.BoundaryNorm(bounds, my_cmap.N)
            # 绘制地图并裁剪到指定区域
            # 绘制地图
            c = ax.imshow(data, cmap=my_cmap, norm=norm, interpolation='nearest')
            #
            # cbar = plt.colorbar(c, ax=ax, orientation='vertical', pad=0.02)
            # cbar.set_label(file_name + "图例")
            # cbar.ax.tick_params(labelsize=9)

            # plt.imshow(data, extent=[lonmin, lonmax, latmin, latmax], origin='lower', cmap=my_cmap, norm=norm)
            save_path = pngPath + "/image/";
            if not os.path.exists(save_path):  # 如果路径不存在
                os.makedirs(save_path)  # 则创建该目录
            plt.axis('off')
            name = file_name.split('.')[0]
            plt.savefig(save_path + name + '.png', facecolor='white', transparent=True, bbox_inches='tight',
                        pad_inches=0.0)

            print(file_name + " 绘制完成！")
            # plt.show()

            # del cf
            plt.close()
            gc.collect()
    except Exception as e:
        # 记录异常信息
        print(e)


if __name__ == '__main__':
    #file = 'E:\\renyingweix\\CHNWindAtlas\\wind'
    file = 'E:\\renyingweix\\CHNWindAtlas\\light'
    pngPath = 'E:\\renyingweix\\CHNWindAtlas\\lightpng'
   # pngPath = 'E:\\renyingweix\\CHNWindAtlas\\windpng'
    # 获取目录下的文件列表
    file_list = os.listdir(file)
    for file_name in file_list:
        # 拼接文件的完整路径
        file_path = os.path.join(file, file_name)
        drawLight(file_path, file_name, pngPath)
        #drawWind(file_path, file_name, pngPath)
