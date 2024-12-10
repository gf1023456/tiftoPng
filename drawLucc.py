# -*- encoding: utf-8 -*-
# -*- 土地利用 -*-

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib as mpl
import cartopy.crs as ccrs
import rioxarray as rxr
import gc


def switch_case(value):
    switcher = {
        "lucc": {
            "name": "土地利用",
            "clevs": [-999, 11, 12, 21, 22, 23, 24, 31, 32, 33, 41, 42, 43, 44, 45, 46, 51, 52, 53, 61, 62, 63, 64, 65, 66, 67],
            "cdict": [
                "#00000000",
                '#f9fbcb', '#fad80d', '#268628', '#a3c840', '#a8dd82',
                '#82dc97', '#969021', '#b8b772', '#dcb789', '#0704f1',
                '#0704f1', '#0704f1', '#e3e4f7', '#3b57b9', '#2072eb',
                '#f2634a', '#ec9310', '#e88286', '#b29abe', '#847cb7',
                '#9a31c3', '#9671d6', '#b956d1', '#b558cf', '#f9c1cc'
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
        tifname = "lucc2020_650000"
        ds = rxr.open_rasterio(tif_path)

        data = ds[0]
        # x = data['x']

        lonmin = 73.5023549999999943
        lonmax = 135.0956700000000126
        latmin = 3.3971618700000001
        latmax = 53.5632689999999982

        proj = ccrs.PlateCarree()
        # proj = ccrs.Miller()
        # proj = ccrs.Mercator()
        # proj = ccrs.LambertConformal()

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        fig = plt.figure(figsize=(16, 9.6), facecolor='#666666', edgecolor='Blue', frameon=False)
        ax = fig.add_subplot(111, projection=proj)
        ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

        parmObj = switch_case('lucc')
        clevs = parmObj['clevs']
        cdict = parmObj['cdict']
        # cdict = np.asarray(parmObj['cdict']) / 255.0
        my_cmap = colors.ListedColormap(cdict)
        norm = mpl.colors.BoundaryNorm(clevs, my_cmap.N)
        print(clevs[0:])
        # cf = ax.contourf(lon, lat, data, levels=clevs[0:], cmap=my_cmap, norm=norm, transform=ccrs.PlateCarree())
        # cf = plt.contourf(lon, lat, data, clevs, transform=ccrs.PlateCarree(), cmap=my_cmap, norm=norm)

        plt.imshow(data, extent=[lonmin, lonmax, latmin, latmax], cmap=my_cmap, norm=norm, interpolation='nearest')  # interpolation='nearest'
        # plt.imshow(data, extent=[lonmin, lonmax, latmin, latmax], origin='lower', cmap=my_cmap, norm=norm)

        plt.axis('off')
        plt.savefig("./image/" + tifname + '.png', facecolor='none', transparent=True, bbox_inches='tight', pad_inches=0.0)
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

tif_path = "./Data/土地利用/lucc2020_650000.tif"
draw(tif_path)