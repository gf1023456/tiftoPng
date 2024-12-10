import json
import os

import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry import shape
from concurrent.futures import ThreadPoolExecutor
from XinJiangData import windSolar_resourceMap_wind_year
from XinJiangData import windSolar_resourceMap_light_year


def processArea():
    with open('./Data/quhua/650000_countyBorder.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
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
            prefixCode = str(adcode)[:4]

            # 如果是多边形或单一多边形
            if geometry.get("type") == "Polygon":
                polygon = Polygon(boundaries[0])  # GeoJSON 的外环是第一个元素
            elif geometry.get("type") == "MultiPolygon":
                polygon = MultiPolygon([Polygon(coords[0]) for coords in boundaries])
            processLind(polygon,bounds,name,prefixCode)
            processWind(polygon,bounds,name,prefixCode)


            print("完成了" + name + "处理")

def processLind(polygon,bounds,name,prefixCode):
    savePath = 'D:\\shadowData\\xj\\ncPng\\light2022\\'
    # 遍历 FeatureCollection 的 features
    newavepath = savePath + "\\" + prefixCode + "\\"
    # 调取光数据处理
    path = 'F:\\xjData\\XNYPoint\\yearAvg\\light\\2022'
    file_list = os.listdir(path)
    # 遍历每个文件
    for file_name in file_list:
        ffile_type = os.path.splitext(file_name)[1].lstrip('.')
        type = file_name.split('.')[1]
        if ffile_type == 'nc':
            # 拼接文件的完整路径
            file_path = os.path.join(path, file_name)
            windSolar_resourceMap_light_year.processLightByPolygon(file_path, file_name, polygon, bounds, newavepath, name)




def processWind(polygon,bounds,name,prefixCode):
    savePath = 'D:\\shadowData\\xj\\ncPng\\wind2022\\'
    # 遍历 FeatureCollection 的 features
    newavepath = savePath + "\\" + prefixCode + "\\"
    # 调取风光数据处理
    path = 'F:\\xjData\\XNYPoint\\yearAvg\\wind\\2022'
    file_list = os.listdir(path)
    # 遍历每个文件
    for file_name in file_list:
        ffile_type = os.path.splitext(file_name)[1].lstrip('.')
        type = file_name.split('.')[1]
        if ffile_type == 'nc':
            # 拼接文件的完整路径
            file_path = os.path.join(path, file_name)
            windSolar_resourceMap_wind_year.processWindByPolygon(file_path, file_name, polygon, bounds, newavepath, name)

    print("完成了" + name + "处理")


if __name__ == '__main__':
    processArea()