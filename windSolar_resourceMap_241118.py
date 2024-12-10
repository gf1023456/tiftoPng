# -*- coding: utf-8 -*-
# -*- 风光资源图谱-新数据 -*-

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
from XinJiangData.colorMap import switch_case
# from mpl_toolkits.basemap import Basemap


# 要素
# 'lat' 'lon' 'weibull_k' 'weibull_c' 'mean_wind_speed'
# 'air_density' 'wind_weighted_avg' 'relative_humidity'
# 'mean_wind_direction' 'wind_rose' 'prevailing_wind_direction'
# 'horizontal_radiation' 'direct_radiation' 'scattered_radiation'

# data = nc.Dataset(r'D:\Code\testData\result_post_interpolation.nc', 'r')
data = nc.Dataset(r'D:\Code\testData\solar_5km_2022.nc', 'r')     #辐射
# data = nc.Dataset(r'D:\Code\testData\xj_3km_80-120_2022.nc', 'r')   #风

variableArray_wind = [
    "mean_wind_speed_120",
    "mean_wind_direction_120", "wind_weighted_avg_120",
    "weibull_k_120","weibull_c_120","air_density_120","relative_humidity_120",
]
variableArray_radiation = [
    "horizontal_radiation",
    "direct_radiation",
    "scattered_radiation",
]
for variable_name in variableArray_radiation:
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
