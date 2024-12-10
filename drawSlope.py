# -*- encoding: utf-8 -*-
# -*- 新疆坡度 -*-

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
import cartopy.crs as ccrs
import rioxarray as rxr
import gc


def switch_case(value):
    switcher = {
        "slope": {
            "name": "坡度",
            "clevs": [-170, 1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 53, 70, 106, 140, 212, 265, 371, 530, 742, 1060, 1484, 1855, 3710, 7420],
            "cdict": [
                "#00000000",
                "#FEFFBE","#E6F6BB","#D2EFB9","#BDE7B6","#A3DDB3","#8ED6B0",
                "#71CBA4","#69C0A3","#64B9A3","#60B4A2","#57A9A2","#509EA1",
                "#4793A0","#458299","#447191","#42618A","#415886","#415083",
                "#3F3E7B","#39356A","#342D5A","#2F254B","#2C2142","#291C3A",
                "#261831","#231328"
            ]
        },
    }
    return switcher.get(value, 'wrong value')


def cm2inch(value):
    return value/2.54

def px_to_size(px, mydpi):
    return px / mydpi


def draw(tif_path):
    try:
        tifname = "650000_slope"
        ds = rxr.open_rasterio(tif_path)

        data = ds[0]
        # x = data['x']

        lonmin = 73.5023549999999943
        lonmax = 135.0956700000000126
        latmin = 3.3971618700000001
        latmax = 53.5632689999999982

        proj = ccrs.PlateCarree()

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(figsize=(16, 9.6), facecolor='#666666', edgecolor='Blue', frameon=False)
        ax = fig.add_subplot(111, projection=proj)
        ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

        parmObj = switch_case('slope')
        clevs = parmObj['clevs']
        cdict = parmObj['cdict']
        my_cmap = colors.ListedColormap(cdict)
        norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
        print(clevs[0:])
        plt.imshow(data, extent=[lonmin, lonmax, latmin, latmax], cmap=my_cmap, norm=norm, interpolation='nearest')

        plt.axis('off')
        plt.savefig("./image/" + tifname + '.png', facecolor='none', transparent=True, bbox_inches='tight', pad_inches=0.0)
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

tif_path = "./Data/新疆坡度/xinjiangslope.tif"
draw(tif_path)


