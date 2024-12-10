# -*- encoding: utf-8 -*-
# -*- 新疆地形 -*-

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, Normalize
import numpy as np
import rioxarray as rxr
import gc


class CustomNormalize(Normalize):
    def __call__(self, value, clip=None):
        # 将小于 -200 的值映射为 0（透明）
        # 其他值按比例映射到 1 到 256 之间
        normalized = np.ma.masked_where(value < -200, value)
        return super().__call__(normalized, clip)


def draw(tif_path):
    try:
        tifname = "650000_dem"
        ds = rxr.open_rasterio(tif_path)

        data = ds[0]
        # x = data['x']

        lonmin = 73.5023549999999943
        lonmax = 135.0956700000000126
        latmin = 3.3971618700000001
        latmax = 53.5632689999999982


        rainbow_cmap = plt.cm.rainbow
        colors = rainbow_cmap(np.linspace(0, 1, 256))
        colors[0] = [0, 0, 0, 0]
        my_cmap = ListedColormap(colors)
        norm = CustomNormalize(vmin=-200, vmax=np.max(data))

        plt.imshow(data, extent=[lonmin, lonmax, latmin, latmax], cmap=my_cmap, norm=norm, interpolation='nearest')

        plt.axis('off')
        plt.savefig("./image/" + tifname + '.png', facecolor='none', transparent=True, bbox_inches='tight', pad_inches=0.0)
        print(tifname + " 绘制完成！")
        # plt.show()

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

tif_path = "./Data/新疆高程/xinjiangdem.tif"
draw(tif_path)


