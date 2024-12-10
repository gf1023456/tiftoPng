# -*- coding: utf-8 -*-
# -*- 风光资源图谱 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.colors import LinearSegmentedColormap
import netCDF4 as nc
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
import math
# from mpl_toolkits.basemap import Basemap


def switch_case(value):
    switcher = {
        "mean_wind_speed": {
            "name": "平均风速",
            "clevs": [0.0, 2.0, 2.5, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10, 100],
            "cdict": [
                [225,224,225], [192,254,231], [189,232,255], [188,211,253], [160,196,255],
                [119,176,251], [2,119,254], [161,254,116], [118,254,5], [255,255,0], [252,220,0],
                [253,170,0], [255,142,1], [255,128,124], [254,91,128], [253,0,0], [228,1,1], [168,0,0]
            ]
        },
        "mean_wind_direction": {
            "name": "风向",
            "clevs": [30.0, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360],
            "cdict": [
                [0,60,248], [1,96,218], [2,185,186], [0,139,97], [0,187,109],
                [120,217,0], [254,247,72], [255,189,85], [254,143,89],
                [251,57,47], [199,0,165], [153,0,192]
            ]
        },
        "wind_weighted_avg": {
            "name": "平均风功率密度",
            "clevs": [100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650],
            "cdict": [
                [50,171,3],[85,184,1],[116,196,5],[148,215,8],[189,231,7],
                [225,238,28],[254,235,11],[251,186,2],[243,142,9],[247,97,8],
                [247,48,8],[245,7,6]
            ]
        },
        "weibull_k": {
            "name": "Weibull分布参数K值",
            "clevs": [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
            "cdict": [
                [197,167,214],[94,21,132],[34,0,169],[0,3,212],[0,103,88],[47,187,4],
                [183,234,0],[255,228,0],[255,178,0],[255,86,0],[255,0,0]
            ]
        },
        "weibull_c": {
            "name": "Weibull分布参数C值",
            "clevs": [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
            "cdict": [
                [197, 167, 214], [94, 21, 132], [34, 0, 169], [0, 3, 212], [0, 103, 88], [47, 187, 4],
                [183, 234, 0], [255, 228, 0], [255, 178, 0], [255, 86, 0], [255, 0, 0]
            ]
        },
        "air_density": {
            "name": "空气密度",
            "clevs": [0.9,0.95,1,1.05,1.1,1.15,1.2,1.25,1.3,1.35,1.4,1.45,1.5,1.55,1.6,1.65],
            "cdict": [
                [16,40,104],[19,86,129],[26,121,139],[30,154,135],[25,170,115],[14,195,66],
                [1,218,5],[79,224,3],[164,240,7],[250,251,5],[242,214,6],[238,187,13],
                [236,160,20],[221,125,34],[203,100,46],[190,87,58]
            ]
        },
        "relative_humidity": {
            "name": "相对湿度",
            "clevs": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            "cdict": [
                [151,232,173],[153,210,202],[155,188,232],[107,157,225],[59,126,219],
                [43,92,194],[28,59,169],[17,44,144],[7,30,120],[0,15,80],
            ]
        },
        "horizontal_radiation": {
            "name": "水平辐射",
            "clevs": [60, 180, 360, 540, 720, 870, 980, 1100],
            "cdict": [
                [55,72,164],[76,101,185],[107,206,235],[154,217,162],[204,230,81],
                [239,219,27],[245,115,23],[237,30,36],
            ]
        },
        "direct_radiation": {
            "name": "直接辐射",
            "clevs": [60, 180, 360, 540, 720, 870, 980, 1100],
            "cdict": [
                [55, 72, 164], [76, 101, 185], [107, 206, 235], [154, 217, 162], [204, 230, 81],
                [239, 219, 27], [245, 115, 23], [237, 30, 36],
            ]
        },
        "scattered_radiation": {
            "name": "散射辐射",
            "clevs": [60, 180, 360, 540, 720, 870, 980, 1100],
            "cdict": [
                [55, 72, 164], [76, 101, 185], [107, 206, 235], [154, 217, 162], [204, 230, 81],
                [239, 219, 27], [245, 115, 23], [237, 30, 36],
            ]
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

data = nc.Dataset(r'D:\Code\result_post_interpolation.nc', 'r')
# data = nc.Dataset(r'D:\shadowData\xj\nc\result_post_interpolation.nc', 'r')
# shp_path = 'E:\区域shp\中华人民共和国 (1)中华人民共和国\中华人民共和国 (1).shp'

variableArray = [
    "mean_wind_speed","mean_wind_direction","wind_weighted_avg",
    "weibull_k","weibull_c","air_density","relative_humidity",
    "horizontal_radiation","direct_radiation","scattered_radiation",
]
for variable_name in variableArray:
    variable_data = data.variables[variable_name][:]

    if(variable_name == 'wind_rose'):
        variable_name = 'mean_wind_direction'
        mean_wind_direction = data.variables[variable_name][:]
        variable_name = 'mean_wind_speed'
        mean_wind_speed = data.variables[variable_name][:]
        # 这里使用风向和风速的均值作为示例
        average_wind_direction = np.mean(mean_wind_direction, axis=0)  # 沿纬度方向取平均
        average_wind_speed = np.mean(mean_wind_speed, axis=0)  # 沿纬度方向取平均
        # 创建极坐标图
        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

        # 将风向转换为弧度
        theta = np.radians(average_wind_direction)

        # 绘制玫瑰图，使用柱状图
        bars = ax.bar(theta, average_wind_speed, width=np.pi / 10, bottom=0.0,
                  color=plt.cm.viridis(average_wind_speed / max(average_wind_speed)))

        # 设置极坐标图的标签
        ax.set_theta_direction(-1)  # 顺时针方向
        ax.set_theta_offset(np.pi / 2)  # 0度朝北

        # 设置图的标题
        plt.title('Wind Rose', fontsize=15)

        # # 添加颜色条
        # cbar = plt.colorbar(b, ax=ax)
        # cbar.set_label('Air Density')
        # plt.axis('off')
        # plt.savefig('D:\\shadowData\\xj\\' + variable_name + '.png', bbox_inches='tight', transparent=True, pad_inches=0)
        plt.show()
    else:
        # 获取数据相关信息
        lat = data.variables['lat'][:]
        lon =  data.variables['lon'][:]
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
        plt.savefig('./image/'+variable_name+'.png',bbox_inches='tight',transparent=True, pad_inches=0)
        # 显示图像
        plt.show()
