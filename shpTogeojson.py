# -*- coding: utf-8 -*-

import json
import fiona
import codecs

import geopandas as gpd

input_dir = "E:\\renyingweix\\CHNWindAtlas\\"
shp_file_path = input_dir + 'akesu_wind_jidian.shp'
json_file_path = input_dir + 'use_land_final.geojson'

# with fiona.open(shp_file_path, 'r', encoding='utf-8') as shp:
#     feature_collection = {
#         'type': 'FeatureCollection',
#         'features': [feature for feature in shp]
#     }
#
# with codecs.open(json_file_path, 'w', encoding='utf-8') as f:
#     f.write(json.dumps(feature_collection, ensure_ascii=False))
# 读取 Shapefile 文件
gdf = gpd.read_file(shp_file_path)

# 保存为 GeoJSON 文件
gdf.to_file(json_file_path, driver="GeoJSON", encoding="utf-8")
print("写入完成！")