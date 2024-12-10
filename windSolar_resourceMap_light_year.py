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

from XinJiangData import windSolar_resourceMap_wind_year

# from mpl_toolkits.basemap import Basemap

plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 修复保存图像是负号'-'显示为方块的问题


def switch_case(value):
    switcher = {
        "horizontal_radiation": {
            "name": "水平辐射",
            # "clevs": [60, 180, 360, 540, 720, 870, 980, 1100],
            "clevs": [170, 190, 210, 230, 250, 270, 290, 320, 340],
            "cdict": [
                [55, 72, 164], [76, 101, 185], [107, 206, 235], [154, 217, 162], [204, 230, 81],
                [239, 219, 27], [245, 115, 23], [237, 30, 36],
            ],
            "unit": "W/m2"
        },
        "direct_radiation": {
            "name": "直接辐射",
            # "clevs": [60, 180, 360, 540, 720, 870, 980, 1100],
            "clevs": [150, 170, 190, 210, 230, 250, 270, 290, 320],
            "cdict": [
                [55, 72, 164], [76, 101, 185], [107, 206, 235], [154, 217, 162], [204, 230, 81],
                [239, 219, 27], [245, 115, 23], [237, 30, 36],
            ],
            "unit": "W/m2"
        },
        "scattered_radiation": {
            "name": "散射辐射",
            # "clevs": [60, 180, 360, 540, 720, 870, 980, 1100],
            "clevs": [10, 16, 22, 28, 34, 40, 46, 52, 60],
            "cdict": [
                [55, 72, 164], [76, 101, 185], [107, 206, 235], [154, 217, 162], [204, 230, 81],
                [239, 219, 27], [245, 115, 23], [237, 30, 36],
            ],
            "unit": "W/m2"
        },
    }
    return switcher.get(value, 'wrong value')


variableArray = [
    "scattered_radiation", "direct_radiation", "horizontal_radiation",
]


def processLight(filePath, file_name):
    data = nc.Dataset(filePath, 'r')
    # 去掉后缀 .nc
    file_name_no_ext = file_name.rstrip('.nc')
    # 如果还需要处理其他部分，比如获取日期
    date = file_name_no_ext.split('_')[2]

    for variable_name in variableArray:
        variable_data = data.variables[variable_name][:]

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
        pngPath = 'D:\\shadowData\\xj\\ncPng\\light\\' + date + '\\'

        if not os.path.exists(pngPath):  # 如果路径不存在
            os.makedirs(pngPath)  # 则创建该目录
        else:
            print("路径已经存在")
        plt.savefig(pngPath + variable_name + '.png', dpi=600, bbox_inches='tight', transparent=True, pad_inches=0)


def processLightByBounds(path, file_name, polygon, bounds, savePath, name):
    for variable_name in variableArray:
        data = nc.Dataset(path, 'r')
        # 去掉后缀 .nc
        file_name_no_ext = file_name.rstrip('.nc')
        # 如果还需要处理其他部分，比如获取日期
        date = file_name_no_ext.split('_')[2]
        variable_data = data.variables[variable_name][:]

        # 获取数据相关信息
        lat = data.variables['lat'][:]
        lon = data.variables['lon'][:]
        latmax = bounds[3]
        latmin = bounds[1]
        lonmax = bounds[2]
        lonmin = bounds[0]
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

        masked_data, latmax, latmin, lonmax, lonmin, lon_cropped, lat_cropped = windSolar_resourceMap_wind_year.makeYM(
            lat, lon, variable_data,
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


def processLightByPolygon(path, file_name, polygon, bounds, savePath, name):
    for variable_name in variableArray:
        data = nc.Dataset(path, 'r')
        # 去掉后缀 .nc
        file_name_no_ext = file_name.rstrip('.nc')
        # 如果还需要处理其他部分，比如获取日期
        date = file_name_no_ext.split('_')[2]
        variable_data = data.variables[variable_name][:]

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
        cb = plt.colorbar(c, ax=ax, orientation='vertical', pad=0.02, shrink=0.8)  # 调整 pad 和 shrink 以适配图例位置
        if (unit != ""):
            cb.set_label(variable_name + "单位: " + unit)  # 图例标题，例如温度、降水量等
        else:
            cb.set_label(variable_name)  # 图例标题，例如温度、降水量等
        cb.ax.tick_params(labelsize=8)  # 可调节刻度字体大小
        plt.axis('off')

        plt.savefig(pngPath + name + '-' + variable_name + '.png', dpi=600, bbox_inches='tight', facecolor='white',
                    pad_inches=0)
        plt.close()


if __name__ == '__main__':
    path = 'F:\\xjData\\XNYPoint\\yearAvg\\light\\yearly\\'
    file_list = os.listdir(path)
    # 遍历每个文件
    for file_name in file_list:
        ffile_type = os.path.splitext(file_name)[1].lstrip('.')
        type = file_name.split('.')[1]
        if ffile_type == 'nc':
            # 拼接文件的完整路径
            file_path = os.path.join(path, file_name)
            processLight(file_path, file_name)
        else:
            continue
