import gc
import json
import os

import cartopy.crs as ccrs
import matplotlib as mpl
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from cartopy.feature import ShapelyFeature
from matplotlib.colors import ListedColormap, Normalize
from rasterio.mask import mask
from scipy.ndimage import zoom
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry import shape

# 中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 修复保存图像是负号'-'显示为方块的问题


# 新疆地形 土地利用 新疆坡度 同时画3个
# 新疆地形 土地利用 新疆坡度 同时画3个 带边界 最终是矩形加图例
def getXJPngByPolygon(lonmin, lonmax, latmin, latmax, savepath):
    ##  读取行政区划geojson
    # 加载 GeoJSON 文件
    with open('./Data/quhua/650000_countyBorder.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # 遍历 FeatureCollection 的 features
    for feature in geojson_data.get("features", []):
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        # 获取属性信息
        adcode = properties.get("adcode")
        name = properties.get("name")
        level = properties.get("level")

        # 获取边界信息 (坐标点)
        boundaries = geometry.get("coordinates")
        geom = shape(geometry)
        bounds = geom.bounds
        # 打印信息
        print(f"行政区划: {name}, 编码: {adcode}, 等级: {level}")
        print(f"边界信息: {boundaries}")
        prefixCode = str(adcode)[:4]
        newavepath = savepath + "\\" + prefixCode

        # 如果是多边形或单一多边形
        if geometry.get("type") == "Polygon":
            polygon = Polygon(boundaries[0])  # GeoJSON 的外环是第一个元素
        elif geometry.get("type") == "MultiPolygon":
            polygon = MultiPolygon([Polygon(coords[0]) for coords in boundaries])

        # 扩展边界
        expanded_geometry = expand_boundary(geometry, bounds, expansion_ratio=0.1)
        tif_Dem_path = "./Data/新疆高程/xinjiangdem.tif"
        with rasterio.open(tif_Dem_path) as src:
            # 使用 GeoJSON 边界掩膜裁剪
            out_image, out_transform = mask(src, [expanded_geometry], crop=True)
        saveDemPath = newavepath + "\\dem\\"
        mkdirPath(saveDemPath)
        drawDemByPolygon(name, out_image, bounds, out_transform, polygon, saveDemPath)

        tif_Lucc_path = "./Data/土地利用/lucc2020_650000.tif"
        with rasterio.open(tif_Lucc_path) as src:
            # 使用 GeoJSON 边界掩膜裁剪
            out_image, out_transform = mask(src, [expanded_geometry], crop=True)
        saveLuccPath = newavepath + "\\lucc\\"
        mkdirPath(saveLuccPath)
        # drawLucc(name, out_image, saveLuccPath)
        drawLuccByPolygon(name, out_image, bounds, out_transform, polygon, saveLuccPath)

        tif_Slope_Path = "./Data/新疆坡度/xinjiangslope.tif"
        with rasterio.open(tif_Slope_Path) as src:
            # 使用 GeoJSON 边界掩膜裁剪
            out_image, out_transform = mask(src, [expanded_geometry], crop=True)
        saveSlopePath = newavepath + "\\slope\\"
        mkdirPath(saveSlopePath)
       # drawSlope(name, out_image, saveSlopePath)
        drawSlopeByPolygon(name, out_image, bounds, out_transform, polygon, saveSlopePath)








def getXJPng(lonmin, lonmax, latmin, latmax, savepath):
    ##  读取行政区划geojson
    # 加载 GeoJSON 文件
    with open('./Data/quhua/650000_countyBorder.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # 遍历 FeatureCollection 的 features
    for feature in geojson_data.get("features", []):
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        # 获取属性信息
        adcode = properties.get("adcode")
        name = properties.get("name")
        level = properties.get("level")

        # 获取边界信息 (坐标点)
        boundaries = geometry.get("coordinates")

        # 打印信息
        print(f"行政区划: {name}, 编码: {adcode}, 等级: {level}")
        print(f"边界信息: {boundaries}")
        prefixCode = str(adcode)[:4]
        newavepath = savepath + "\\" + prefixCode

        tif_Dem_path = "./Data/新疆高程/xinjiangdem.tif"
        with rasterio.open(tif_Dem_path) as src:
            # 使用 GeoJSON 边界掩膜裁剪
            out_image, out_transform = mask(src, [geometry], crop=True)
        saveDemPath = newavepath + "\\dem\\"
        mkdirPath(saveDemPath)
        drawDem(name, out_image, saveDemPath)

        tif_Lucc_path = "./Data/土地利用/lucc2020_650000.tif"
        with rasterio.open(tif_Lucc_path) as src:
            # 使用 GeoJSON 边界掩膜裁剪
            out_image, out_transform = mask(src, [geometry], crop=True)
        saveLuccPath = newavepath + "\\lucc\\"
        mkdirPath(saveLuccPath)
        drawLucc(name, out_image, saveLuccPath)

        tif_Slope_Path = "./Data/新疆坡度/xinjiangslope.tif"
        with rasterio.open(tif_Slope_Path) as src:
            # 使用 GeoJSON 边界掩膜裁剪
            out_image, out_transform = mask(src, [geometry], crop=True)
        saveSlopePath = newavepath + "\\slope\\"
        mkdirPath(saveSlopePath)
        drawSlope(name, out_image, saveSlopePath)


class CustomNormalize(Normalize):
    def __call__(self, value, clip=None):
        # 将小于 -200 的值映射为 0（透明）
        # 其他值按比例映射到 1 到 256 之间
        normalized = np.ma.masked_where(value < -200, value)
        return super().__call__(normalized, clip)


def expand_boundary(geometry, bounds, expansion_ratio=0.1):
    # 获取原始边界框
    lonmin, latmin, lonmax, latmax = bounds

    # 根据扩展比例计算新的边界
    lon_range = lonmax - lonmin
    lat_range = latmax - latmin
    lonmin_expanded = lonmin - lon_range * expansion_ratio
    lonmax_expanded = lonmax + lon_range * expansion_ratio
    latmin_expanded = latmin - lat_range * expansion_ratio
    latmax_expanded = latmax + lat_range * expansion_ratio

    # 创建扩展后的多边形
    expanded_geometry = Polygon([(lonmin_expanded, latmin_expanded),
                                 (lonmax_expanded, latmin_expanded),
                                 (lonmax_expanded, latmax_expanded),
                                 (lonmin_expanded, latmax_expanded)])
    return expanded_geometry


def switch_case(value):
    switcher = {
        "lucc": {
            "name": "土地利用",
            "clevs": [-999, 11, 12, 21, 22, 23, 24, 31, 32, 33, 41, 42, 43, 44, 45, 46, 51, 52, 53, 61, 62, 63, 64, 65,
                      66, 67],
            "cdict": [
                "#00000000",  # 无效值 (透明)
                '#f9fbcb',  # 水田
                '#fad80d',  # 旱地
                '#268628',  # 林地
                '#a3c840',  # 灌木林
                '#a8dd82',  # 蔬林地
                '#82dc97',  # 其他林地
                '#969021',  # 高覆盖度草地
                '#b8b772',  # 中覆盖度草地
                '#dcb789',  # 低覆盖度草地
                '#0704f1',  # 河流 (重复三次)
                '#0704f1',
                '#0704f1',
                '#e3e4f7',  # 冰川
                '#3b57b9',  # 海涂
                '#2072eb',  # 滩地
                '#f2634a',  # 城镇
                '#ec9310',  # 农村居民点
                '#e88286',  # 工矿建设用地
                '#b29abe',  # 沙地
                '#847cb7',  # 戈壁
                '#9a31c3',  # 盐碱地
                '#9671d6',  # 沼泽
                '#b956d1',  # 裸土
                '#b558cf',  # 裸岩
                '#f9c1cc',  # 其他未利用地
            ],
            "labels": [
                "无效值", "水田", "旱地", "林地", "灌木林", "蔬林地", "其他林地",
                "高覆盖度草地", "中覆盖度草地", "低覆盖度草地", "河流", "湖泊",
                "水塘", "冰川", "海涂", "滩地", "城镇", "农村居民点",
                "工矿建设用地", "沙地", "戈壁", "盐碱地", "沼泽", "裸土", "裸岩", "其他未利用地"
            ]
        }, "slope": {
            "name": "坡度",
            "clevs": [-170, 1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 53, 70, 106, 140, 212, 265, 371, 530, 742, 1060, 1484,
                      1855, 3710, 7420],
            "cdict": [
                "#00000000",
                "#FEFFBE", "#E6F6BB", "#D2EFB9", "#BDE7B6", "#A3DDB3", "#8ED6B0",
                "#71CBA4", "#69C0A3", "#64B9A3", "#60B4A2", "#57A9A2", "#509EA1",
                "#4793A0", "#458299", "#447191", "#42618A", "#415886", "#415083",
                "#3F3E7B", "#39356A", "#342D5A", "#2F254B", "#2C2142", "#291C3A",
                "#261831", "#231328"
            ]
        },
    }
    return switcher.get(value, 'wrong value')


# -*- 新疆地形
#         lonmin = 73.5023549999999943
#         lonmax = 135.0956700000000126
#         latmin = 3.3971618700000001
#         latmax = 53.5632689999999982 -*-

def drawDem(tifname, data, savePath):
    tifname = tifname + "dem"
    data = data[0]
    scale_factor = 2  # 放大倍数
    data_resampled = zoom(data, scale_factor, order=3)  # 放大数据

    # x = data['x']
    rainbow_cmap = plt.cm.rainbow
    colors = rainbow_cmap(np.linspace(0, 1, 256))
    colors[0] = [0, 0, 0, 0]
    my_cmap = ListedColormap(colors)
    norm = CustomNormalize(vmin=-200, vmax=np.max(data))
    # 4. 可视化并保存为 PNG
    plt.figure(figsize=(12, 12))
    plt.imshow(data_resampled, cmap=my_cmap, norm=norm, interpolation='nearest')
    plt.axis('off')

    # 保存为透明背景 PNG 文件
    plt.savefig(
        f"{savePath}{tifname}.png",
        dpi=500,
        facecolor='none',
        transparent=True,
        bbox_inches='tight',
        pad_inches=0.0,
    )
    print(tifname + " 绘制完成！")
    # plt.show()

    plt.close()
    gc.collect()


def drawDemByPolygon(tifname, data, bounds, transform, polygon, savePath):
    tifname = tifname + "dem"
    data = data[0]
    latmax = bounds[3]
    latmin = bounds[1]
    lonmax = bounds[2]
    lonmin = bounds[0]
    # x = data['x']
    rainbow_cmap = plt.cm.rainbow
    colors = rainbow_cmap(np.linspace(0, 1, 256))
    colors[0] = [0, 0, 0, 0]
    my_cmap = ListedColormap(colors)
    norm = CustomNormalize(vmin=-200, vmax=np.max(data))
    # 4. 可视化并保存为 PNG
    # 绘图
    # 创建一个新的图形
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

    # 绘制裁切后的数据
    c = ax.imshow(data, extent=[transform[2], transform[2] + transform[0] * data.shape[1],
                                transform[5] + transform[4] * data.shape[0], transform[5]], cmap=my_cmap, norm=norm)
    # 绘制原始的边界（蓝色）
    if polygon:
        # 转换 shapely 的 MultiPolygon 到 cartopy 的 feature
        feature = ShapelyFeature(polygon, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=1)
        ax.add_feature(feature)
    # 添加图例（colorbar）
    cbar = plt.colorbar(c, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label("高程图例")
    cbar.ax.tick_params(labelsize=8)  # 可调节刻度字体大小

    plt.axis('off')

    # 保存为透明背景 PNG 文件
    plt.savefig(
        f"{savePath}{tifname}.png",
        dpi=500,
        facecolor='white',
        bbox_inches='tight',
        pad_inches=0.0,
    )
    print(tifname + " 绘制完成！")
    # plt.show()

    plt.close()
    gc.collect()


def drawLuccByPolygon(tifname, data, bounds, transform, polygon, savePath):
    tifname = tifname + "lucc"
    data = data[0]
    # x = data['x']
    rainbow_cmap = plt.cm.rainbow
    parmObj = switch_case('lucc')
    clevs = parmObj['clevs']
    cdict = parmObj['cdict']
    labels = parmObj['labels']
    # 计算每个颜色区间的中间值
    mid_points = [(clevs[i] + clevs[i + 1]) / 2 for i in range(len(clevs) - 1)]
    # cdict = np.asarray(parmObj['cdict']) / 255.0
    my_cmap = colors.ListedColormap(cdict)
    norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
    # 4. 可视化并保存为 PNG
    # 绘图
    # 创建一个新的图形
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

    # 绘制裁切后的数据
    c = ax.imshow(data, extent=[transform[2], transform[2] + transform[0] * data.shape[1],
                                transform[5] + transform[4] * data.shape[0], transform[5]], cmap=my_cmap, norm=norm)
    # 绘制原始的边界（蓝色）
    if polygon:
        # 转换 shapely 的 MultiPolygon 到 cartopy 的 feature
        feature = ShapelyFeature(polygon, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=1)
        ax.add_feature(feature)
    # 添加图例（colorbar）
    # 只保留需要的刻度位置
    cbar = plt.colorbar(c, ticks=mid_points)  # 使用中间值作为刻度

    cbar.ax.set_yticklabels(labels[1:])  # 设置标签

    cbar.set_label("土地利用图例")
    cbar.ax.tick_params(labelsize=7)  # 可调节刻度字体大小

    plt.axis('off')

    # 保存为透明背景 PNG 文件
    plt.savefig(
        f"{savePath}{tifname}.png",
        dpi=500,
        facecolor='white',
        bbox_inches='tight',
        pad_inches=0.0,
    )
    print(tifname + " 绘制完成！")
    # plt.show()

    plt.close()
    gc.collect()


def drawSlopeByPolygon(tifname, data, bounds, transform, polygon, savePath):
    tifname = tifname + "slope"
    data = data[0]
    # x = data['x']

    parmObj = switch_case('slope')
    clevs = parmObj['clevs']
    cdict = parmObj['cdict']
    my_cmap = colors.ListedColormap(cdict)
    norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
    # 4. 可视化并保存为 PNG
    # 绘图
    # 创建一个新的图形
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})

    # 绘制裁切后的数据
    c = ax.imshow(data, extent=[transform[2], transform[2] + transform[0] * data.shape[1],
                                transform[5] + transform[4] * data.shape[0], transform[5]], cmap=my_cmap, norm=norm)
    # 绘制原始的边界（蓝色）
    if polygon:
        # 转换 shapely 的 MultiPolygon 到 cartopy 的 feature
        feature = ShapelyFeature(polygon, ccrs.PlateCarree(), edgecolor='black', facecolor='none', linewidth=1)
        ax.add_feature(feature)
    # 添加图例（colorbar）
    cbar = plt.colorbar(c, ax=ax, orientation='vertical', pad=0.02)
    cbar.set_label("坡度图例")
    cbar.ax.tick_params(labelsize=8)  # 可调节刻度字体大小

    plt.axis('off')

    # 保存为透明背景 PNG 文件
    plt.savefig(
        f"{savePath}{tifname}.png",
        dpi=500,
        facecolor='white',
        bbox_inches='tight',
        pad_inches=0.0,
    )
    print(tifname + " 绘制完成！")
    # plt.show()

    plt.close()
    gc.collect()


# -*- 土地利用 -*-
def drawLucc(tifname, data, savePath):
    try:
        tifname = tifname + "lucc"
        data = data[0]
        scale_factor = 2  # 放大倍数
        data_resampled = zoom(data, scale_factor, order=3)  # 放大数据

        proj = ccrs.PlateCarree()
        # proj = ccrs.Miller()
        # proj = ccrs.Mercator()
        # proj = ccrs.LambertConformal()

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(figsize=(16, 9.6), facecolor='#666666', edgecolor='Blue', frameon=False)
        ax = fig.add_subplot(111, projection=proj)
        parmObj = switch_case('lucc')
        clevs = parmObj['clevs']
        cdict = parmObj['cdict']
        # cdict = np.asarray(parmObj['cdict']) / 255.0
        my_cmap = colors.ListedColormap(cdict)
        norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
        print(clevs[0:])

        plt.imshow(data, cmap=my_cmap, norm=norm,
                   interpolation='nearest')  # interpolation='nearest'

        plt.axis('off')

        plt.savefig(f"{savePath}{tifname}.png", dpi=500, facecolor='none', transparent=True, bbox_inches='tight',
                    pad_inches=0.0)
        print(tifname + " 绘制完成！")
        # plt.show()
        # del cf
        plt.close()
        gc.collect()
    except:
        return {
            "code": 202,
            "msg": Exception
        }
    else:
        return {
            "code": 200,
            "msg": tifname + " 绘制完成！"
        }


# -*- 新疆坡度 -*-
def drawSlope(tifname, data, savePath):
    try:
        tifname = tifname + "slope"
        data = data[0]
        scale_factor = 2  # 放大倍数
        data_resampled = zoom(data, scale_factor, order=3)  # 放大数据

        proj = ccrs.PlateCarree()

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(figsize=(16, 9.6), facecolor='#666666', edgecolor='Blue', frameon=False)
        ax = fig.add_subplot(111, projection=proj)

        parmObj = switch_case('slope')
        clevs = parmObj['clevs']
        cdict = parmObj['cdict']
        my_cmap = colors.ListedColormap(cdict)
        norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
        print(clevs[0:])
        plt.imshow(data, cmap=my_cmap, norm=norm, interpolation='nearest')

        plt.axis('off')
        plt.savefig(f"{savePath}{tifname}.png", dpi=500, facecolor='none', transparent=True, bbox_inches='tight',
                    pad_inches=0.0)
        print(tifname + " 绘制完成！")

        # del cf
        plt.close()
        gc.collect()
    except:
        return {
            "code": 202,
            "msg": Exception
        }
    else:
        return {
            "code": 200,
            "msg": tifname + " 绘制完成！"
        }


def mkdirPath(savePath):
    if not os.path.exists(savePath):  # 如果路径不存在
        os.makedirs(savePath)  # 则创建该目录


if __name__ == '__main__':
    savepath = "D:\\shadowData\\xj\\tifPngPolygon"
    getXJPngByPolygon(1, 1, 1, 1, savepath)
