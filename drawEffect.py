import os

import geopandas as gpd
import matplotlib.pyplot as plt

# 1. 读取 SHP 文件和 GeoJSON 文件
#shp_path = 'F:\\xjData\\限制性因素data(1)\\限制性因素data\\道路\\xj_road.shp'  # 替换为你的 SHP 文件路径
#shp_path = 'F:\\xjData\\限制性因素data(1)\\限制性因素data\\自然保护\\ziran.shp'  # 替换为你的 SHP 文件路径
#shp_path = 'F:\\xjData\\限制性因素data\\水系\\shui_huanchong_10m.shp'  # 替换为你的 SHP 文件路径
#shp_path = 'F:\\xjData\\限制性因素data\\湖泊河流\\全国水系_xj.shp'  # 替换为你的 SHP 文件路径
#shp_path = 'F:\\xjData\\限制性因素data\\生态红线\\red_650000.shp'  # 替换为你的 SHP 文件路径
shp_path = 'F:\\xjData\\限制性因素data\\已建风电场\\wind_landt_area.shp'  # 替换为你的 SHP 文件路径
geojson_path = './Data/quhua/650000_countyBorder.geojson'  # 替换为你的 GeoJSON 文件路径

# 2. 加载 SHP 和 GeoJSON 数据
shp_gdf = gpd.read_file(shp_path)
geojson_gdf = gpd.read_file(geojson_path)

# 3. 确保坐标系一致
shp_gdf = shp_gdf.to_crs(geojson_gdf.crs)

# 4. 创建输出文件夹
#output_folder = 'F:\\xjData\\xianzhix\\road'
#output_folder = 'F:\\xjData\\xianzhix\\ziranbaohuqu'
#output_folder = 'F:\\xjData\\xianzhix\\shuixi'
output_folder = 'F:\\xjData\\xianzhix\\fengdianchang'
os.makedirs(output_folder, exist_ok=True)

# 5. 循环遍历 GeoJSON 中的每个区县
for index, row in geojson_gdf.iterrows():
    # 1. 获取当前区县的名称（假设名称存储在 "name" 列中，可能需要根据实际列名调整）
    county_name = row['name']  # 假设区县名称在 'name' 列中
    print(f"正在裁剪: {county_name}...")
    admin_code = row['adcode']  # 假设行政区划代码在 'code' 列中

    # 2. 提取前 4 位行政区划代码
    sub_folder_name = str(admin_code)[:4]  # 例如 1101、1201 等

    # 3. 生成当前区县的子文件夹路径
    sub_folder_path = os.path.join(output_folder, sub_folder_name)
    os.makedirs(sub_folder_path, exist_ok=True)  # 创建子文件夹

    # 2. 提取当前区县的边界作为 GeoDataFrame
    county_boundary = gpd.GeoDataFrame([row], crs=geojson_gdf.crs)

    # 3. 使用 clip 函数裁剪 SHP 文件
    clipped_gdf = gpd.clip(shp_gdf, county_boundary)

    # 4. 跳过空的裁剪结果（如果某些区县没有 SHP 数据）
    if clipped_gdf.empty:
        print(f"{county_name} 没有裁剪到有效的 SHP 数据，跳过。")
        continue

    # 5. 可视化裁剪结果
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
   # clipped_gdf.plot(ax=ax, color='blue', edgecolor='#f4c500')
    clipped_gdf.plot(ax=ax, color='#00D4E5', edgecolor='black')
    # 绘制区县的边界线，颜色为黄色，线宽为 2
    county_boundary.boundary.plot(ax=ax, edgecolor='black', linewidth=2)
    plt.axis('off')

    # 8. 生成文件路径，确保文件名没有非法字符
    safe_county_name = ''.join(c for c in county_name if c.isalnum() or c in [' ', '_', '-'])
    output_path = os.path.join(sub_folder_path, f'{safe_county_name}.png')
    # 7. 保存图片
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)  # 关闭当前图，释放内存

    print(f" {county_name} 的裁剪图片已保存为 {output_path}")
